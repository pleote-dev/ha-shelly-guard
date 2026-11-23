"""Async Home Assistant manager for Shelly Guard."""

from __future__ import annotations

import asyncio
import datetime
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send

from . import core
from .const import (
    CONF_AUTO_RESTORE,
    CONF_BACKUP_DIR,
    CONF_HARDEN,
    CONF_KEEP_VERSIONS,
    CONF_NETALERTX_TOKEN,
    CONF_NETALERTX_URL,
    CONF_NOTIFY_SERVICE,
    CONF_NOTIFY_THREAD_ID,
    CONF_SCAN_DEVICES,
    CONF_SCAN_EVERY_MIN,
    CONF_SHELLY_PASSWORD,
    CONF_SHELLY_USER,
    CONF_WIFI_PASSWORD,
    CONF_WIFI_SECRETS_FILE,
    DEFAULT_AUTO_RESTORE,
    DEFAULT_BACKUP_DIR,
    DEFAULT_HARDEN,
    DEFAULT_KEEP_VERSIONS,
    DEFAULT_SCAN_DEVICES,
    DEFAULT_SCAN_EVERY_MIN,
    DEFAULT_SHELLY_USER,
    DEFAULT_WIFI_SECRETS_FILE,
    SIGNAL_UPDATE,
)

_LOGGER = logging.getLogger(__name__)


class ShellyGuardManager:
    """Coordinates Shelly Guard checks, backups, hardening, Range Extender discovery and state."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._lock = asyncio.Lock()
        self.backup_dir: str = DEFAULT_BACKUP_DIR
        self.suspect: dict[str, int] = {}
        self.offline_runs: dict[str, int] = {}
        self.notified: dict[str, str] = {}
        self.last_scan_ts: float = 0.0
        self.device_table: dict[str, dict[str, Any]] = {}
        self.status: dict[str, Any] = {
            "devices": 0,
            "offline": [],
            "reset_detected": [],
            "restored": [],
            "errors": [],
            "hardened": [],
            "last_backup": None,
            "last_check": None,
            "last_device_check": None,
            "state_ts": None,
        }

    def _cfg(self, key: str, default: Any = None) -> Any:
        if key in self.entry.options:
            return self.entry.options[key]
        return self.entry.data.get(key, default)

    async def async_init(self) -> None:
        pref = self._cfg(CONF_BACKUP_DIR, DEFAULT_BACKUP_DIR)
        self.backup_dir = await self.hass.async_add_executor_job(core.resolve_dir, pref, DEFAULT_BACKUP_DIR)
        await self._seed_table_from_registry()
        self._publish()

    async def _seed_table_from_registry(self) -> None:
        """Populate initial device rows from HA registries + existing backups on disk."""
        inv = self.shelly_inventory()
        for mac, dev in inv.items():
            backup = await self.hass.async_add_executor_job(core.read_backup, self.backup_dir, mac)
            self.device_table[mac] = core.build_device_row(mac, dev, cur=None, backup=backup, online=True)
        self.status["devices"] = len(inv)

    def shelly_inventory(self) -> dict[str, dict[str, Any]]:
        dreg = dr.async_get(self.hass)
        areg = ar.async_get(self.hass)
        ereg = er.async_get(self.hass)
        default_user = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        default_pass = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        out: dict[str, dict[str, Any]] = {}
        for entry in self.hass.config_entries.async_entries("shelly"):
            if entry.source == "ignore" or entry.disabled_by:
                continue
            host = entry.data.get("host")
            port = int(entry.data.get("port") or 80)
            gen = int(entry.data.get("gen") or 1)
            mac = core.norm_mac(entry.unique_id or "")
            if not host or not mac:
                continue
            name, area, model, label, sw_ver = entry.title, None, entry.data.get("model"), None, None
            for dev in dr.async_entries_for_config_entry(dreg, entry.entry_id):
                if dev.via_device_id:
                    continue
                label = dev.name_by_user
                name = dev.name or name
                model = dev.model or model
                sw_ver = dev.sw_version
                if dev.area_id and (area_obj := areg.async_get_area(dev.area_id)):
                    area = area_obj.name
                break
            upd_eid = None
            for ent in er.async_entries_for_config_entry(ereg, entry.entry_id):
                if ent.entity_id.startswith("update.") and not ent.disabled_by and "beta" not in ent.entity_id:
                    upd_eid = ent.entity_id
                    break
            out[mac] = {
                "mac": mac,
                "host": host,
                "port": port,
                "gen": gen,
                "name": name,
                "area": area,
                "model": model,
                "label": label,
                "sw_version": sw_ver,
                "update_entity": upd_eid,
                "entry_id": entry.entry_id,
                "state": str(entry.state),
                "user": entry.data.get("username") or default_user,
                "password": entry.data.get("password") or default_pass,
            }
        return out

    def get_state_payload(self) -> dict[str, Any]:
        rows = sorted(
            self.device_table.values(),
            key=lambda x: (x.get("online", True), (x.get("name") or "").lower()),
        )
        return {
            "updated_at": self.status.get("state_ts"),
            "status": self.status,
            "devices": rows,
        }

    def _publish(self) -> None:
        self.status["state_ts"] = datetime.datetime.now().isoformat(timespec="seconds")
        async_dispatcher_send(self.hass, SIGNAL_UPDATE)

    async def _notify(self, title: str, message: str) -> None:
        _LOGGER.warning("[shelly_guard] %s: %s", title, message)
        svc_full = str(self._cfg(CONF_NOTIFY_SERVICE, "") or "").strip()
        if svc_full and "." in svc_full:
            dom, svc = svc_full.split(".", 1)
            payload: dict[str, Any] = {"title": title, "message": message}
            tid = self._cfg(CONF_NOTIFY_THREAD_ID, "")
            if tid:
                payload["data"] = {"push": {"thread-id": tid}}
            try:
                await self.hass.services.async_call(dom, svc, payload, blocking=False)
            except Exception as e:
                _LOGGER.error("[shelly_guard] notify failed: %s", e)

    async def _resolve_via_range_extenders(
        self,
        offline_map: dict[str, dict[str, Any]],
        range_extenders: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        resolved: dict[str, dict[str, Any]] = {}
        if not offline_map or not range_extenders:
            return resolved
        du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        for ext in range_extenders:
            u = ext.get("user") or du
            p = ext.get("password") or dp
            try:
                res = await self.hass.async_add_executor_job(
                    core.rpc, core.dev_addr(ext), "WiFi.ListAPClients", None, 4, u, p
                )
            except Exception as e:
                _LOGGER.debug("[shelly_guard] ListAPClients %s: %s", ext["name"], e)
                continue
            for c in (res or {}).get("ap_clients") or []:
                cmac = core.norm_mac(c.get("mac") or "")
                mport = c.get("mport")
                if not cmac or cmac not in offline_map or not mport:
                    continue
                dev = offline_map[cmac]
                new_host, new_port = ext["host"], int(mport)
                updated = False
                try:
                    entry = self.hass.config_entries.async_get_entry(dev["entry_id"])
                    if entry and (
                        entry.data.get("host") != new_host or int(entry.data.get("port") or 80) != new_port
                    ):
                        new_data = dict(entry.data)
                        new_data["host"] = new_host
                        new_data["port"] = new_port
                        self.hass.config_entries.async_update_entry(entry, data=new_data)
                        await self.hass.config_entries.async_reload(entry.entry_id)
                        updated = True
                except Exception as e:
                    _LOGGER.error("[shelly_guard] update range-extender entry for %s: %s", dev["name"], e)
                resolved[cmac] = {
                    "via": ext["name"],
                    "host": new_host,
                    "port": new_port,
                    "client_ip": c.get("ip"),
                    "updated": updated,
                }
                self.offline_runs.pop(cmac, None)
                self.notified.pop(cmac, None)
                if updated:
                    await self._notify(
                        "Shelly via Range Extender",
                        f"{dev['name']} ({dev['area'] or '-'}) is connected via Range Extender "
                        f"{ext['name']} ({new_host}:{new_port}). Home Assistant entry updated.",
                    )
        return resolved

    async def _scan_for_reset_aps(
        self,
        offline_devs: dict[str, dict[str, Any]],
        online_gen2: list[dict[str, Any]],
    ) -> None:
        areas = {d["area"] for d in offline_devs.values() if d.get("area")}
        same = [d for d in online_gen2 if d.get("area") in areas]
        other = [d for d in online_gen2 if d.get("area") not in areas]
        limit = int(self._cfg(CONF_SCAN_DEVICES, DEFAULT_SCAN_DEVICES))
        scanners = (same + other)[:limit]
        du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        scans: dict[str, list[dict[str, Any]]] = {}
        for d in scanners:
            res, err = await self.hass.async_add_executor_job(
                core.wifi_scan, core.dev_addr(d), d.get("user") or du, d.get("password") or dp
            )
            if res is None:
                _LOGGER.warning("[shelly_guard] scan via %s failed: %s", d["name"], err)
                continue
            scans[d["name"]] = res
        found = core.match_reset_aps(offline_devs, scans)
        needs = []
        for mac, hit in found.items():
            dev = offline_devs[mac]
            item = {
                "mac": mac,
                "name": dev["name"],
                "area": dev.get("area"),
                "gen": dev["gen"],
                "ssid": hit["ssid"],
                "near": hit["near"],
                "rssi": hit["rssi"],
            }
            needs.append(item)
            if self.notified.get(mac) == hit["ssid"]:
                continue
            self.notified[mac] = hit["ssid"]
            if dev["gen"] == 1:
                how = (
                    f"Connect to Wi-Fi '{hit['ssid']}', open http://192.168.33.1 > "
                    "Internet & Security > Wi-Fi Mode - Client and join your home Wi-Fi."
                )
            else:
                how = (
                    "In Home Assistant open Settings > Devices & services > Discovered and use "
                    "'Provision Wi-Fi via Bluetooth' (or join its Wi-Fi and open http://192.168.33.1)."
                )
            await self._notify(
                "Shelly needs Wi-Fi",
                f"{dev['name']} ({dev.get('area') or '-'}) appears factory-reset and is broadcasting "
                f"'{hit['ssid']}' near {hit['near']}. {how}",
            )
            self.hass.bus.async_fire("shelly_guard_reconnect_needed", item)
        self.status["needs_reconnect"] = needs
        self.status["last_scan"] = {
            "at": datetime.datetime.now().isoformat(timespec="seconds"),
            "scanners": list(scans.keys()),
            "offline_checked": [d["name"] for d in offline_devs.values()],
        }

    async def async_check_all(self) -> None:
        if self._lock.locked():
            _LOGGER.debug("[shelly_guard] check already running, skipping")
            return
        async with self._lock:
            inv = self.shelly_inventory()
            self.status["devices"] = len(inv)
            keep = int(self._cfg(CONF_KEEP_VERSIONS, DEFAULT_KEEP_VERSIONS))
            auto_restore = bool(self._cfg(CONF_AUTO_RESTORE, DEFAULT_AUTO_RESTORE))
            harden = bool(self._cfg(CONF_HARDEN, DEFAULT_HARDEN))
            scan_every = int(self._cfg(CONF_SCAN_EVERY_MIN, DEFAULT_SCAN_EVERY_MIN)) * 60
            du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
            dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
            wsec = self._cfg(CONF_WIFI_SECRETS_FILE, DEFAULT_WIFI_SECRETS_FILE) or ""
            wpass = self._cfg(CONF_WIFI_PASSWORD, "") or ""

            resets, restored, hardened, offline, errors, risky = [], [], [], [], [], []
            saved = 0
            online_gen2, range_extenders = [], []
            offline_devs: dict[str, dict[str, Any]] = {}
            all_offline: dict[str, dict[str, Any]] = {}

            for mac, dev in inv.items():
                backup = await self.hass.async_add_executor_job(core.read_backup, self.backup_dir, mac)
                try:
                    cur = await self.hass.async_add_executor_job(core.fetch_device, dev, du, dp)
                except Exception as e:
                    err_msg = f"{type(e).__name__} {str(e)[:120]}"
                    offline.append(f"{dev['name']}: {err_msg}")
                    all_offline[mac] = dev
                    self.device_table[mac] = core.build_device_row(
                        mac, dev, cur=None, backup=backup, online=False, err=err_msg
                    )
                    self.offline_runs[mac] = self.offline_runs.get(mac, 0) + 1
                    if self.offline_runs[mac] >= 2:
                        offline_devs[mac] = dev
                    continue

                if self.offline_runs.pop(mac, 0) and mac in self.notified:
                    self.notified.pop(mac, None)
                    await self._notify(
                        "Shelly back online",
                        f"{dev['name']} ({dev.get('area') or '-'}) is back on the network.",
                    )

                if dev["gen"] != 1:
                    online_gen2.append(dev)
                    re_cfg = (
                        ((cur["config"].get("config") or {}).get("wifi") or {}).get("ap") or {}
                    ).get("range_extender") or {}
                    if re_cfg.get("enable"):
                        range_extenders.append(dev)

                if dev["gen"] == 1:
                    is_reset = core.gen1_looks_factory(
                        cur["config"]["settings"], backup and backup["config"]["settings"]
                    )
                else:
                    is_reset = core.gen2_looks_factory(
                        cur["config"]["config"], backup and backup["config"]
                    )

                if is_reset:
                    self.suspect[mac] = self.suspect.get(mac, 0) + 1
                    resets.append(dev["name"])
                    self.device_table[mac] = core.build_device_row(
                        mac, dev, cur=cur, backup=backup, online=True, reset=True
                    )
                    if self.suspect[mac] < 2:
                        continue
                    self.suspect.pop(mac, None)
                    if auto_restore and backup:
                        done, failed = await self.hass.async_add_executor_job(
                            core.restore_device, dev, backup, False, du, dp, wsec, wpass
                        )
                        restored.append(dev["name"])
                        await self._notify(
                            "Shelly restored",
                            f"{dev['name']} ({dev.get('area') or '-'}) came back factory-reset and was "
                            f"restored from {backup['saved_at']}: {len(done)} steps ok"
                            + (f", to check: {'; '.join(failed)}" if failed else "."),
                        )
                        if failed:
                            errors.extend(f"{dev['name']}: {f}" for f in failed)
                    elif backup:
                        await self._notify(
                            "Shelly factory-reset detected",
                            f"{dev['name']} lost its configuration. Backup from {backup['saved_at']} is ready.",
                        )
                    continue

                self.suspect.pop(mac, None)
                ch: list[Any] = []
                if harden:
                    try:
                        ch = await self.hass.async_add_executor_job(core.harden_device, dev, cur, du, dp)
                        if ch:
                            hardened.append(f"{dev['name']}: {ch}")
                    except Exception as e:
                        errors.append(f"{dev['name']} harden: {e}")

                try:
                    final = (
                        await self.hass.async_add_executor_job(core.fetch_device, dev, du, dp)
                        if ch
                        else cur
                    )
                    await self.hass.async_add_executor_job(core.write_backup, self.backup_dir, mac, final, keep)
                    saved += 1
                    if core.reset_by_input_enabled(final):
                        risky.append(dev["name"])
                    self.device_table[mac] = core.build_device_row(mac, dev, cur=final, backup=final, online=True)
                except Exception as e:
                    errors.append(f"{dev['name']} backup: {e}")
                    self.device_table[mac] = core.build_device_row(
                        mac, dev, cur=cur, backup=backup, online=True, err=str(e)
                    )

            for stale in [m for m in list(self.device_table) if m not in inv]:
                self.device_table.pop(stale, None)

            re_resolved = await self._resolve_via_range_extenders(all_offline, range_extenders)
            for cmac, rinfo in re_resolved.items():
                offline_devs.pop(cmac, None)
                cname = all_offline[cmac]["name"]
                offline = [o for o in offline if not o.startswith(f"{cname}:")]
                dev_re = dict(all_offline[cmac])
                dev_re["host"] = rinfo["host"]
                dev_re["port"] = rinfo["port"]
                try:
                    cur_re = await self.hass.async_add_executor_job(core.fetch_device, dev_re, du, dp)
                    await self.hass.async_add_executor_job(core.write_backup, self.backup_dir, cmac, cur_re, keep)
                    saved += 1
                    self.device_table[cmac] = core.build_device_row(
                        cmac, dev_re, cur=cur_re, backup=cur_re, online=True
                    )
                except Exception:
                    if cmac in self.device_table:
                        self.device_table[cmac]["host"] = rinfo["host"]
                        self.device_table[cmac]["port"] = rinfo["port"]
                        self.device_table[cmac]["online"] = True
                        self.device_table[cmac]["error"] = ""

            if offline_devs and time.time() - self.last_scan_ts >= scan_every:
                await self._scan_for_reset_aps(offline_devs, online_gen2)
                self.last_scan_ts = time.time()

            self.status.update(
                reset_detected=resets,
                restored=restored,
                hardened=hardened,
                offline=offline,
                range_extender_resolved=re_resolved,
                backed_up=saved,
                reset_by_switch_still_on=risky,
                errors=errors[-20:],
                last_check=datetime.datetime.now().isoformat(timespec="seconds"),
            )
            self._publish()

    async def async_check_device(self, mac: str) -> None:
        m = core.norm_mac(mac or "")
        if not m:
            _LOGGER.error("[shelly_guard] check_device: invalid mac=%s", mac)
            return
        inv = self.shelly_inventory()
        dev = inv.get(m)
        if not dev:
            _LOGGER.error("[shelly_guard] check_device: mac %s not found in HA Shelly inventory", m)
            return
        keep = int(self._cfg(CONF_KEEP_VERSIONS, DEFAULT_KEEP_VERSIONS))
        harden = bool(self._cfg(CONF_HARDEN, DEFAULT_HARDEN))
        du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        backup = await self.hass.async_add_executor_job(core.read_backup, self.backup_dir, m)

        try:
            cur = await self.hass.async_add_executor_job(core.fetch_device, dev, du, dp)
        except Exception as e:
            err_msg = f"{type(e).__name__} {str(e)[:120]}"
            re_hosts = [d for d in inv.values() if d["gen"] != 1 and d["mac"] != m]
            re_res = await self._resolve_via_range_extenders({m: dev}, re_hosts)
            if m in re_res:
                dev = dict(dev)
                dev["host"] = re_res[m]["host"]
                dev["port"] = re_res[m]["port"]
                try:
                    cur = await self.hass.async_add_executor_job(core.fetch_device, dev, du, dp)
                except Exception as e2:
                    self.device_table[m] = core.build_device_row(
                        m, dev, cur=None, backup=backup, online=False, err=str(e2)
                    )
                    self._publish()
                    return
            else:
                self.device_table[m] = core.build_device_row(
                    m, dev, cur=None, backup=backup, online=False, err=err_msg
                )
                self._publish()
                return

        if harden:
            try:
                ch = await self.hass.async_add_executor_job(core.harden_device, dev, cur, du, dp)
                if ch:
                    cur = await self.hass.async_add_executor_job(core.fetch_device, dev, du, dp)
            except Exception as e:
                _LOGGER.warning("[shelly_guard] single harden %s: %s", dev["name"], e)
        try:
            await self.hass.async_add_executor_job(core.write_backup, self.backup_dir, m, cur, keep)
        except Exception as e:
            _LOGGER.warning("[shelly_guard] single backup %s: %s", dev["name"], e)

        self.device_table[m] = core.build_device_row(m, dev, cur=cur, backup=cur, online=True)
        self.status["offline"] = [o for o in self.status.get("offline", []) if not o.startswith(f"{dev['name']}:")]
        self.status["last_device_check"] = f"{dev['name']} @ {datetime.datetime.now().strftime('%H:%M:%S')}"
        self._publish()

    async def async_backup_all(self) -> None:
        inv = self.shelly_inventory()
        keep = int(self._cfg(CONF_KEEP_VERSIONS, DEFAULT_KEEP_VERSIONS))
        du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        offline: list[str] = []
        index: dict[str, Any] = {}
        changed = 0
        for mac, dev in inv.items():
            try:
                payload = await self.hass.async_add_executor_job(core.fetch_device, dev, du, dp)
                if await self.hass.async_add_executor_job(core.write_backup, self.backup_dir, mac, payload, keep):
                    changed += 1
                index[mac] = {k: dev[k] for k in ("name", "area", "model", "host", "port", "gen")}
                index[mac]["saved_at"] = payload["saved_at"]
                self.device_table[mac] = core.build_device_row(mac, dev, cur=payload, backup=payload, online=True)
            except Exception as e:
                offline.append(dev["name"])
                _LOGGER.info("[shelly_guard] backup %s (%s): %s", dev["name"], dev["host"], e)
        await self.hass.async_add_executor_job(core.write_index, self.backup_dir, index)
        self.status.update(
            devices=len(inv),
            offline=offline,
            last_backup=datetime.datetime.now().isoformat(timespec="seconds"),
        )
        self._publish()
        _LOGGER.info("[shelly_guard] backup done: %d ok, %d changed, %d offline", len(index), changed, len(offline))

    async def async_restore(
        self,
        mac: str,
        host: str | None = None,
        dry_run: bool = True,
        backup_mac: str | None = None,
    ) -> dict[str, Any]:
        m = core.norm_mac(mac or "")
        if not m:
            return {"error": "invalid mac"}
        inv = self.shelly_inventory()
        dev = dict(inv.get(m) or {"mac": m, "host": host, "port": 80, "gen": None, "name": m, "area": None, "model": None})
        if host:
            dev["host"] = host
        bmac = core.norm_mac(backup_mac) if backup_mac else m
        backup = await self.hass.async_add_executor_job(core.read_backup, self.backup_dir, bmac or m)
        if not backup:
            _LOGGER.error("[shelly_guard] no backup for %s", bmac or m)
            return {"error": f"no backup for {bmac or m}"}
        du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        wsec = self._cfg(CONF_WIFI_SECRETS_FILE, DEFAULT_WIFI_SECRETS_FILE) or ""
        wpass = self._cfg(CONF_WIFI_PASSWORD, "") or ""
        done, failed = await self.hass.async_add_executor_job(
            core.restore_device, dev, backup, dry_run, du, dp, wsec, wpass
        )
        _LOGGER.warning("[shelly_guard] restore %s dry_run=%s: %d ok, %d issues", dev["name"], dry_run, len(done), len(failed))
        return {"done": done, "failed": failed}

    async def async_scan_now(self) -> None:
        inv = self.shelly_inventory()
        du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        offline_devs: dict[str, dict[str, Any]] = {}
        online_gen2: list[dict[str, Any]] = []
        for mac, dev in inv.items():
            u = dev.get("user") or du
            p = dev.get("password") or dp
            addr = core.dev_addr(dev)
            try:
                if dev["gen"] == 1:
                    await self.hass.async_add_executor_job(core.gen1_get, addr, "/shelly", None, 4, u, p)
                else:
                    await self.hass.async_add_executor_job(core.rpc, addr, "Shelly.GetDeviceInfo", None, 4, u, p)
                    online_gen2.append(dev)
            except Exception:
                offline_devs[mac] = dev
        resolved = await self._resolve_via_range_extenders(offline_devs, online_gen2)
        for cmac in resolved:
            offline_devs.pop(cmac, None)
        await self._scan_for_reset_aps(offline_devs, online_gen2)
        self.last_scan_ts = time.time()
        self._publish()

    async def async_audit(self, fix: bool = False) -> None:
        du = self._cfg(CONF_SHELLY_USER, DEFAULT_SHELLY_USER) or DEFAULT_SHELLY_USER
        dp = self._cfg(CONF_SHELLY_PASSWORD, "") or ""
        report: list[str] = []
        for dev in self.shelly_inventory().values():
            if dev["gen"] == 1:
                continue
            u = dev.get("user") or du
            p = dev.get("password") or dp
            addr = core.dev_addr(dev)
            try:
                scripts = (await self.hass.async_add_executor_job(core.rpc, addr, "Script.List", None, 8, u, p) or {}).get("scripts", [])
                hooks = (await self.hass.async_add_executor_job(core.rpc, addr, "Webhook.List", None, 8, u, p) or {}).get("hooks", [])
            except Exception:
                continue
            seen: dict[Any, int] = {}
            for sc in scripts:
                key = sc.get("name")
                if key in seen:
                    report.append(f"{dev['name']}: duplicate script '{key}' id={sc['id']}")
                    if fix:
                        try:
                            await self.hass.async_add_executor_job(core.rpc, addr, "Script.Stop", {"id": sc["id"]}, 8, u, p)
                        except Exception:
                            pass
                        await self.hass.async_add_executor_job(core.rpc, addr, "Script.Delete", {"id": sc["id"]}, 8, u, p)
                else:
                    seen[key] = sc["id"]
            seen = {}
            for h in hooks:
                key = (h.get("name"), h.get("event"), h.get("cid"), tuple(h.get("urls") or []))
                if key in seen:
                    report.append(f"{dev['name']}: duplicate webhook {key[0]}/{key[1]} id={h['id']}")
                    if fix:
                        await self.hass.async_add_executor_job(core.rpc, addr, "Webhook.Delete", {"id": h["id"]}, 8, u, p)
                else:
                    seen[key] = h["id"]
        self.status["audit"] = report or ["no duplicates"]
        self._publish()

    async def async_router_dhcp(self, apply: bool = False) -> None:
        ents = self.hass.config_entries.async_entries("asusrouter")
        if not ents:
            _LOGGER.error("[shelly_guard] no asusrouter integration configured")
            return
        d = dict(ents[0].data)
        d.update(dict(ents[0].options or {}))
        host = d.get("host")
        port = d.get("port") or (8443 if d.get("ssl") or d.get("use_ssl") else 80)
        proto = "https" if (d.get("ssl") or d.get("use_ssl") or port in (443, 8443)) else "http"
        base = f"{proto}://{host}:{port}"
        user, pw = d.get("username", ""), d.get("password", "")
        cur = await self.hass.async_add_executor_job(core.asus_dhcp, base, user, pw)
        if cur.get("error"):
            self.status["router_dhcp"] = {"error": cur["error"], "base": base}
            self._publish()
            return
        existing = core.parse_staticlist(cur.get("dhcp_staticlist"))
        template = existing[0]["rest"] if existing else ["", "__NAME__"]
        template = ["__NAME__" if i == len(template) - 1 else "" for i in range(len(template))] or ["", "__NAME__"]
        wanted: dict[str, tuple[str, str]] = {}
        for mac, dev in self.shelly_inventory().items():
            if int(dev.get("port") or 80) != 80:
                continue
            if "Pro" in str(dev.get("model") or ""):
                mac = "%012X" % (int(mac, 16) + 3)
            wanted[":".join(mac[i : i + 2] for i in range(0, 12, 2))] = (dev["host"], dev["name"])
        to_add, conflicts, already = core.plan_reservations(existing, wanted, template)
        raw = cur.get("dhcp_staticlist") or ""
        sane = ("&#" not in raw) and (len(existing) == raw.count("<")) and all(
            len(e["mac"]) == 17 and e["ip"].count(".") == 3 for e in existing
        )
        report: dict[str, Any] = {
            "router": f"{cur.get('productid')} {cur.get('firmver')}.{cur.get('buildno')}",
            "existing_count": len(existing),
            "already_ok": already,
            "to_add": [f"{a['name']} {a['mac']} {a['ip']}" for a in to_add],
            "conflicts": conflicts,
            "parse_ok": sane,
            "applied": False,
        }
        if apply and to_add and sane:
            new_raw = core.build_staticlist(existing + to_add)
            res = await self.hass.async_add_executor_job(core.asus_dhcp, base, user, pw, new_raw)
            after = core.parse_staticlist(res.get("after"))
            report["applied"] = True
            report["count_after"] = len(after)
        self.status["router_dhcp"] = report
        self._publish()

    async def async_sync_netalertx(self) -> None:
        url = str(self._cfg(CONF_NETALERTX_URL, "") or "").strip()
        tok = str(self._cfg(CONF_NETALERTX_TOKEN, "") or "").strip()
        if not (url and tok):
            _LOGGER.error("[shelly_guard] NetAlertX URL/token not configured")
            return
        ok, missing = 0, []
        for mac, dev in self.shelly_inventory().items():
            cm = core.colon_mac(mac) or ""
            code, txt = await self.hass.async_add_executor_job(core.nax_update, url, tok, cm, "devName", dev["name"])
            if code == 200 and "false" not in txt.lower():
                ok += 1
                await self.hass.async_add_executor_job(core.nax_update, url, tok, cm, "devVendor", "Shelly")
                if dev.get("area"):
                    await self.hass.async_add_executor_job(core.nax_update, url, tok, cm, "devLocation", dev["area"])
            else:
                missing.append(f"{dev['name']} {cm} [{code}]")
        self.status["netalertx"] = {"renamed": ok, "failed": missing}
        self._publish()
