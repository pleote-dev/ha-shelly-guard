"""Pure-Python Shelly Guard engine (Gen1/Gen2+ HTTP/RPC, backup, hardening, restore, scans)."""

from __future__ import annotations

import base64
import datetime
import hashlib
import html as _html
import json
import os
import re as _re
import threading
import time
from typing import Any

import requests
import urllib3

from .const import DEFAULT_WARRANTY_MONTHS, HTTP_TIMEOUT, MARKER_KEY


def resolve_dir(preferred: str, fallback: str = "/share/shelly_guard") -> str:
    for d in (preferred, fallback):
        if not d:
            continue
        try:
            os.makedirs(d, exist_ok=True)
            probe = os.path.join(d, ".write_test")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(probe)
            return d
        except Exception:
            continue
    return fallback


def norm_mac(mac: Any) -> str | None:
    m = "".join(c for c in str(mac) if c.isalnum()).upper()
    return m if len(m) == 12 else None


def colon_mac(mac: Any) -> str | None:
    m = norm_mac(mac)
    return ":".join(m[i : i + 2] for i in range(0, 12, 2)).lower() if m else None


def dev_addr(dev: dict[str, Any]) -> str:
    h = str(dev["host"])
    p = int(dev.get("port") or 80)
    return f"{h}:{p}" if (p != 80 and ":" not in h) else h


def short_fw(raw: Any) -> str:
    s = str(raw or "").strip()
    if not s:
        return ""
    if "/" in s:
        s = s.split("/", 1)[1]
    for sep in ("-g", "@"):
        if sep in s:
            s = s.split(sep, 1)[0]
    return s


def rpc(
    host: str,
    method: str,
    params: dict[str, Any] | None = None,
    timeout: int = HTTP_TIMEOUT,
    user: str = "admin",
    password: str = "",
) -> Any:
    """Gen2+ JSON-RPC over HTTP POST /rpc."""
    body: dict[str, Any] = {"id": 1, "method": method}
    if params is not None:
        body["params"] = params
    auth = requests.auth.HTTPDigestAuth(user, password) if password else None
    r = requests.post(f"http://{host}/rpc", json=body, timeout=timeout, auth=auth)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"{method}: {data['error']}")
    return data.get("result")


def gen1_get(
    host: str,
    path: str,
    params: dict[str, Any] | None = None,
    timeout: int = HTTP_TIMEOUT,
    user: str = "admin",
    password: str = "",
) -> Any:
    auth = (user, password) if password else None
    r = requests.get(f"http://{host}{path}", params=params, timeout=timeout, auth=auth)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return r.text


def wifi_scan(
    host: str,
    user: str = "admin",
    password: str = "",
    hard_timeout: int = 30,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """WiFi.Scan with a hard wall-clock limit."""
    box: dict[str, Any] = {}

    def worker() -> None:
        try:
            auth = requests.auth.HTTPDigestAuth(user, password) if password else None
            r = requests.post(
                f"http://{host}/rpc",
                json={"id": 1, "method": "WiFi.Scan"},
                timeout=(4, 20),
                auth=auth,
            )
            box["res"] = (r.json().get("result") or {}).get("results", [])
        except Exception as e:
            box["err"] = f"{type(e).__name__}: {e}"

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(hard_timeout)
    if t.is_alive():
        return None, "hard timeout"
    return box.get("res"), box.get("err")


def wifi_creds(
    path: str,
    ssid_key: str = "conf_ssid",
    pass_key: str = "conf_ssidpass",
    fallback_pass: str = "",
) -> tuple[str | None, str]:
    try:
        import yaml

        with open(path, encoding="utf-8") as f:
            sec = yaml.safe_load(f) or {}
        return sec.get(ssid_key), sec.get(pass_key) or fallback_pass
    except Exception:
        return None, fallback_pass


def write_backup(backup_dir: str, mac: str, payload: dict[str, Any], keep: int) -> bool:
    """Write latest.json; keep a dated copy only when content changed."""
    d = os.path.join(backup_dir, mac)
    os.makedirs(d, exist_ok=True)
    body = json.dumps(payload["config"], sort_keys=True)
    digest = hashlib.sha256(body.encode()).hexdigest()[:16]
    latest = os.path.join(d, "latest.json")
    old_digest = None
    if os.path.exists(latest):
        try:
            with open(latest, encoding="utf-8") as f:
                old_digest = json.load(f).get("digest")
        except Exception:
            pass
    payload["digest"] = digest
    tmp = f"{latest}.{os.getpid()}.{time.time_ns()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, sort_keys=True)
    os.replace(tmp, latest)
    changed = digest != old_digest
    if changed:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(d, f"{stamp}_{digest}.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1, sort_keys=True)
        versions = sorted(x for x in os.listdir(d) if x[:2] == "20" and x.endswith(".json"))
        for old in versions[:-keep]:
            os.remove(os.path.join(d, old))
    return changed


def read_backup(backup_dir: str, mac: str) -> dict[str, Any] | None:
    p = os.path.join(backup_dir, mac, "latest.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_index(backup_dir: str, index: dict[str, Any]) -> None:
    os.makedirs(backup_dir, exist_ok=True)
    with open(os.path.join(backup_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1, sort_keys=True)


def read_metadata(backup_dir: str) -> dict[str, dict[str, Any]]:
    p = os.path.join(backup_dir, "metadata.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_metadata(backup_dir: str, metadata: dict[str, dict[str, Any]]) -> None:
    os.makedirs(backup_dir, exist_ok=True)
    p = os.path.join(backup_dir, "metadata.json")
    tmp = f"{p}.{os.getpid()}.{time.time_ns()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, sort_keys=True, ensure_ascii=False)
    os.replace(tmp, p)


def _add_months(d: datetime.date, months: int) -> datetime.date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    # clamp day to end of month
    next_m = datetime.date(y + (m // 12), (m % 12) + 1, 1)
    max_day = (next_m - datetime.timedelta(days=1)).day
    return datetime.date(y, m, min(d.day, max_day))


def compute_warranty(meta: dict[str, Any] | None) -> dict[str, Any]:
    """Return warranty_until (YYYY-MM-DD), days_left, and status (valid|expiring|expired|unknown)."""
    m = meta or {}
    pdate_str = str(m.get("purchase_date") or "").strip()
    months = m.get("warranty_months")
    try:
        months_int = int(months) if months not in (None, "") else DEFAULT_WARRANTY_MONTHS
    except Exception:
        months_int = DEFAULT_WARRANTY_MONTHS
    if not pdate_str:
        return {
            "purchase_date": "",
            "warranty_months": months_int,
            "warranty_until": "",
            "warranty_days_left": None,
            "warranty_status": "unknown",
        }
    try:
        pdate = datetime.date.fromisoformat(pdate_str[:10])
    except Exception:
        return {
            "purchase_date": pdate_str,
            "warranty_months": months_int,
            "warranty_until": "",
            "warranty_days_left": None,
            "warranty_status": "unknown",
        }
    until = _add_months(pdate, max(0, months_int))
    days_left = (until - datetime.date.today()).days
    if days_left < 0:
        status = "expired"
    elif days_left <= 90:
        status = "expiring"
    else:
        status = "valid"
    return {
        "purchase_date": pdate.isoformat(),
        "warranty_months": months_int,
        "warranty_until": until.isoformat(),
        "warranty_days_left": days_left,
        "warranty_status": status,
    }


def nax_update(url: str, token: str, mac: str, column: str, value: str) -> tuple[int, str]:
    r = requests.post(
        f"{url.rstrip('/')}/device/{mac}/update-column",
        headers={"Authorization": f"Bearer {token}"},
        json={"columnName": column, "columnValue": value},
        timeout=HTTP_TIMEOUT,
    )
    return r.status_code, r.text[:200]


def asus_dhcp(
    base: str,
    user: str,
    password: str,
    new_list: str | None = None,
    clients: bool = False,
) -> dict[str, Any]:
    """Read (and optionally write) the ASUS DHCP static list through the router's web API."""
    urllib3.disable_warnings()
    ua = {"User-Agent": "asusrouter--DUTUtil-", "Referer": base + "/"}
    s = requests.Session()
    r = s.post(
        base + "/login.cgi",
        headers=ua,
        verify=False,
        timeout=10,
        data={"login_authorization": base64.b64encode(f"{user}:{password}".encode()).decode()},
    )
    tok = (
        r.json()
        if r.headers.get("content-type", "").startswith("application/json") or r.text.startswith("{")
        else {}
    ).get("asus_token")
    if not tok:
        return {"error": f"login failed ({r.status_code})"}
    s.cookies.set("asus_token", tok)
    out: dict[str, Any] = {}
    try:
        q = (
            "nvram_get(dhcp_staticlist);nvram_get(dhcp_start);nvram_get(dhcp_end);"
            "nvram_get(dhcp_static_x);nvram_get(dhcp_hostnames);nvram_get(productid);"
            "nvram_get(firmver);nvram_get(buildno)"
        )
        g = s.get(base + "/appGet.cgi", params={"hook": q}, headers=ua, verify=False, timeout=10)

        def _dec(v: str) -> str:
            v = _re.sub(r"&#(60|62);?", lambda m: "<" if m.group(1) == "60" else ">", v)
            return _html.unescape(v)

        out = {k: (_dec(v) if isinstance(v, str) else v) for k, v in json.loads(g.text).items()}
        if clients:
            c = s.get(base + "/appGet.cgi", params={"hook": "get_clientlist()"}, headers=ua, verify=False, timeout=15)
            cl = (json.loads(c.text) or {}).get("get_clientlist", {})
            out["clients"] = {
                k.upper(): {
                    "ip": v.get("ip"),
                    "name": v.get("nickName") or v.get("name"),
                    "online": v.get("isOnline"),
                    "wl": v.get("isWL"),
                }
                for k, v in cl.items()
                if isinstance(v, dict) and ":" in k
            }
        if new_list is not None:
            a = s.post(
                base + "/applyapp.cgi",
                headers=ua,
                verify=False,
                timeout=15,
                data={
                    "action_mode": "apply",
                    "rc_service": "restart_dnsmasq",
                    "dhcp_static_x": "1",
                    "dhcp_staticlist": new_list,
                },
            )
            out["apply_status"] = a.status_code
            out["apply_reply"] = a.text[:200]
            g2 = s.get(
                base + "/appGet.cgi",
                params={"hook": "nvram_get(dhcp_staticlist)"},
                headers=ua,
                verify=False,
                timeout=10,
            )
            out["after"] = _dec(json.loads(g2.text).get("dhcp_staticlist") or "")
    finally:
        try:
            s.get(base + "/Logout.asp", headers=ua, verify=False, timeout=5)
        except Exception:
            pass
    return out


def parse_staticlist(raw: str | None) -> list[dict[str, Any]]:
    items = []
    for chunk in (raw or "").split("<"):
        if not chunk:
            continue
        f = chunk.split(">")
        items.append({"mac": f[0].upper(), "ip": f[1] if len(f) > 1 else "", "rest": f[2:]})
    return items


def build_staticlist(items: list[dict[str, Any]]) -> str:
    return "".join("<" + ">".join([i["mac"], i["ip"]] + list(i["rest"])) for i in items)


def plan_reservations(
    existing: list[dict[str, Any]],
    wanted: dict[str, tuple[str, str]],
    template_rest: list[str],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    def ipn(ip: str) -> int:
        try:
            a = [int(x) for x in ip.split(".")]
            return a[0] << 24 | a[1] << 16 | a[2] << 8 | a[3]
        except Exception:
            return 0

    by_mac = {e["mac"]: e for e in existing}
    by_ip = {e["ip"]: e for e in existing}
    to_add, conflicts, already = [], [], []
    for mac, (ip, name) in sorted(wanted.items(), key=lambda kv: ipn(kv[1][0])):
        if mac in by_mac:
            if by_mac[mac]["ip"] == ip:
                already.append(name)
            else:
                conflicts.append(f"{name} {mac}: router reserves {by_mac[mac]['ip']}, device uses {ip}")
            continue
        if ip in by_ip:
            conflicts.append(f"{name} {mac}: {ip} already reserved for {by_ip[ip]['mac']}")
            continue
        rest = [x if x != "__NAME__" else name.replace(" ", "_")[:32] for x in template_rest]
        to_add.append({"mac": mac, "ip": ip, "rest": rest, "name": name})
    return to_add, conflicts, already


# ---------------------------------------------------------------------------
# Gen1 / Gen2+ Restore, Hardening & Classification
# ---------------------------------------------------------------------------

GEN1_ROOT_KEYS = [
    "name", "discoverable", "led_status_disable", "led_power_disable",
    "sntp_server", "tzautodetect", "timezone", "lat", "lng",
    "max_power", "eco_mode_enabled", "longpush_time", "multipush_time",
    "coiot_enable", "coiot_update_period", "coiot_peer",
    "mqtt_enable", "mqtt_server", "mqtt_user", "mqtt_id", "mqtt_clean_session",
    "mqtt_retain", "mqtt_qos", "mqtt_keep_alive", "mqtt_update_period",
    "mqtt_reconnect_timeout_max", "mqtt_reconnect_timeout_min",
    "cloud_enabled", "wifirecovery_reboot_enabled", "allow_cross_modes",
    "transition", "night_mode_enabled", "allow_cross_origin",
    "longpush_duration_ms", "multipush_time_between_pushes_ms", "favorites_enabled", "dcpower",
]

GEN1_SECTION_KEYS = {
    "relays": ("/settings/relay/{i}", [
        "name", "appliance_type", "default_state", "btn_type", "btn_reverse",
        "btn1_type", "btn1_reverse", "btn2_type", "btn2_reverse", "swap_inputs",
        "auto_on", "auto_off", "max_power", "schedule", "schedule_rules",
    ]),
    "rollers": ("/settings/roller/{i}", [
        "maxtime", "maxtime_open", "maxtime_close", "default_state", "swap",
        "swap_inputs", "input_mode", "button_type", "btn_reverse",
        "safety_switch", "safety_mode", "safety_action", "safety_allowed_on_trigger",
        "off_power", "obstacle_mode", "obstacle_action", "obstacle_power",
        "obstacle_delay", "favorites_enabled", "ends_delay", "schedule", "schedule_rules",
    ]),
    "lights": ("/settings/light/{i}", [
        "name", "default_state", "auto_on", "auto_off", "btn_type", "btn_reverse",
        "schedule", "schedule_rules", "transition",
    ]),
    "emeters": ("/settings/emeter/{i}", ["name", "appliance_type", "ctraf_type", "max_power", "range_extender"]),
    "inputs": ("/settings/input/{i}", ["name", "btn_type", "btn_reverse"]),
}

GEN2_NS = {
    "sys": "Sys", "switch": "Switch", "input": "Input", "cover": "Cover", "light": "Light",
    "rgb": "RGB", "rgbw": "RGBW", "cct": "CCT", "em": "EM", "em1": "EM1", "emdata": "EMData",
    "em1data": "EM1Data", "pm1": "PM1", "temperature": "Temperature", "humidity": "Humidity",
    "voltmeter": "Voltmeter", "cloud": "Cloud", "mqtt": "MQTT", "ble": "BLE", "ws": "WS",
    "ui": "UI", "plugs_ui": "PLUGS_UI", "knx": "KNX", "illuminance": "Illuminance",
    "devicepower": "DevicePower", "smoke": "Smoke", "modbus": "Modbus", "pro_output_add_on": None,
}

GEN2_SKIP = {
    "wifi", "eth", "matter", "zigbee", "bthome", "bthomedevice", "bthomesensor",
    "bthomecontrol", "blugw", "script", "schedule", "webhook", "kvs", "service",
    "ht_ui", "wd", "sensoraddon",
}

VIRTUAL_TYPES = {"boolean", "number", "text", "enum", "button", "group", "object"}

SYS_ALLOWED = {
    "device": ["name", "eco_mode", "discoverable"],
    "location": ["tz", "lat", "lon"],
    "sntp": ["server"],
    "rpc_udp": ["dst_addr", "listen_port"],
    "debug": [],
}


def _gen1_val(v: Any) -> Any:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return ",".join(str(x) for x in v)
    return v


def gen1_restore_plan(settings: dict[str, Any], actions: dict[str, Any] | None = None) -> list[tuple[str, dict[str, Any]]]:
    plan: list[tuple[str, dict[str, Any]]] = []
    if settings.get("mode"):
        plan.append(("/settings", {"mode": settings["mode"]}))
    root: dict[str, Any] = {}
    for k in GEN1_ROOT_KEYS:
        v = settings.get(k)
        if v is not None:
            root[k] = _gen1_val(v)
    mq = settings.get("mqtt") or {}
    for src, dst in [
        ("enable", "mqtt_enable"), ("server", "mqtt_server"), ("user", "mqtt_user"),
        ("id", "mqtt_id"), ("clean_session", "mqtt_clean_session"),
        ("retain", "mqtt_retain"), ("max_qos", "mqtt_max_qos"),
        ("keep_alive", "mqtt_keep_alive"), ("update_period", "mqtt_update_period"),
        ("reconnect_timeout_max", "mqtt_reconnect_timeout_max"),
        ("reconnect_timeout_min", "mqtt_reconnect_timeout_min"),
    ]:
        if mq.get(src) is not None:
            root[dst] = _gen1_val(mq[src])
    co = settings.get("coiot") or {}
    if co.get("enabled") is not None:
        root["coiot_enable"] = _gen1_val(co["enabled"])
    if co.get("update_period") is not None:
        root["coiot_update_period"] = co["update_period"]
    if co.get("peer"):
        root["coiot_peer"] = co["peer"]
    sn = settings.get("sntp") or {}
    if sn.get("server"):
        root["sntp_server"] = sn["server"]
    cloud = settings.get("cloud") or {}
    if cloud.get("enabled") is not None:
        root["cloud_enabled"] = _gen1_val(cloud["enabled"])
    root["factory_reset_from_switch"] = "false"
    if "pon_wifi_reset" in settings:
        root["pon_wifi_reset"] = "false"
    plan.append(("/settings", root))

    for section, (path, keys) in GEN1_SECTION_KEYS.items():
        for i, item in enumerate(settings.get(section) or []):
            params = {k: _gen1_val(item[k]) for k in keys if k in item and item[k] is not None}
            if params:
                plan.append((path.format(i=i), params))

    for name, entries in ((actions or {}).get("actions") or {}).items():
        for e in entries:
            p: dict[str, Any] = {
                "index": e.get("index", 0),
                "name": name,
                "enabled": _gen1_val(bool(e.get("enabled"))),
            }
            urls = e.get("urls") or []
            if urls and isinstance(urls[0], dict):
                urls = [u.get("url") for u in urls if u.get("url")]
            p["urls[]"] = urls
            if urls or e.get("enabled"):
                plan.append(("/settings/actions", p))
    return plan


def gen2_restore_plan(backup: dict[str, Any]) -> list[tuple[str, Any]]:
    cfg = backup.get("config") or {}
    head: list[tuple[str, Any]] = []
    prof = backup.get("profile")
    if prof:
        head.append(("Shelly.SetProfile", {"name": prof}))

    sysc = cfg.get("sys") or {}
    sys_new: dict[str, Any] = {}
    for sect, keys in SYS_ALLOWED.items():
        src = sysc.get(sect) or {}
        part = {k: src[k] for k in keys if k in src}
        if part:
            sys_new[sect] = part
    if sys_new:
        head.append(("Sys.SetConfig", {"config": sys_new}))

    virtuals: list[tuple[str, Any]] = []
    comps: list[tuple[str, Any]] = []
    for key, comp in sorted(cfg.items()):
        prefix, _, idx = key.partition(":")
        if prefix == "sys" or prefix in GEN2_SKIP or not isinstance(comp, dict):
            continue
        c = dict(comp)
        c.pop("id", None)
        if prefix == "input":
            c["factory_reset"] = False
        if prefix in VIRTUAL_TYPES and idx.isdigit() and int(idx) >= 200:
            virtuals.append(("Virtual.Add", {"type": prefix, "id": int(idx), "config": c}))
            continue
        if prefix == "mqtt":
            c.pop("pass", None)
        ns = GEN2_NS.get(prefix, prefix.capitalize())
        if ns is None:
            continue
        params: dict[str, Any] = {"config": c}
        if idx.isdigit():
            params["id"] = int(idx)
        comps.append((f"{ns}.SetConfig", params))
    plan = head + virtuals + comps

    for s in backup.get("scripts") or []:
        if str(s.get("name", "")).startswith("aioshelly"):
            continue
        plan.append(("__script__", s))
    sched = backup.get("schedules") or []
    if sched:
        plan.append(("Schedule.DeleteAll", {}))
        for j in sched:
            j = dict(j)
            j.pop("id", None)
            plan.append(("Schedule.Create", j))
    for h in backup.get("webhooks") or []:
        if str(h.get("name", "")).startswith("ha_"):
            continue
        h = dict(h)
        h.pop("id", None)
        plan.append(("Webhook.Create", h))
    for k, v in (backup.get("kvs") or {}).items():
        if k == MARKER_KEY:
            continue
        plan.append(("KVS.Set", {"key": k, "value": v.get("value") if isinstance(v, dict) else v}))
    return plan


def match_reset_aps(
    offline: dict[str, dict[str, Any]],
    scans: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for mac in offline:
        tail6, full = mac[-6:].upper(), mac.upper()
        for scanner, results in scans.items():
            for r in results or []:
                ssid = str(r.get("ssid") or "")
                up = ssid.upper()
                if not up.startswith("SHELLY") or not (up.endswith(full) or up.endswith(tail6)):
                    continue
                rssi = r.get("rssi", -999)
                if mac not in found or rssi > found[mac]["rssi"]:
                    found[mac] = {"ssid": ssid, "near": scanner, "rssi": rssi}
    return found


def reset_by_input_enabled(payload: dict[str, Any]) -> bool:
    c = payload["config"]
    if payload["gen"] == 1:
        st = c.get("settings") or {}
        return bool(st.get("factory_reset_from_switch") or st.get("pon_wifi_reset"))
    return any(
        k.startswith("input:") and isinstance(v, dict) and v.get("factory_reset")
        for k, v in (c.get("config") or {}).items()
    )


def gen1_looks_factory(settings: dict[str, Any], backup_settings: dict[str, Any] | None) -> bool:
    if not backup_settings:
        return False
    return bool(backup_settings.get("name")) and not settings.get("name")


def gen2_looks_factory(cfg: dict[str, Any], backup: dict[str, Any] | None) -> bool:
    if not backup:
        return False
    had_name = ((backup.get("config") or {}).get("sys") or {}).get("device", {}).get("name")
    now_name = ((cfg or {}).get("sys") or {}).get("device", {}).get("name")
    return bool(had_name) and not now_name


def classify_config(
    dev: dict[str, Any],
    cur: dict[str, Any] | None = None,
    backup: dict[str, Any] | None = None,
) -> str:
    src = cur or backup
    gen = dev.get("gen") or (src and src.get("gen")) or 1
    port = int(dev.get("port") or 80)
    parts = [f"Gen{gen}"]
    if port != 80:
        parts.append("Range Extender")
    elif src:
        if gen == 1:
            parts.append("Wi-Fi")
        else:
            c = (src.get("config") or {}).get("config") or {}
            eth = c.get("eth") or {}
            re_on = (((c.get("wifi") or {}).get("ap") or {}).get("range_extender") or {}).get("enable")
            parts.append("Ethernet" if eth.get("enable") else "Wi-Fi")
            if re_on:
                parts.append("RE Host")
    if src:
        if gen == 1:
            st = (src.get("config") or {}).get("settings") or {}
            m = (st.get("wifi_sta") or {}).get("ipv4_method")
            if m:
                parts.append("Estático" if m == "static" else "DHCP")
        else:
            c = (src.get("config") or {}).get("config") or {}
            eth = c.get("eth") or {}
            sta = (c.get("wifi") or {}).get("sta") or {}
            m = eth.get("ipv4mode") if eth.get("enable") else sta.get("ipv4mode")
            if m:
                parts.append("Estático" if m == "static" else "DHCP")
    return " · ".join(parts)


def extract_fw(
    dev: dict[str, Any],
    cur: dict[str, Any] | None = None,
    backup: dict[str, Any] | None = None,
) -> str:
    src = cur or backup
    if src:
        if src.get("fw"):
            return short_fw(src["fw"])
        if src.get("gen") == 1:
            st = (src.get("config") or {}).get("settings") or {}
            if st.get("fw"):
                return short_fw(st["fw"])
    return short_fw(dev.get("sw_version"))


def build_device_row(
    mac: str,
    dev: dict[str, Any],
    cur: dict[str, Any] | None = None,
    backup: dict[str, Any] | None = None,
    online: bool = True,
    reset: bool = False,
    err: str = "",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bk = backup or cur
    m = meta or {}
    w = compute_warranty(m)
    return {
        "mac": mac,
        "name": dev.get("name") or m.get("last_name") or mac,
        "area": dev.get("area") or m.get("last_area") or "",
        "host": dev.get("host") or m.get("last_host") or "",
        "port": int(dev.get("port") or m.get("last_port") or 80),
        "gen": int(dev.get("gen") or m.get("last_gen") or 1),
        "model": dev.get("model") or m.get("last_model") or "",
        "online": bool(online),
        "reset": bool(reset),
        "has_backup": bool(bk and bk.get("saved_at")),
        "backup_at": (bk or {}).get("saved_at") or "",
        "config_type": classify_config(dev, cur, backup),
        "fw": extract_fw(dev, cur, backup),
        "update_entity": dev.get("update_entity") or "",
        "hardened": (not reset_by_input_enabled(cur)) if cur else None,
        "checked_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "error": str(err)[:120] if err else "",
        "lifecycle": m.get("lifecycle") or "active",
        "faulty_at": m.get("faulty_at") or "",
        "faulty_reason": m.get("faulty_reason") or "",
        "replaced_by": m.get("replaced_by") or "",
        "replaced_at": m.get("replaced_at") or "",
        "vendor": m.get("vendor") or "",
        "invoice_number": m.get("invoice_number") or "",
        "notes": m.get("notes") or "",
        **w,
    }


def fetch_device(dev: dict[str, Any], default_user: str = "admin", default_pass: str = "") -> dict[str, Any]:
    host, gen = dev_addr(dev), int(dev["gen"])
    u = dev.get("user") or default_user
    p = dev.get("password") or default_pass
    if gen == 1:
        settings = gen1_get(host, "/settings", user=u, password=p)
        try:
            actions = gen1_get(host, "/settings/actions", user=u, password=p)
        except Exception:
            actions = None
        cfg: dict[str, Any] = {"settings": settings, "actions": actions}
        fw = settings.get("fw") or dev.get("sw_version")
    else:
        conf = rpc(host, "Shelly.GetConfig", user=u, password=p)
        info = rpc(host, "Shelly.GetDeviceInfo", user=u, password=p) or {}
        fw = info.get("ver") or info.get("fw_id") or dev.get("sw_version")
        scripts = []
        try:
            for s in (rpc(host, "Script.List", user=u, password=p) or {}).get("scripts", []):
                code, offset = "", 0
                while True:
                    r = rpc(
                        host,
                        "Script.GetCode",
                        {"id": s["id"], "offset": offset, "len": 2048},
                        user=u,
                        password=p,
                    )
                    chunk = r.get("data", "")
                    code += chunk
                    offset += len(chunk)
                    if not chunk or r.get("left", 0) == 0:
                        break
                s["code"] = code
                scripts.append(s)
        except Exception:
            pass
        schedules, webhooks, kvs = [], [], {}
        try:
            schedules = (rpc(host, "Schedule.List", user=u, password=p) or {}).get("jobs", [])
        except Exception:
            pass
        try:
            webhooks = (rpc(host, "Webhook.List", user=u, password=p) or {}).get("hooks", [])
        except Exception:
            pass
        try:
            raw_kvs = (rpc(host, "KVS.GetMany", {"match": "*"}, user=u, password=p) or {}).get("items", {})
            if isinstance(raw_kvs, list):
                kvs = {i["key"]: {"value": i.get("value")} for i in raw_kvs}
            else:
                kvs = raw_kvs
        except Exception:
            pass
        cfg = {
            "config": conf,
            "profile": info.get("profile"),
            "scripts": scripts,
            "schedules": schedules,
            "webhooks": webhooks,
            "kvs": kvs,
        }
    return {
        "mac": dev["mac"],
        "gen": gen,
        "name": dev["name"],
        "area": dev.get("area"),
        "model": dev.get("model"),
        "host": dev["host"],
        "port": int(dev.get("port") or 80),
        "fw": fw,
        "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "config": cfg,
    }


def harden_device(
    dev: dict[str, Any],
    current: dict[str, Any],
    default_user: str = "admin",
    default_pass: str = "",
) -> list[Any]:
    host, gen, changes = dev_addr(dev), int(dev["gen"]), []
    u = dev.get("user") or default_user
    p = dev.get("password") or default_pass
    if gen == 1:
        s = current["config"]["settings"]
        params: dict[str, Any] = {}
        if s.get("factory_reset_from_switch"):
            params["factory_reset_from_switch"] = "false"
        if s.get("pon_wifi_reset"):
            params["pon_wifi_reset"] = "false"
        if not s.get("name") and dev["name"]:
            params["name"] = dev["name"]
        if params:
            gen1_get(host, "/settings", params, user=u, password=p)
            changes.append(params)
    else:
        conf = current["config"]["config"]
        for key, comp in conf.items():
            if key.startswith("input:") and isinstance(comp, dict) and comp.get("factory_reset"):
                rpc(
                    host,
                    "Input.SetConfig",
                    {"id": int(key.split(":")[1]), "config": {"factory_reset": False}},
                    user=u,
                    password=p,
                )
                changes.append(f"{key}.factory_reset=false")
        if not ((conf.get("sys") or {}).get("device") or {}).get("name") and dev["name"]:
            rpc(host, "Sys.SetConfig", {"config": {"device": {"name": dev["name"]}}}, user=u, password=p)
            changes.append("name")
        if MARKER_KEY not in (current["config"].get("kvs") or {}):
            rpc(host, "KVS.Set", {"key": MARKER_KEY, "value": current["saved_at"]}, user=u, password=p)
            changes.append("marker")
    return changes


def restore_device(
    dev: dict[str, Any],
    backup: dict[str, Any],
    dry_run: bool = True,
    default_user: str = "admin",
    default_pass: str = "",
    wifi_secrets_file: str = "",
    wifi_password: str = "",
) -> tuple[list[str], list[str]]:
    host, gen = dev_addr(dev), int(backup["gen"])
    u = dev.get("user") or default_user
    p = dev.get("password") or default_pass
    done: list[str] = []
    failed: list[str] = []

    if gen == 1:
        plan = gen1_restore_plan(backup["config"]["settings"], backup["config"].get("actions"))
        for path, params in plan:
            if dry_run:
                done.append(f"GET {path} {params}")
                continue
            try:
                gen1_get(host, path, params, user=u, password=p)
                done.append(path)
                if "mode" in params and len(params) == 1:
                    time.sleep(3)
            except Exception as e:
                failed.append(f"{path}: {e}")
        if not dry_run and p:
            try:
                gen1_get(host, "/settings/login", {"enabled": "true", "username": u, "password": p}, user=u, password=p)
                done.append("auth")
            except Exception as e:
                failed.append(f"auth: {e}")
        sta = backup["config"]["settings"].get("wifi_sta") or {}
        if not dry_run and done:
            try:
                gen1_get(host, "/reboot", user=u, password=p)
                done.append("reboot")
                time.sleep(25)
            except Exception as e:
                failed.append(f"reboot: {e}")
        if sta.get("ipv4_method") == "static" and sta.get("ip"):
            home_ssid, wpass = wifi_creds(wifi_secrets_file, fallback_pass=wifi_password)
            if not wpass:
                failed.append(f"static IP {sta['ip']} not set: no Wi-Fi password configured")
            elif dry_run:
                done.append(f"GET /settings/sta static {sta['ip']}")
            else:
                try:
                    gen1_get(
                        host,
                        "/settings/sta",
                        {
                            "enabled": "true",
                            "ssid": sta.get("ssid") or home_ssid,
                            "key": wpass,
                            "ipv4_method": "static",
                            "ip": sta["ip"],
                            "netmask": sta.get("mask"),
                            "gateway": sta.get("gw"),
                            "dns": sta.get("dns"),
                        },
                        user=u,
                        password=p,
                    )
                    done.append(f"static IP {sta['ip']}")
                except Exception as e:
                    failed.append(f"static IP: {e}")
        rollers = backup["config"]["settings"].get("rollers") or []
        if not dry_run and any(r.get("positioning") for r in rollers):
            failed.append("roller: needs recalibration (/roller/0/calibrate)")
        return done, failed

    plan2 = gen2_restore_plan(backup["config"])
    need_reboot = False
    existing_scripts: dict[str, int] = {}
    existing_hooks: list[dict[str, Any]] = []
    if not dry_run:
        try:
            for s0 in (rpc(host, "Script.List", user=u, password=p) or {}).get("scripts", []):
                existing_scripts[s0.get("name")] = s0["id"]
        except Exception:
            pass
        try:
            existing_hooks = (rpc(host, "Webhook.List", user=u, password=p) or {}).get("hooks", [])
        except Exception:
            pass
    for method, params in plan2:
        if dry_run:
            done.append(f"{method} {json.dumps(params)[:160]}")
            continue
        try:
            if method == "Shelly.SetProfile":
                cur = (rpc(host, "Shelly.GetDeviceInfo", user=u, password=p) or {}).get("profile")
                if cur and cur != params["name"]:
                    rpc(host, method, params, user=u, password=p)
                    time.sleep(25)
            elif method == "__script__":
                s = params
                sid = existing_scripts.get(s.get("name"))
                if sid is None:
                    sid = rpc(host, "Script.Create", {"name": s.get("name")}, user=u, password=p)["id"]
                else:
                    try:
                        rpc(host, "Script.Stop", {"id": sid}, user=u, password=p)
                    except Exception:
                        pass
                code = s.get("code", "")
                for i in range(0, max(len(code), 1), 1024):
                    rpc(
                        host,
                        "Script.PutCode",
                        {"id": sid, "code": code[i : i + 1024], "append": i > 0},
                        user=u,
                        password=p,
                    )
                rpc(host, "Script.SetConfig", {"id": sid, "config": {"enable": bool(s.get("enable"))}}, user=u, password=p)
                if s.get("running"):
                    rpc(host, "Script.Start", {"id": sid}, user=u, password=p)
            elif method == "Webhook.Create" and any(
                h.get("name") == params.get("name")
                and h.get("event") == params.get("event")
                and h.get("cid") == params.get("cid")
                for h in existing_hooks
            ):
                done.append("Webhook exists: " + str(params.get("name")))
                continue
            else:
                res = rpc(host, method, params, user=u, password=p)
                if isinstance(res, dict) and res.get("restart_required"):
                    need_reboot = True
            done.append(method)
        except Exception as e:
            failed.append(f"{method}: {e}")
    if not dry_run and need_reboot:
        try:
            rpc(host, "Shelly.Reboot", user=u, password=p)
            time.sleep(20)
        except Exception as e:
            failed.append(f"reboot: {e}")
    sta2 = ((backup["config"].get("config") or {}).get("wifi") or {}).get("sta") or {}
    if sta2.get("ipv4mode") == "static" and sta2.get("ip"):
        cfg_ip = {
            "sta": {
                "ipv4mode": "static",
                "ip": sta2["ip"],
                "netmask": sta2.get("netmask"),
                "gw": sta2.get("gw"),
                "nameserver": sta2.get("nameserver"),
            }
        }
        if dry_run:
            done.append(f"WiFi.SetConfig static {sta2['ip']}")
        else:
            try:
                rpc(host, "WiFi.SetConfig", {"config": cfg_ip}, user=u, password=p)
                done.append(f"static IP {sta2['ip']}")
            except Exception as e:
                failed.append(f"static IP: {e}")
    if not dry_run and p:
        try:
            dev_id = (rpc(host, "Shelly.GetDeviceInfo", user=u, password=p) or {}).get("id")
            ha1 = hashlib.sha256(f"admin:{dev_id}:{p}".encode()).hexdigest()
            rpc(host, "Shelly.SetAuth", {"user": "admin", "realm": dev_id, "ha1": ha1}, user=u, password=p)
            done.append("auth")
        except Exception as e:
            failed.append(f"auth: {e}")
    if not dry_run:
        try:
            rpc(host, "KVS.Set", {"key": MARKER_KEY, "value": "restored " + backup["saved_at"]}, user=u, password=p)
        except Exception:
            pass
        if any(k.startswith("cover:") for k in (backup["config"].get("config") or {})):
            failed.append("cover: run calibration in HA/web UI (Cover.Calibrate)")
    return done, failed
