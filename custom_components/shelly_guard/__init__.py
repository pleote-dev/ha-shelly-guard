"""Shelly Guard — Home Assistant native integration (no Pyscript required)."""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import Any

from aiohttp import web
from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_change, async_track_time_interval

from .const import (
    API_ACTION_PATH,
    API_BACKUPS_PATH,
    API_STATE_PATH,
    CONF_CHECK_INTERVAL_MIN,
    CONF_NETALERTX_TOKEN,
    CONF_NETALERTX_URL,
    CONF_SHOW_SIDEBAR,
    DEFAULT_CHECK_INTERVAL_MIN,
    DEFAULT_SHOW_SIDEBAR,
    DOMAIN,
    PANEL_URL_PATH,
    STATIC_URL_PATH,
    VERSION,
)
from .manager import ShellyGuardManager

try:
    from homeassistant.core import SupportsResponse
except ImportError:  # pragma: no cover
    SupportsResponse = None  # type: ignore[assignment]

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

SERVICE_NAMES = (
    "check",
    "check_device",
    "backup_all",
    "backup_device",
    "restore",
    "scan",
    "audit",
    "router_dhcp",
    "sync_netalertx",
    "reload",
    "set_metadata",
    "set_lifecycle",
    "confirm_new_device",
    "replace_device",
)


class ShellyGuardStateView(HomeAssistantView):
    """Authenticated HTTP endpoint returning live Shelly Guard device table."""

    url = API_STATE_PATH
    name = "api:shelly_guard:state"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        data = hass.data.get(DOMAIN) or {}
        manager: ShellyGuardManager | None = data.get("manager")
        if not manager:
            return self.json({"devices": [], "status": {}, "updated_at": None})
        return self.json(manager.get_state_payload())


class ShellyGuardBackupsView(HomeAssistantView):
    """Authenticated HTTP endpoint returning backup snapshots for a single device."""

    url = API_BACKUPS_PATH
    name = "api:shelly_guard:backups"
    requires_auth = True

    async def get(self, request: web.Request, mac: str) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        data = hass.data.get(DOMAIN) or {}
        manager: ShellyGuardManager | None = data.get("manager")
        if not manager:
            return self.json({"ok": False, "error": "manager_not_ready", "backups": []}, status_code=503)
        res = await manager.async_get_device_backups(mac)
        return self.json(res)


class ShellyGuardActionView(HomeAssistantView):
    """Authenticated HTTP endpoint returning synchronous results for UI device actions."""

    url = API_ACTION_PATH
    name = "api:shelly_guard:action"
    requires_auth = True

    async def post(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        data = hass.data.get(DOMAIN) or {}
        manager: ShellyGuardManager | None = data.get("manager")
        if not manager:
            return self.json({"ok": False, "error": "manager_not_ready"}, status_code=503)
        try:
            body = await request.json()
        except Exception:
            return self.json({"ok": False, "error": "invalid_json"}, status_code=400)

        act = str(body.get("action") or "").strip()
        if act == "backup_device":
            res = await manager.async_backup_device(
                mac=str(body.get("mac") or ""),
                force=bool(body.get("force", False)),
            )
            return self.json(res)
        if act == "check_device":
            res = await manager.async_check_device(str(body.get("mac") or ""))
            return self.json(res)
        if act == "restore":
            res = await manager.async_restore(
                mac=str(body.get("mac") or ""),
                host=body.get("host") or None,
                dry_run=bool(body.get("dry_run", True)),
                backup_mac=body.get("backup_mac") or None,
                version=body.get("version") or None,
            )
            return self.json(res)
        if act == "confirm_new_device":
            res = await manager.async_confirm_new_device(
                mac=str(body.get("mac") or ""),
                purchase_date=body.get("purchase_date"),
                warranty_months=body.get("warranty_months"),
                vendor=body.get("vendor"),
                invoice_number=body.get("invoice_number"),
                notes=body.get("notes"),
            )
            return self.json(res)
        if act == "replace_device":
            res = await manager.async_replace_device(
                old_mac=str(body.get("old_mac") or ""),
                new_mac=str(body.get("new_mac") or ""),
                purchase_date=body.get("purchase_date"),
                warranty_months=body.get("warranty_months"),
                vendor=body.get("vendor"),
                invoice_number=body.get("invoice_number"),
                notes=body.get("notes"),
            )
            return self.json(res)
        return self.json({"ok": False, "error": f"unknown action '{act}'"}, status_code=400)


async def _async_register_frontend(hass: HomeAssistant, show_sidebar: bool) -> None:
    """Serve frontend JS and register the Shelly Guard sidebar panel."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    frontend_dir = str(Path(__file__).parent / "frontend")

    if not domain_data.get("static_registered"):
        try:
            from homeassistant.components.http import StaticPathConfig

            await hass.http.async_register_static_paths(
                [StaticPathConfig(STATIC_URL_PATH, frontend_dir, cache_headers=False)]
            )
        except Exception:
            hass.http.register_static_path(STATIC_URL_PATH, frontend_dir, cache_headers=False)
        hass.http.register_view(ShellyGuardStateView())
        domain_data["static_registered"] = True

    if not domain_data.get("action_views_registered"):
        hass.http.register_view(ShellyGuardBackupsView())
        hass.http.register_view(ShellyGuardActionView())
        domain_data["action_views_registered"] = True

    if show_sidebar and not domain_data.get("panel_registered"):
        try:
            await panel_custom.async_register_panel(
                hass,
                webcomponent_name="shelly-guard-panel",
                frontend_url_path=PANEL_URL_PATH,
                sidebar_title="Shelly Guard",
                sidebar_icon="mdi:shield-sync",
                module_url=f"{STATIC_URL_PATH}/shelly-guard-panel.js?v={VERSION}",
                embed_iframe=False,
                require_admin=False,
            )
            domain_data["panel_registered"] = True
        except ValueError as err:
            _LOGGER.warning(
                "[shelly_guard] Sidebar panel '%s' already exists (%s). "
                "Remove any legacy Lovelace dashboard with url_path '%s' and reload Shelly Guard.",
                PANEL_URL_PATH,
                err,
                PANEL_URL_PATH,
            )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Shelly Guard from a config entry."""
    manager = ShellyGuardManager(hass, entry)
    await manager.async_init()

    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data["manager"] = manager
    domain_data["entry_id"] = entry.entry_id

    show_sidebar = entry.options.get(
        CONF_SHOW_SIDEBAR, entry.data.get(CONF_SHOW_SIDEBAR, DEFAULT_SHOW_SIDEBAR)
    )
    await _async_register_frontend(hass, bool(show_sidebar))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def _svc_check(call: ServiceCall) -> None:
        hass.async_create_task(manager.async_check_all())

    async def _svc_check_device(call: ServiceCall) -> dict[str, Any]:
        return await manager.async_check_device(call.data.get("mac", ""))

    async def _svc_backup_all(call: ServiceCall) -> None:
        hass.async_create_task(manager.async_backup_all())

    async def _svc_backup_device(call: ServiceCall) -> dict[str, Any]:
        return await manager.async_backup_device(
            mac=call.data.get("mac", ""),
            force=bool(call.data.get("force", False)),
        )

    async def _svc_restore(call: ServiceCall) -> dict[str, Any]:
        return await manager.async_restore(
            mac=call.data.get("mac", ""),
            host=call.data.get("host"),
            dry_run=bool(call.data.get("dry_run", True)),
            backup_mac=call.data.get("backup_mac"),
            version=call.data.get("version"),
        )

    async def _svc_scan(call: ServiceCall) -> None:
        hass.async_create_task(manager.async_scan_now())

    async def _svc_audit(call: ServiceCall) -> None:
        hass.async_create_task(manager.async_audit(fix=bool(call.data.get("fix", False))))

    async def _svc_router_dhcp(call: ServiceCall) -> None:
        hass.async_create_task(manager.async_router_dhcp(apply=bool(call.data.get("apply", False))))

    async def _svc_sync_nax(call: ServiceCall) -> None:
        hass.async_create_task(manager.async_sync_netalertx())

    async def _svc_reload(call: ServiceCall) -> None:
        await hass.config_entries.async_reload(entry.entry_id)

    async def _svc_set_metadata(call: ServiceCall) -> None:
        await manager.async_set_metadata(
            mac=call.data.get("mac", ""),
            purchase_date=call.data.get("purchase_date"),
            warranty_months=call.data.get("warranty_months"),
            vendor=call.data.get("vendor"),
            invoice_number=call.data.get("invoice_number"),
            notes=call.data.get("notes"),
        )

    async def _svc_set_lifecycle(call: ServiceCall) -> None:
        await manager.async_set_lifecycle(
            mac=call.data.get("mac", ""),
            lifecycle=call.data.get("lifecycle", "active"),
            reason=call.data.get("reason", ""),
        )

    async def _svc_confirm_new(call: ServiceCall) -> None:
        hass.async_create_task(
            manager.async_confirm_new_device(
                mac=call.data.get("mac", ""),
                purchase_date=call.data.get("purchase_date"),
                warranty_months=call.data.get("warranty_months"),
                vendor=call.data.get("vendor"),
                invoice_number=call.data.get("invoice_number"),
                notes=call.data.get("notes"),
            )
        )

    async def _svc_replace(call: ServiceCall) -> None:
        hass.async_create_task(
            manager.async_replace_device(
                old_mac=call.data.get("old_mac", ""),
                new_mac=call.data.get("new_mac", ""),
                purchase_date=call.data.get("purchase_date"),
                warranty_months=call.data.get("warranty_months"),
                vendor=call.data.get("vendor"),
                invoice_number=call.data.get("invoice_number"),
                notes=call.data.get("notes"),
            )
        )

    services: dict[str, Any] = {
        "check": _svc_check,
        "check_device": _svc_check_device,
        "backup_all": _svc_backup_all,
        "backup_device": _svc_backup_device,
        "restore": _svc_restore,
        "scan": _svc_scan,
        "audit": _svc_audit,
        "router_dhcp": _svc_router_dhcp,
        "sync_netalertx": _svc_sync_nax,
        "reload": _svc_reload,
        "set_metadata": _svc_set_metadata,
        "set_lifecycle": _svc_set_lifecycle,
        "confirm_new_device": _svc_confirm_new,
        "replace_device": _svc_replace,
    }
    response_services = {"check_device", "backup_device", "restore"}
    for name, handler in services.items():
        if SupportsResponse is not None and name in response_services:
            hass.services.async_register(
                DOMAIN, name, handler, supports_response=SupportsResponse.OPTIONAL
            )
        else:
            hass.services.async_register(DOMAIN, name, handler)

    # Detect newly added Shelly devices immediately
    async def _on_device_reg_updated(event: Any) -> None:
        if event.data.get("action") == "create":
            await manager.async_detect_new_devices(notify=True)
            manager._publish()

    unsub_dev_reg = hass.bus.async_listen("device_registry_updated", _on_device_reg_updated)
    entry.async_on_unload(unsub_dev_reg)

    # Periodic check & nightly backup
    interval_min = int(
        entry.options.get(
            CONF_CHECK_INTERVAL_MIN,
            entry.data.get(CONF_CHECK_INTERVAL_MIN, DEFAULT_CHECK_INTERVAL_MIN),
        )
    )
    unsub_interval = async_track_time_interval(
        hass,
        lambda _now: hass.async_create_task(manager.async_check_all()),
        datetime.timedelta(minutes=max(1, interval_min)),
    )

    async def _nightly(_now: Any) -> None:
        await manager.async_backup_all()
        if manager._cfg(CONF_NETALERTX_URL) and manager._cfg(CONF_NETALERTX_TOKEN):
            await manager.async_sync_netalertx()

    unsub_nightly = async_track_time_change(
        hass,
        lambda _now: hass.async_create_task(_nightly(_now)),
        hour=4,
        minute=17,
        second=0,
    )

    entry.async_on_unload(unsub_interval)
    entry.async_on_unload(unsub_nightly)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Run an initial check once HA has finished starting
    if hass.is_running:
        hass.async_create_task(manager.async_check_all())
    else:
        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED,
            lambda _evt: hass.async_create_task(manager.async_check_all()),
        )

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        domain_data = hass.data.get(DOMAIN, {})
        domain_data.pop("manager", None)
        if domain_data.pop("panel_registered", False):
            try:
                frontend.async_remove_panel(hass, PANEL_URL_PATH)
            except Exception:
                pass
        for svc in SERVICE_NAMES:
            if hass.services.has_service(DOMAIN, svc):
                hass.services.async_remove(DOMAIN, svc)
    return unload_ok
