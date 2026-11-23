"""
shelly_guard — backup, hardening, auto-restore and NetAlertX naming for Shelly devices.

Runs inside Home Assistant via pyscript (needs `allow_all_imports: true` and
`hass_is_global: true`). Network/file work runs in executor threads
(@pyscript_executor), so nothing blocks the HA event loop.

Services:
  pyscript.shelly_guard_backup_all       backup every Shelly known to HA
  pyscript.shelly_guard_check            harden + detect factory-reset devices (+ auto-restore)
  pyscript.shelly_guard_restore          restore one device: mac=..., [host=...], dry_run=true|false
  pyscript.shelly_guard_harden_all       disable "factory reset from switch/input" everywhere
  pyscript.shelly_guard_sync_netalertx   push HA names/areas to NetAlertX

State: sensor.shelly_guard  (attributes: last_backup, devices, offline, reset_detected, restored, errors)
"""

import json
import os
import time
import hashlib
import datetime

APP = "shelly_guard"
try:
    CFG = pyscript.app_config or {}
except Exception:
    CFG = {}

BACKUP_DIR = CFG.get("backup_dir", "/share/shelly_guard")
STATE_FILE = CFG.get("state_file", "/config/www/shelly_guard_state.json")
KEEP_VERSIONS = int(CFG.get("keep_versions", 15))
AUTO_RESTORE = bool(CFG.get("auto_restore", True))
HARDEN = bool(CFG.get("harden", True))
NOTIFY = CFG.get("notify_service", "")            # e.g. notify.mobile_app_your_phone
NOTIFY_DATA = CFG.get("notify_data", {})
NAX_URL = CFG.get("netalertx_url", "")            # e.g. http://192.168.1.10:20212
NAX_TOKEN = CFG.get("netalertx_token", "")
SHELLY_USER = CFG.get("shelly_user", "admin")
SHELLY_PASS = CFG.get("shelly_password", "")      # only if devices have auth enabled
WIFI_PASS = CFG.get("wifi_password", "")          # needed to put back a Gen1 static IP
WIFI_SECRETS = CFG.get("wifi_secrets_file", "/config/esphome/secrets.yaml")
WIFI_SSID_KEY = CFG.get("wifi_ssid_key", "conf_ssid")
WIFI_PASS_KEY = CFG.get("wifi_password_key", "conf_ssidpass")
MARKER_KEY = "shelly_guard"                       # KVS key written on Gen2+ devices
HTTP_TIMEOUT = 8

# ---------------------------------------------------------------------------
# Native helpers (executor threads)
# ---------------------------------------------------------------------------

@pyscript_executor
def _resolve_dir(preferred, fallback="/share/shelly_guard"):
    for d in (preferred, fallback):
        try:
            os.makedirs(d, exist_ok=True)
            probe = os.path.join(d, ".write_test")
            with open(probe, "w") as f:
                f.write("ok")
            os.remove(probe)
            return d
        except Exception:
            continue
    return fallback


@pyscript_executor
def _rpc(host, method, params=None, timeout=HTTP_TIMEOUT, user="admin", password=""):
    """Gen2+ JSON-RPC over HTTP POST /rpc."""
    import requests
    body = {"id": 1, "method": method}
    if params is not None:
        body["params"] = params
    auth = requests.auth.HTTPDigestAuth(user, password) if password else None
    r = requests.post(f"http://{host}/rpc", json=body, timeout=timeout, auth=auth)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"{method}: {data['error']}")
    return data.get("result")


@pyscript_executor
def _wifi_creds(path, ssid_key, pass_key, fallback_pass=""):
    """Home Wi-Fi credentials from the ESPHome secrets file (read only when restoring)."""
    try:
        import yaml
        with open(path) as f:
            sec = yaml.safe_load(f) or {}
        return sec.get(ssid_key), sec.get(pass_key) or fallback_pass
    except Exception:
        return None, fallback_pass


@pyscript_executor
def _asus_dhcp(base, user, password, new_list=None, clients=False):
    """Read (and optionally write) the ASUS DHCP static list through the router's web API,
    the same API the AsusRouter integration uses. Returns dict with raw list and pool."""
    import base64
    import requests
    import urllib3
    urllib3.disable_warnings()
    ua = {"User-Agent": "asusrouter--DUTUtil-", "Referer": base + "/"}
    s = requests.Session()
    r = s.post(base + "/login.cgi", headers=ua, verify=False, timeout=10,
               data={"login_authorization": base64.b64encode(f"{user}:{password}".encode()).decode()})
    tok = (r.json() if r.headers.get("content-type", "").startswith("application/json") or r.text.startswith("{") else {}).get("asus_token")
    if not tok:
        return {"error": f"login failed ({r.status_code})"}
    s.cookies.set("asus_token", tok)
    out = {}
    try:
        q = "nvram_get(dhcp_staticlist);nvram_get(dhcp_start);nvram_get(dhcp_end);nvram_get(dhcp_static_x);nvram_get(dhcp_hostnames);nvram_get(productid);nvram_get(firmver);nvram_get(buildno)"
        g = s.get(base + "/appGet.cgi", params={"hook": q}, headers=ua, verify=False, timeout=10)
        import json as _j
        import html as _h
        import re as _re

        def _dec(v):
            # the router entity-encodes '<' and '>' (sometimes without the ';')
            v = _re.sub(r"&#(60|62);?", lambda m: "<" if m.group(1) == "60" else ">", v)
            return _h.unescape(v)
        out = {k: (_dec(v) if isinstance(v, str) else v) for k, v in _j.loads(g.text).items()}
        if clients:
            c = s.get(base + "/appGet.cgi", params={"hook": "get_clientlist()"}, headers=ua, verify=False, timeout=15)
            cl = (_j.loads(c.text) or {}).get("get_clientlist", {})
            out["clients"] = {k.upper(): {"ip": v.get("ip"), "name": v.get("nickName") or v.get("name"),
                                          "online": v.get("isOnline"), "wl": v.get("isWL")}
                              for k, v in cl.items() if isinstance(v, dict) and ":" in k}
        if new_list is not None:
            a = s.post(base + "/applyapp.cgi", headers=ua, verify=False, timeout=15, data={
                "action_mode": "apply", "rc_service": "restart_dnsmasq",
                "dhcp_static_x": "1", "dhcp_staticlist": new_list})
            out["apply_status"] = a.status_code
            out["apply_reply"] = a.text[:200]
            g2 = s.get(base + "/appGet.cgi", params={"hook": "nvram_get(dhcp_staticlist)"},
                       headers=ua, verify=False, timeout=10)
            out["after"] = _dec(_j.loads(g2.text).get("dhcp_staticlist") or "")
    finally:
        try:
            s.get(base + "/Logout.asp", headers=ua, verify=False, timeout=5)
        except Exception:
            pass
    return out


@pyscript_compile
def parse_staticlist(raw):
    """'<MAC>IP>DNS>HOST<MAC>IP>>HOST...' -> list of dicts (keeps unknown trailing fields)."""
    items = []
    for chunk in (raw or "").split("<"):
        if not chunk:
            continue
        f = chunk.split(">")
        items.append({"mac": f[0].upper(), "ip": f[1] if len(f) > 1 else "", "rest": f[2:]})
    return items


@pyscript_compile
def build_staticlist(items):
    return "".join("<" + ">".join([i["mac"], i["ip"]] + list(i["rest"])) for i in items)


@pyscript_compile
def plan_reservations(existing, wanted, pool_start, pool_end, template_rest):
    """existing: parsed list; wanted: {MAC: (ip, name)}. Returns (to_add, conflicts, already)."""
    def ipn(ip):
        try:
            a = [int(x) for x in ip.split(".")]
            return a[0] << 24 | a[1] << 16 | a[2] << 8 | a[3]
        except Exception:
            return None
    by_mac = {e["mac"]: e for e in existing}
    by_ip = {e["ip"]: e for e in existing}
    to_add, conflicts, already = [], [], []
    for mac, (ip, name) in sorted(wanted.items(), key=lambda kv: ipn(kv[1][0]) or 0):
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


@pyscript_executor
def _wifi_scan(host, user="admin", password="", hard_timeout=30):
    """WiFi.Scan with a hard wall-clock limit (some firmwares stall the HTTP reply)."""
    import threading
    import requests
    box = {}

    def worker():
        try:
            auth = requests.auth.HTTPDigestAuth(user, password) if password else None
            r = requests.post(f"http://{host}/rpc", json={"id": 1, "method": "WiFi.Scan"},
                              timeout=(4, 20), auth=auth)
            box["res"] = (r.json().get("result") or {}).get("results", [])
        except Exception as e:
            box["err"] = f"{type(e).__name__}: {e}"

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(hard_timeout)
    if t.is_alive():
        return None, "hard timeout"
    return box.get("res"), box.get("err")


@pyscript_executor
def _gen1_get(host, path, params=None, timeout=HTTP_TIMEOUT, user="admin", password=""):
    import requests
    auth = (user, password) if password else None
    r = requests.get(f"http://{host}{path}", params=params, timeout=timeout, auth=auth)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return r.text


@pyscript_executor
def _write_backup(backup_dir, mac, payload, keep):
    """Write latest.json; keep a dated copy only when content changed."""
    d = os.path.join(backup_dir, mac)
    os.makedirs(d, exist_ok=True)
    body = json.dumps(payload["config"], sort_keys=True)
    digest = hashlib.sha256(body.encode()).hexdigest()[:16]
    latest = os.path.join(d, "latest.json")
    old_digest = None
    if os.path.exists(latest):
        try:
            with open(latest) as f:
                old_digest = json.load(f).get("digest")
        except Exception:
            pass
    payload["digest"] = digest
    tmp = f"{latest}.{os.getpid()}.{time.time_ns()}.tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=1, sort_keys=True)
    os.replace(tmp, latest)
    changed = digest != old_digest
    if changed:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(d, f"{stamp}_{digest}.json"), "w") as f:
            json.dump(payload, f, indent=1, sort_keys=True)
        versions = sorted(x for x in os.listdir(d) if x[:2] == "20" and x.endswith(".json"))
        for old in versions[:-keep]:
            os.remove(os.path.join(d, old))
    return changed


@pyscript_executor
def _read_backup(backup_dir, mac):
    p = os.path.join(backup_dir, mac, "latest.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


@pyscript_executor
def _write_index(backup_dir, index):
    os.makedirs(backup_dir, exist_ok=True)
    with open(os.path.join(backup_dir, "index.json"), "w") as f:
        json.dump(index, f, indent=1, sort_keys=True)


@pyscript_executor
def _nax_update(url, token, mac, column, value):
    import requests
    r = requests.post(
        f"{url.rstrip('/')}/device/{mac}/update-column",
        headers={"Authorization": f"Bearer {token}"},
        json={"columnName": column, "columnValue": value},
        timeout=HTTP_TIMEOUT,
    )
    return r.status_code, r.text[:200]


# ---------------------------------------------------------------------------
# Pure logic (no I/O) — kept native so it can be unit-tested outside HA
# ---------------------------------------------------------------------------

@pyscript_compile
def norm_mac(mac):
    m = "".join(c for c in str(mac) if c.isalnum()).upper()
    return m if len(m) == 12 else None


@pyscript_compile
def colon_mac(mac):
    m = norm_mac(mac)
    return ":".join(m[i:i + 2] for i in range(0, 12, 2)).lower() if m else None


# Gen1 keys that may be written back, per settings section.
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
        "auto_on", "auto_off", "max_power", "schedule", "schedule_rules"]),
    "rollers": ("/settings/roller/{i}", [
        "maxtime", "maxtime_open", "maxtime_close", "default_state", "swap",
        "swap_inputs", "input_mode", "button_type", "btn_reverse",
        "safety_switch", "safety_mode", "safety_action", "safety_allowed_on_trigger",
        "off_power", "obstacle_mode", "obstacle_action", "obstacle_power",
        "obstacle_delay", "favorites_enabled", "ends_delay", "schedule", "schedule_rules"]),
    "lights": ("/settings/light/{i}", [
        "name", "default_state", "auto_on", "auto_off", "btn_type", "btn_reverse",
        "schedule", "schedule_rules", "transition"]),
    "emeters": ("/settings/emeter/{i}", ["name", "appliance_type", "ctraf_type", "max_power", "range_extender"]),
    "inputs": ("/settings/input/{i}", ["name", "btn_type", "btn_reverse"]),
}


@pyscript_compile
def _gen1_val(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return ",".join(str(x) for x in v)
    return v


@pyscript_compile
def gen1_restore_plan(settings, actions=None):
    """Return ordered list of (path, params) GETs that rebuild a Gen1 device."""
    plan = []
    # Mode first (Shelly 2.5 relay/roller, RGBW2 color/white) — it reshapes the rest.
    if settings.get("mode"):
        plan.append(("/settings", {"mode": settings["mode"]}))
    root = {}
    for k in GEN1_ROOT_KEYS:
        v = settings.get(k)
        if v is not None:
            root[k] = _gen1_val(v)
    # nested objects in /settings
    mq = settings.get("mqtt") or {}
    for src, dst in [("enable", "mqtt_enable"), ("server", "mqtt_server"), ("user", "mqtt_user"),
                     ("id", "mqtt_id"), ("clean_session", "mqtt_clean_session"),
                     ("retain", "mqtt_retain"), ("max_qos", "mqtt_max_qos"),
                     ("keep_alive", "mqtt_keep_alive"), ("update_period", "mqtt_update_period"),
                     ("reconnect_timeout_max", "mqtt_reconnect_timeout_max"),
                     ("reconnect_timeout_min", "mqtt_reconnect_timeout_min")]:
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
    led = settings.get("led_status_disable")
    if led is not None:
        root["led_status_disable"] = _gen1_val(led)
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

    # Gen1 "actions" (URLs called on button/output events)
    for name, entries in ((actions or {}).get("actions") or {}).items():
        for e in entries:
            p = {"index": e.get("index", 0), "name": name,
                 "enabled": _gen1_val(bool(e.get("enabled")))}
            urls = e.get("urls") or []
            if urls and isinstance(urls[0], dict):  # newer fw: [{"url":..,"int":..}]
                urls = [u.get("url") for u in urls if u.get("url")]
            p["urls[]"] = urls
            if urls or e.get("enabled"):
                plan.append(("/settings/actions", p))
    return plan


# Gen2+ component prefix -> RPC namespace. Unknown prefixes fall back to Capitalize.
GEN2_NS = {
    "sys": "Sys", "switch": "Switch", "input": "Input", "cover": "Cover", "light": "Light",
    "rgb": "RGB", "rgbw": "RGBW", "cct": "CCT", "em": "EM", "em1": "EM1", "emdata": "EMData",
    "em1data": "EM1Data", "pm1": "PM1", "temperature": "Temperature", "humidity": "Humidity",
    "voltmeter": "Voltmeter", "cloud": "Cloud", "mqtt": "MQTT", "ble": "BLE", "ws": "WS",
    "ui": "UI", "plugs_ui": "PLUGS_UI", "knx": "KNX", "illuminance": "Illuminance",
    "devicepower": "DevicePower", "smoke": "Smoke", "modbus": "Modbus", "pro_output_add_on": None,
}
# Never pushed back: connectivity is already working (HA provisioned it) or HA manages it.
GEN2_SKIP = {"wifi", "eth", "matter", "zigbee", "bthome", "bthomedevice", "bthomesensor",
             "bthomecontrol", "blugw", "script", "schedule", "webhook", "kvs", "service", "ht_ui",
             "wd", "sensoraddon"}
VIRTUAL_TYPES = {"boolean", "number", "text", "enum", "button", "group", "object"}
SYS_ALLOWED = {
    "device": ["name", "eco_mode", "discoverable"],
    "location": ["tz", "lat", "lon"],
    "sntp": ["server"],
    "rpc_udp": ["dst_addr", "listen_port"],
    "debug": [],
}


@pyscript_compile
def gen2_restore_plan(backup):
    """Return ordered list of (method, params) RPC calls rebuilding a Gen2+ device.

    backup = {"config": Shelly.GetConfig, "profile": str|None, "scripts": [...],
              "schedules": [...], "webhooks": [...], "kvs": {...}}
    """
    cfg = backup.get("config") or {}
    head = []
    prof = backup.get("profile")
    if prof:
        head.append(("Shelly.SetProfile", {"name": prof}))  # caller handles reboot

    sysc = cfg.get("sys") or {}
    sys_new = {}
    for sect, keys in SYS_ALLOWED.items():
        src = sysc.get(sect) or {}
        part = {k: src[k] for k in keys if k in src}
        if part:
            sys_new[sect] = part
    if sys_new:
        head.append(("Sys.SetConfig", {"config": sys_new}))

    virtuals, comps = [], []
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
        if prefix in ("mqtt",):
            c.pop("pass", None)
        ns = GEN2_NS.get(prefix, prefix.capitalize())
        if ns is None:
            continue
        params = {"config": c}
        if idx.isdigit():
            params["id"] = int(idx)
        comps.append((f"{ns}.SetConfig", params))
    plan = head + virtuals + comps

    for s in backup.get("scripts") or []:
        if str(s.get("name", "")).startswith("aioshelly"):
            continue  # HA reinstalls its own BLE proxy script
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
            continue  # HA recreates its own hooks
        h = dict(h)
        h.pop("id", None)
        plan.append(("Webhook.Create", h))
    for k, v in (backup.get("kvs") or {}).items():
        if k == MARKER_KEY:
            continue
        plan.append(("KVS.Set", {"key": k, "value": v.get("value") if isinstance(v, dict) else v}))
    return plan


@pyscript_compile
def match_reset_aps(offline, scans):
    """offline: {mac: {name, area, gen}}; scans: {scanner_name: [{ssid, rssi, ...}]}.
    A factory-reset Shelly broadcasts an open AP whose SSID ends with its MAC (Gen1 may use the
    last 6 hex digits). Returns {mac: {"ssid", "near", "rssi"}} with the strongest sighting."""
    found = {}
    for mac, dev in offline.items():
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


@pyscript_compile
def _reset_by_input_enabled(payload):
    c = payload["config"]
    if payload["gen"] == 1:
        st = c.get("settings") or {}
        return bool(st.get("factory_reset_from_switch") or st.get("pon_wifi_reset"))
    return any(k.startswith("input:") and isinstance(v, dict) and v.get("factory_reset")
               for k, v in (c.get("config") or {}).items())


@pyscript_compile
def gen1_looks_factory(settings, backup_settings):
    """Gen1: reset if the name is gone but we had one (we always set a name when hardening)."""
    if not backup_settings:
        return False
    had = backup_settings.get("name")
    now = settings.get("name")
    return bool(had) and not now


@pyscript_compile
def gen2_looks_factory(cfg, kvs_keys, backup):
    if not backup:
        return False
    had_name = ((backup.get("config") or {}).get("sys") or {}).get("device", {}).get("name")
    now_name = ((cfg or {}).get("sys") or {}).get("device", {}).get("name")
    return bool(had_name) and not now_name


# ---------------------------------------------------------------------------
# HA side: discover Shellys from config entries + device registry
# ---------------------------------------------------------------------------

@pyscript_compile
def _dev_addr(dev):
    h = dev["host"]
    p = int(dev.get("port") or 80)
    return f"{h}:{p}" if (p != 80 and ":" not in str(h)) else h


@pyscript_compile
def _short_fw(raw):
    s = str(raw or "").strip()
    if not s:
        return ""
    if "/" in s:
        s = s.split("/", 1)[1]
    for sep in ("-g", "@"):
        if sep in s:
            s = s.split(sep, 1)[0]
    return s


@pyscript_compile
def _classify_config(dev, cur=None, backup=None):
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
            if eth.get("enable"):
                parts.append("Ethernet")
            else:
                parts.append("Wi-Fi")
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


@pyscript_compile
def _extract_fw(dev, cur=None, backup=None):
    src = cur or backup
    if src:
        if src.get("fw"):
            return _short_fw(src["fw"])
        if src.get("gen") == 1:
            st = (src.get("config") or {}).get("settings") or {}
            if st.get("fw"):
                return _short_fw(st["fw"])
    return _short_fw(dev.get("sw_version"))


@pyscript_compile
def _build_device_row(mac, dev, cur=None, backup=None, online=True, reset=False, err=""):
    bk = backup or cur
    return {
        "mac": mac,
        "name": dev["name"],
        "area": dev.get("area") or "",
        "host": dev["host"],
        "port": int(dev.get("port") or 80),
        "gen": int(dev.get("gen") or 1),
        "model": dev.get("model") or "",
        "online": bool(online),
        "reset": bool(reset),
        "has_backup": bool(bk and bk.get("saved_at")),
        "backup_at": (bk or {}).get("saved_at") or "",
        "config_type": _classify_config(dev, cur, backup),
        "fw": _extract_fw(dev, cur, backup),
        "update_entity": dev.get("update_entity") or "",
        "hardened": (not _reset_by_input_enabled(cur)) if cur else None,
        "checked_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "error": str(err)[:120] if err else "",
    }


def _shelly_inventory():
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import area_registry as ar
    from homeassistant.helpers import entity_registry as er
    dreg = dr.async_get(hass)
    areg = ar.async_get(hass)
    ereg = er.async_get(hass)
    out = {}
    for entry in hass.config_entries.async_entries("shelly"):
        if entry.source == "ignore" or entry.disabled_by:
            continue
        host = entry.data.get("host")
        port = int(entry.data.get("port") or 80)
        gen = entry.data.get("gen") or 1
        mac = norm_mac(entry.unique_id or "")
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
            if dev.area_id and areg.async_get_area(dev.area_id):
                area = areg.async_get_area(dev.area_id).name
            break
        upd_eid = None
        for ent in er.async_entries_for_config_entry(ereg, entry.entry_id):
            if ent.entity_id.startswith("update.") and not ent.disabled_by and "beta" not in ent.entity_id:
                upd_eid = ent.entity_id
                break
        out[mac] = {"mac": mac, "host": host, "port": port, "gen": gen, "name": name, "area": area,
                    "model": model, "label": label, "sw_version": sw_ver, "update_entity": upd_eid,
                    "entry_id": entry.entry_id, "state": str(entry.state),
                    "user": entry.data.get("username") or SHELLY_USER,
                    "password": entry.data.get("password") or SHELLY_PASS}
    return out


def _notify(title, message):
    log.warning(f"[{APP}] {title}: {message}")
    if NOTIFY and "." in NOTIFY:
        dom, svc = NOTIFY.split(".", 1)
        try:
            service.call(dom, svc, title=title, message=message, data=NOTIFY_DATA)
        except Exception as e:
            log.error(f"[{APP}] notify failed: {e}")


SUSPECT = {}
OFFLINE_RUNS = {}      # mac -> consecutive checks offline
LAST_SCAN = {"t": 0}
NOTIFIED = {}          # mac -> ssid already reported for this incident
SCAN_EVERY = int(CFG.get("scan_every_min", 30)) * 60
DEVICE_TABLE = {}      # mac -> dashboard row dict
STATUS = {"devices": 0, "offline": [], "reset_detected": [], "restored": [], "errors": [],
          "hardened": [], "last_backup": None, "last_check": None, "state_ts": None}


def _publish():
    now_ts = datetime.datetime.now().isoformat(timespec="seconds")
    STATUS["state_ts"] = now_ts
    try:
        rows = sorted(DEVICE_TABLE.values(), key=lambda x: (x.get("online", True), (x.get("name") or "").lower()))
        _write_json(STATE_FILE, {"updated_at": now_ts, "status": STATUS, "devices": rows})
    except Exception as e:
        log.error(f"[{APP}] write state file {STATE_FILE}: {e}")
    state.set("sensor.shelly_guard", value=len(STATUS["reset_detected"]),
              new_attributes={**STATUS, "friendly_name": "Shelly Guard",
                              "icon": "mdi:shield-sync", "backup_dir": BACKUP_DIR})


# ---------------------------------------------------------------------------
# Device operations
# ---------------------------------------------------------------------------

def _fetch(dev):
    """Read full config of one device. Returns backup payload."""
    host, gen = _dev_addr(dev), dev["gen"]
    u, p = dev.get("user") or SHELLY_USER, dev.get("password") or SHELLY_PASS
    if gen == 1:
        settings = _gen1_get(host, "/settings", user=u, password=p)
        try:
            actions = _gen1_get(host, "/settings/actions", user=u, password=p)
        except Exception:
            actions = None
        cfg = {"settings": settings, "actions": actions}
        fw = settings.get("fw") or dev.get("sw_version")
    else:
        conf = _rpc(host, "Shelly.GetConfig", user=u, password=p)
        info = _rpc(host, "Shelly.GetDeviceInfo", user=u, password=p) or {}
        fw = info.get("ver") or info.get("fw_id") or dev.get("sw_version")
        scripts = []
        try:
            for s in (_rpc(host, "Script.List", user=u, password=p) or {}).get("scripts", []):
                code, offset = "", 0
                while True:
                    r = _rpc(host, "Script.GetCode", {"id": s["id"], "offset": offset, "len": 2048},
                             user=u, password=p)
                    chunk = r.get("data", "")
                    code += chunk
                    offset += len(chunk)
                    if not chunk or r.get("left", 0) == 0:
                        break
                s["code"] = code
                scripts.append(s)
        except Exception as e:
            log.debug(f"[{APP}] {host} scripts: {e}")
        schedules = webhooks = []
        kvs = {}
        try:
            schedules = (_rpc(host, "Schedule.List", user=u, password=p) or {}).get("jobs", [])
        except Exception:
            pass
        try:
            webhooks = (_rpc(host, "Webhook.List", user=u, password=p) or {}).get("hooks", [])
        except Exception:
            pass
        try:
            kvs = (_rpc(host, "KVS.GetMany", {"match": "*"}, user=u, password=p) or {}).get("items", {})
            if isinstance(kvs, list):  # newer fw returns list of {key, value, etag}
                kvs = {i["key"]: {"value": i.get("value")} for i in kvs}
        except Exception:
            pass
        cfg = {"config": conf, "profile": info.get("profile"), "scripts": scripts,
               "schedules": schedules, "webhooks": webhooks, "kvs": kvs}
    return {"mac": dev["mac"], "gen": gen, "name": dev["name"], "area": dev["area"],
            "model": dev["model"], "host": dev["host"], "port": int(dev.get("port") or 80),
            "fw": fw,
            "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "config": cfg}


def _harden(dev, current):
    """Disable factory-reset-by-input; make sure the device has a name. Returns list of changes."""
    host, gen, changes = _dev_addr(dev), dev["gen"], []
    u, p = dev.get("user") or SHELLY_USER, dev.get("password") or SHELLY_PASS
    if gen == 1:
        s = current["config"]["settings"]
        params = {}
        if s.get("factory_reset_from_switch"):
            params["factory_reset_from_switch"] = "false"
        if s.get("pon_wifi_reset"):
            params["pon_wifi_reset"] = "false"
        if not s.get("name") and dev["name"]:
            params["name"] = dev["name"]
        if params:
            _gen1_get(host, "/settings", params, user=u, password=p)
            changes.append(params)
    else:
        conf = current["config"]["config"]
        for key, comp in conf.items():
            if key.startswith("input:") and isinstance(comp, dict) and comp.get("factory_reset"):
                _rpc(host, "Input.SetConfig",
                     {"id": int(key.split(":")[1]), "config": {"factory_reset": False}},
                     user=u, password=p)
                changes.append(f"{key}.factory_reset=false")
        if not ((conf.get("sys") or {}).get("device") or {}).get("name") and dev["name"]:
            _rpc(host, "Sys.SetConfig", {"config": {"device": {"name": dev["name"]}}}, user=u, password=p)
            changes.append("name")
        if MARKER_KEY not in (current["config"].get("kvs") or {}):
            _rpc(host, "KVS.Set", {"key": MARKER_KEY, "value": current["saved_at"]}, user=u, password=p)
            changes.append("marker")
    return changes


def _restore(dev, backup, dry_run=True):
    host, gen = _dev_addr(dev), backup["gen"]
    u, p = dev.get("user") or SHELLY_USER, dev.get("password") or SHELLY_PASS
    done, failed = [], []
    if gen == 1:
        plan = gen1_restore_plan(backup["config"]["settings"], backup["config"].get("actions"))
        for path, params in plan:
            if dry_run:
                done.append(f"GET {path} {params}")
                continue
            try:
                _gen1_get(host, path, params, user=u, password=p)
                done.append(path)
                if "mode" in params and len(params) == 1:
                    task.sleep(3)
            except Exception as e:
                failed.append(f"{path}: {e}")
        if not dry_run and p:
            try:
                _gen1_get(host, "/settings/login", {"enabled": "true", "username": u, "password": p},
                          user=u, password=p)
                done.append("auth")
            except Exception as e:
                failed.append(f"auth: {e}")
        sta = backup["config"]["settings"].get("wifi_sta") or {}
        if not dry_run and done:
            try:
                _gen1_get(host, "/reboot", user=u, password=p)
                done.append("reboot")
                task.sleep(25)
            except Exception as e:
                failed.append(f"reboot: {e}")
        if sta.get("ipv4_method") == "static" and sta.get("ip"):
            home_ssid, wifi_pass = _wifi_creds(WIFI_SECRETS, WIFI_SSID_KEY, WIFI_PASS_KEY, WIFI_PASS)
            if not wifi_pass:
                failed.append(f"static IP {sta['ip']} not set: no Wi-Fi password in {WIFI_SECRETS}")
            elif dry_run:
                done.append(f"GET /settings/sta static {sta['ip']}")
            else:
                try:
                    _gen1_get(host, "/settings/sta", {
                        "enabled": "true", "ssid": sta.get("ssid") or home_ssid, "key": wifi_pass,
                        "ipv4_method": "static", "ip": sta["ip"], "netmask": sta.get("mask"),
                        "gateway": sta.get("gw"), "dns": sta.get("dns")}, user=u, password=p)
                    done.append(f"static IP {sta['ip']}")
                except Exception as e:
                    failed.append(f"static IP: {e}")
        rollers = backup["config"]["settings"].get("rollers") or []
        if not dry_run and any([r.get("positioning") for r in rollers]):
            failed.append("roller: needs recalibration (/roller/0/calibrate)")
        return done, failed

    plan = gen2_restore_plan(backup["config"])
    need_reboot = False
    existing_scripts, existing_hooks = {}, []
    if not dry_run:
        try:
            for s0 in (_rpc(host, "Script.List", user=u, password=p) or {}).get("scripts", []):
                existing_scripts[s0.get("name")] = s0["id"]
        except Exception:
            pass
        try:
            existing_hooks = (_rpc(host, "Webhook.List", user=u, password=p) or {}).get("hooks", [])
        except Exception:
            pass
    for method, params in plan:
        if dry_run:
            done.append(f"{method} {json.dumps(params)[:160]}")
            continue
        try:
            if method == "Shelly.SetProfile":
                cur = (_rpc(host, "Shelly.GetDeviceInfo", user=u, password=p) or {}).get("profile")
                if cur and cur != params["name"]:
                    _rpc(host, method, params, user=u, password=p)
                    task.sleep(25)  # device reboots
            elif method == "__script__":
                s = params
                sid = existing_scripts.get(s.get("name"))
                if sid is None:
                    sid = _rpc(host, "Script.Create", {"name": s.get("name")}, user=u, password=p)["id"]
                else:
                    try:
                        _rpc(host, "Script.Stop", {"id": sid}, user=u, password=p)
                    except Exception:
                        pass
                code = s.get("code", "")
                for i in range(0, max(len(code), 1), 1024):
                    _rpc(host, "Script.PutCode", {"id": sid, "code": code[i:i + 1024], "append": i > 0},
                         user=u, password=p)
                _rpc(host, "Script.SetConfig", {"id": sid, "config": {"enable": bool(s.get("enable"))}},
                     user=u, password=p)
                if s.get("running"):
                    _rpc(host, "Script.Start", {"id": sid}, user=u, password=p)
            elif method == "Webhook.Create" and [h for h in existing_hooks
                                                  if h.get("name") == params.get("name")
                                                  and h.get("event") == params.get("event")
                                                  and h.get("cid") == params.get("cid")]:
                done.append("Webhook exists: " + str(params.get("name")))
                continue
            else:
                res = _rpc(host, method, params, user=u, password=p)
                if isinstance(res, dict) and res.get("restart_required"):
                    need_reboot = True
            done.append(method)
        except Exception as e:
            failed.append(f"{method}: {e}")
    if not dry_run and need_reboot:
        try:
            _rpc(host, "Shelly.Reboot", user=u, password=p)
            task.sleep(20)
        except Exception as e:
            failed.append(f"reboot: {e}")
    sta2 = ((backup["config"].get("config") or {}).get("wifi") or {}).get("sta") or {}
    if sta2.get("ipv4mode") == "static" and sta2.get("ip"):
        cfg_ip = {"sta": {"ipv4mode": "static", "ip": sta2["ip"], "netmask": sta2.get("netmask"),
                          "gw": sta2.get("gw"), "nameserver": sta2.get("nameserver")}}
        if dry_run:
            done.append(f"WiFi.SetConfig static {sta2['ip']}")
        else:
            try:
                _rpc(host, "WiFi.SetConfig", {"config": cfg_ip}, user=u, password=p)
                done.append(f"static IP {sta2['ip']}")
            except Exception as e:
                failed.append(f"static IP: {e}")
    if not dry_run and p:
        try:
            dev_id = (_rpc(host, "Shelly.GetDeviceInfo", user=u, password=p) or {}).get("id")
            ha1 = hashlib.sha256(f"admin:{dev_id}:{p}".encode()).hexdigest()
            _rpc(host, "Shelly.SetAuth", {"user": "admin", "realm": dev_id, "ha1": ha1},
                 user=u, password=p)
            done.append("auth")
        except Exception as e:
            failed.append(f"auth: {e}")
    if not dry_run:
        try:
            _rpc(host, "KVS.Set", {"key": MARKER_KEY, "value": "restored " + backup["saved_at"]},
                 user=u, password=p)
        except Exception:
            pass
        if any([k.startswith("cover:") for k in (backup["config"].get("config") or {})]):
            failed.append("cover: run calibration in HA/web UI (Cover.Calibrate)")
    return done, failed


# ---------------------------------------------------------------------------
# Services & triggers
# ---------------------------------------------------------------------------

def _resolve_via_range_extenders(offline_map, range_extenders):
    """Check online Range Extender Shellys (WiFi.ListAPClients) for offline devices.
    If a MAC is found behind a Range Extender, update its HA config entry to host:mport
    and reload it so HA and shelly_guard reach it transparently."""
    resolved = {}
    if not offline_map or not range_extenders:
        return resolved
    for ext in range_extenders:
        u, p = ext.get("user") or SHELLY_USER, ext.get("password") or SHELLY_PASS
        try:
            res = _rpc(_dev_addr(ext), "WiFi.ListAPClients", timeout=4, user=u, password=p) or {}
        except Exception as e:
            log.debug(f"[{APP}] ListAPClients {ext['name']}: {e}")
            continue
        for c in res.get("ap_clients") or []:
            cmac = norm_mac(c.get("mac") or "")
            mport = c.get("mport")
            if cmac not in offline_map or not mport:
                continue
            dev = offline_map[cmac]
            new_host, new_port = ext["host"], int(mport)
            updated = False
            try:
                entry = hass.config_entries.async_get_entry(dev["entry_id"])
                if entry and (entry.data.get("host") != new_host or int(entry.data.get("port") or 80) != new_port):
                    new_data = dict(entry.data)
                    new_data["host"] = new_host
                    new_data["port"] = new_port
                    hass.config_entries.async_update_entry(entry, data=new_data)
                    hass.config_entries.async_reload(entry.entry_id)
                    updated = True
            except Exception as e:
                log.error(f"[{APP}] update range-extender entry for {dev['name']}: {e}")
            resolved[cmac] = {"via": ext["name"], "host": new_host, "port": new_port,
                              "client_ip": c.get("ip"), "updated": updated}
            OFFLINE_RUNS.pop(cmac, None)
            NOTIFIED.pop(cmac, None)
            if updated:
                _notify("Shelly via Range Extender",
                        f"{dev['name']} ({dev['area'] or '-'}) está ligado ao Range Extender "
                        f"{ext['name']} ({new_host}:{new_port}). A integração no Home Assistant foi atualizada.")
    return resolved


def _scan_for_reset_aps(offline_devs, online_gen2):
    """Ask nearby Gen2+ Shellys to scan Wi-Fi and look for the reset APs of offline devices."""
    areas = set([d["area"] for d in offline_devs.values() if d["area"]])
    same = [d for d in online_gen2 if d["area"] in areas]
    other = [d for d in online_gen2 if d["area"] not in areas]
    scanners = (same + other)[:int(CFG.get("scan_devices", 8))]
    scans = {}
    for d in scanners:
        res, err = _wifi_scan(_dev_addr(d), user=d.get("user") or SHELLY_USER,
                              password=d.get("password") or SHELLY_PASS)
        if res is None:
            log.warning(f"[{APP}] scan via {d['name']} failed: {err}")
            continue
        scans[d["name"]] = res
    found = match_reset_aps(offline_devs, scans)
    needs = []
    for mac, hit in found.items():
        dev = offline_devs[mac]
        item = {"mac": mac, "name": dev["name"], "area": dev["area"], "gen": dev["gen"],
                "ssid": hit["ssid"], "near": hit["near"], "rssi": hit["rssi"]}
        needs.append(item)
        if NOTIFIED.get(mac) == hit["ssid"]:
            continue
        NOTIFIED[mac] = hit["ssid"]
        if dev["gen"] == 1:
            how = (f"Connect your phone to Wi-Fi '{hit['ssid']}', open http://192.168.33.1 > "
                   "Internet & Security > Wi-Fi Mode - Client, enter the home Wi-Fi and save.")
        else:
            how = ("In Home Assistant open Settings > Devices & services > Discovered and use "
                   "'Provision Wi-Fi via Bluetooth' (or join its Wi-Fi and open http://192.168.33.1).")
        _notify("Shelly needs Wi-Fi",
                f"{dev['name']} ({dev['area'] or '-'}) was factory-reset and is broadcasting "
                f"'{hit['ssid']}' near {hit['near']}. {how} Its configuration will then be restored automatically.")
        event.fire("shelly_guard_reconnect_needed", **item)
    STATUS["needs_reconnect"] = needs
    STATUS["last_scan"] = {"at": datetime.datetime.now().isoformat(timespec="seconds"),
                           "scanners": list(scans.keys()),
                           "offline_checked": [d["name"] for d in offline_devs.values()]}


@service
def shelly_guard_scan(force=True):
    """Run the neighbour Wi-Fi scan now (in the background) for every offline device."""
    task.create(_scan_now)


def _scan_now():
    task.unique("shelly_guard_scan_run", kill_me=True)
    inv = _shelly_inventory()
    offline_devs, online_gen2 = {}, []
    for mac, dev in inv.items():
        u, p = dev.get("user") or SHELLY_USER, dev.get("password") or SHELLY_PASS
        addr = _dev_addr(dev)
        try:
            if dev["gen"] == 1:
                _gen1_get(addr, "/shelly", timeout=4, user=u, password=p)
            else:
                _rpc(addr, "Shelly.GetDeviceInfo", timeout=4, user=u, password=p)
                online_gen2.append(dev)
        except Exception:
            offline_devs[mac] = dev
    resolved = _resolve_via_range_extenders(offline_devs, online_gen2)
    for cmac in resolved:
        offline_devs.pop(cmac, None)
    _scan_for_reset_aps(offline_devs, online_gen2)
    LAST_SCAN["t"] = time.time()
    _publish()
    log.warning(f"[{APP}] scan: offline={[d['name'] for d in offline_devs.values()]} "
                f"needs_reconnect={STATUS.get('needs_reconnect')}")


@service
def shelly_guard_backup_all():
    """Backup the configuration of every Shelly known to Home Assistant."""
    inv = _shelly_inventory()
    STATUS["devices"] = len(inv)
    offline, errors, changed = [], [], 0
    index = {}
    for mac, dev in inv.items():
        try:
            payload = _fetch(dev)
            if _write_backup(BACKUP_DIR, mac, payload, KEEP_VERSIONS):
                changed += 1
            index[mac] = {k: dev[k] for k in ("name", "area", "model", "host", "gen")}
            index[mac]["saved_at"] = payload["saved_at"]
        except Exception as e:
            offline.append(dev["name"])
            log.info(f"[{APP}] backup {dev['name']} ({dev['host']}): {e}")
    _write_index(BACKUP_DIR, index)
    STATUS.update(offline=offline, last_backup=datetime.datetime.now().isoformat(timespec="seconds"))
    _publish()
    log.info(f"[{APP}] backup done: {len(index)} ok, {changed} changed, {len(offline)} offline")


@service
def shelly_guard_check():
    """Harden every device and detect devices that came back factory-reset."""
    task.unique("shelly_guard_check_run", kill_me=True)
    inv = _shelly_inventory()
    STATUS["devices"] = len(inv)
    resets, restored, hardened, offline, errors, risky, saved = [], [], [], [], [], [], 0
    online_gen2, range_extenders, offline_devs, all_offline = [], [], {}, {}
    for mac, dev in inv.items():
        backup = _read_backup(BACKUP_DIR, mac)
        try:
            cur = _fetch(dev)
        except Exception as e:
            err_msg = f"{type(e).__name__} {str(e)[:120]}"
            offline.append(f"{dev['name']}: {err_msg}")
            all_offline[mac] = dev
            DEVICE_TABLE[mac] = _build_device_row(mac, dev, cur=None, backup=backup, online=False, err=err_msg)
            OFFLINE_RUNS[mac] = OFFLINE_RUNS.get(mac, 0) + 1
            if OFFLINE_RUNS[mac] >= 2:
                offline_devs[mac] = dev
            continue
        if OFFLINE_RUNS.pop(mac, 0) and mac in NOTIFIED:
            NOTIFIED.pop(mac, None)
            _notify("Shelly back online",
                    f"{dev['name']} ({dev['area'] or '-'}) is back on the network. "
                    "If it was reset, its configuration is restored automatically in the next minutes.")
        if dev["gen"] != 1:
            online_gen2.append(dev)
            re_cfg = (((cur["config"].get("config") or {}).get("wifi") or {}).get("ap") or {}).get("range_extender") or {}
            if re_cfg.get("enable"):
                range_extenders.append(dev)
        if dev["gen"] == 1:
            is_reset = gen1_looks_factory(cur["config"]["settings"],
                                          backup and backup["config"]["settings"])
        else:
            is_reset = gen2_looks_factory(cur["config"]["config"],
                                          set((cur["config"].get("kvs") or {}).keys()),
                                          backup and backup["config"])
        if is_reset:
            SUSPECT[mac] = SUSPECT.get(mac, 0) + 1
            resets.append(dev["name"])
            DEVICE_TABLE[mac] = _build_device_row(mac, dev, cur=cur, backup=backup, online=True, reset=True)
            if SUSPECT[mac] < 2:
                continue  # confirm on the next run before touching the device
            SUSPECT.pop(mac, None)
            if AUTO_RESTORE:
                done, failed = _restore(dev, backup, dry_run=False)
                restored.append(dev["name"])
                _notify("Shelly restored",
                        f"{dev['name']} ({dev['area'] or '-'}) came back factory-reset and was restored "
                        f"from the {backup['saved_at']} backup: {len(done)} steps ok"
                        + (f", to check: {'; '.join(failed)}" if failed else "."))
                if failed:
                    errors.extend([f"{dev['name']}: {f}" for f in failed])
            else:
                _notify("Shelly factory-reset detected",
                        f"{dev['name']} lost its configuration. Backup from {backup['saved_at']} is ready "
                        f"(pyscript.shelly_guard_restore mac={mac}).")
            continue
        SUSPECT.pop(mac, None)
        ch = []
        if HARDEN:
            try:
                ch = _harden(dev, cur)
                if ch:
                    hardened.append(f"{dev['name']}: {ch}")
            except Exception as e:
                errors.append(f"{dev['name']} harden: {e}")
        # keep the backup fresh (only when the device is NOT in factory state)
        try:
            final = _fetch(dev) if ch else cur
            _write_backup(BACKUP_DIR, mac, final, KEEP_VERSIONS)
            saved += 1
            if _reset_by_input_enabled(final):
                risky.append(dev["name"])
            DEVICE_TABLE[mac] = _build_device_row(mac, dev, cur=final, backup=final, online=True)
        except Exception as e:
            errors.append(f"{dev['name']} backup: {e}")
            DEVICE_TABLE[mac] = _build_device_row(mac, dev, cur=cur, backup=backup, online=True, err=str(e))
    # Drop removed devices from table
    for stale in [m for m in list(DEVICE_TABLE.keys()) if m not in inv]:
        DEVICE_TABLE.pop(stale, None)
    re_resolved = _resolve_via_range_extenders(all_offline, range_extenders)
    for cmac, rinfo in re_resolved.items():
        offline_devs.pop(cmac, None)
        cname = all_offline[cmac]["name"]
        offline = [o for o in offline if not o.startswith(f"{cname}:")]
        dev_re = dict(all_offline[cmac])
        dev_re["host"] = rinfo["host"]
        dev_re["port"] = rinfo["port"]
        try:
            cur_re = _fetch(dev_re)
            _write_backup(BACKUP_DIR, cmac, cur_re, KEEP_VERSIONS)
            saved += 1
            DEVICE_TABLE[cmac] = _build_device_row(cmac, dev_re, cur=cur_re, backup=cur_re, online=True)
        except Exception:
            if cmac in DEVICE_TABLE:
                DEVICE_TABLE[cmac]["host"] = rinfo["host"]
                DEVICE_TABLE[cmac]["port"] = rinfo["port"]
                DEVICE_TABLE[cmac]["online"] = True
                DEVICE_TABLE[cmac]["error"] = ""
    if offline_devs and time.time() - LAST_SCAN["t"] >= SCAN_EVERY:
        _scan_for_reset_aps(offline_devs, online_gen2)
        LAST_SCAN["t"] = time.time()
    STATUS.update(reset_detected=resets, restored=restored, hardened=hardened, offline=offline,
                  range_extender_resolved=re_resolved,
                  backed_up=saved, reset_by_switch_still_on=risky,
                  errors=errors[-20:], last_check=datetime.datetime.now().isoformat(timespec="seconds"))
    _publish()
    if hardened:
        log.warning(f"[{APP}] hardened: {hardened}")


@service
def shelly_guard_check_device(mac=None):
    """Run check, hardening, Range Extender lookup and backup for a single Shelly device."""
    m = norm_mac(mac or "")
    if not m:
        log.error(f"[{APP}] shelly_guard_check_device: invalid mac={mac}")
        return
    inv = _shelly_inventory()
    dev = inv.get(m)
    if not dev:
        log.error(f"[{APP}] shelly_guard_check_device: mac {m} not in HA Shelly inventory")
        return
    backup = _read_backup(BACKUP_DIR, m)
    try:
        cur = _fetch(dev)
    except Exception as e:
        err_msg = f"{type(e).__name__} {str(e)[:120]}"
        # Try Range Extenders before marking offline
        re_hosts = [d for d in inv.values() if d["gen"] != 1 and d["mac"] != m]
        re_res = _resolve_via_range_extenders({m: dev}, re_hosts)
        if m in re_res:
            dev = dict(dev)
            dev["host"] = re_res[m]["host"]
            dev["port"] = re_res[m]["port"]
            try:
                cur = _fetch(dev)
            except Exception as e2:
                DEVICE_TABLE[m] = _build_device_row(m, dev, cur=None, backup=backup, online=False, err=str(e2))
                _publish()
                return
        else:
            DEVICE_TABLE[m] = _build_device_row(m, dev, cur=None, backup=backup, online=False, err=err_msg)
            _publish()
            return
    if HARDEN:
        try:
            ch = _harden(dev, cur)
            if ch:
                cur = _fetch(dev)
        except Exception as e:
            log.warning(f"[{APP}] single harden {dev['name']}: {e}")
    try:
        _write_backup(BACKUP_DIR, m, cur, KEEP_VERSIONS)
    except Exception as e:
        log.warning(f"[{APP}] single backup {dev['name']}: {e}")
    DEVICE_TABLE[m] = _build_device_row(m, dev, cur=cur, backup=cur, online=True)
    STATUS["offline"] = [o for o in STATUS.get("offline", []) if not o.startswith(f"{dev['name']}:")]
    STATUS["last_device_check"] = f"{dev['name']} @ {datetime.datetime.now().strftime('%H:%M:%S')}"
    _publish()


@service
def shelly_guard_restore(mac=None, host=None, dry_run=True, backup_mac=None):
    """Restore one Shelly from backup.
    mac: device MAC; host: override IP (e.g. after a new DHCP lease);
    dry_run: only list the steps (default true); backup_mac: restore another device's backup
    onto this one (replacement device, same model)."""
    m = norm_mac(mac or "")
    inv = _shelly_inventory()
    dev = inv.get(m) or {"mac": m, "host": host, "gen": None, "name": m, "area": None, "model": None}
    if host:
        dev["host"] = host
    backup = _read_backup(BACKUP_DIR, norm_mac(backup_mac) if backup_mac else m)
    if not backup:
        log.error(f"[{APP}] no backup for {mac}")
        return
    done, failed = _restore(dev, backup, dry_run=bool(dry_run) and str(dry_run).lower() != "false")
    log.warning(f"[{APP}] restore {dev['name']} dry_run={dry_run}: {len(done)} ok, {len(failed)} issues")
    for line in done:
        log.warning(f"[{APP}]   {line}")
    for line in failed:
        log.warning(f"[{APP}]   ! {line}")
    return {"done": done, "failed": failed}


GEN1_HANDLED_ROOT = set(GEN1_ROOT_KEYS + ["mode", "mqtt", "coiot", "sntp", "cloud", "factory_reset_from_switch", "pon_wifi_reset",
                                         "login", "wifi_sta", "relays", "rollers", "lights", "emeters", "inputs"])
GEN1_READ_ONLY = set(["device", "wifi_ap", "wifi_sta1", "ap_roaming", "fw", "build_info", "time", "unixtime",
                      "hwinfo", "actions", "pin_code", "fw_mode", "debug_enable", "calibrated", "tz_utc_offset",
                      "tz_dst", "tz_dst_auto", "tz_utc_offset", "has_timer", "sleep_mode", "power"])


@service
def shelly_guard_coverage(mac=None):
    """Compare a device's live settings with what a restore would write; lists anything not covered."""
    task.create(_coverage_now, mac)


def _coverage_now(mac):
    inv = _shelly_inventory()
    targets = [inv[norm_mac(mac)]] if mac else [d for d in inv.values() if d["gen"] == 1]
    report = {}
    for dev in targets:
        try:
            cur = _fetch(dev)
        except Exception as e:
            report[dev["name"]] = f"offline: {e}"
            continue
        if dev["gen"] != 1:
            report[dev["name"]] = "gen2+: full Shelly.GetConfig (minus Wi-Fi password)"
            continue
        st = cur["config"]["settings"]
        miss = [k for k in st.keys() if k not in GEN1_HANDLED_ROOT and k not in GEN1_READ_ONLY]
        for section, (path, keys) in GEN1_SECTION_KEYS.items():
            for i, item in enumerate(st.get(section) or []):
                for k in item.keys():
                    if k not in keys and k not in ("ison", "has_timer", "timer_started", "timer_duration",
                                                   "timer_remaining", "overpower", "source", "state",
                                                   "current_pos", "last_direction", "positioning",
                                                   "calibrating", "power", "is_valid", "temperature"):
                        miss.append(f"{section}[{i}].{k}={item[k]}")
        report[dev["name"]] = miss or "all covered"
        log.warning(f"[{APP}] coverage {dev['name']}: {miss}")
    STATUS["coverage"] = report
    _publish()


@service
def shelly_guard_router_dhcp(apply=False):
    """Compare Shelly IPs with the ASUS DHCP reservations (via the AsusRouter integration's
    credentials). apply=true adds ONLY the missing reservations; existing ones are never changed."""
    task.create(_router_dhcp_now, str(apply).lower() == "true")


def _router_dhcp_now(apply):
    ents = hass.config_entries.async_entries("asusrouter")
    if not ents:
        log.error(f"[{APP}] no asusrouter integration")
        return
    d = dict(ents[0].data)
    d.update(dict(ents[0].options or {}))
    host = d.get("host")
    port = d.get("port") or (8443 if d.get("ssl") or d.get("use_ssl") else 80)
    proto = "https" if (d.get("ssl") or d.get("use_ssl") or port in (443, 8443)) else "http"
    base = f"{proto}://{host}:{port}"
    user, pw = d.get("username"), d.get("password")
    cur = _asus_dhcp(base, user, pw)
    if cur.get("error"):
        STATUS["router_dhcp"] = {"error": cur["error"], "base": base, "entry_keys": sorted(d.keys())}
        _publish()
        return
    existing = parse_staticlist(cur.get("dhcp_staticlist"))
    template = existing[0]["rest"] if existing else ["", "__NAME__"]
    template = ["__NAME__" if i == len(template) - 1 else "" for i in range(len(template))] or ["", "__NAME__"]
    wanted = {}
    for mac, dev in _shelly_inventory().items():
        if int(dev.get("port") or 80) != 80:
            continue  # behind a Shelly Range Extender (NAT), not on router DHCP
        if "Pro" in str(dev.get("model") or "") and CFG.get("pro_use_eth_mac", True):
            mac = "%012X" % (int(mac, 16) + 3)  # Shelly Pro on Ethernet uses base MAC + 3
        wanted[":".join([mac[i:i + 2] for i in range(0, 12, 2)])] = (dev["host"], dev["name"])
    to_add, conflicts, already = plan_reservations(existing, wanted, cur.get("dhcp_start"),
                                                   cur.get("dhcp_end"), template)
    report = {"router": f"{cur.get('productid')} {cur.get('firmver')}.{cur.get('buildno')}",
              "pool": f"{cur.get('dhcp_start')} - {cur.get('dhcp_end')}",
              "static_enabled": cur.get("dhcp_static_x"),
              "existing_count": len(existing), "already_ok": already,
              "to_add": [f"{a['name']} {a['mac']} {a['ip']}" for a in to_add],
              "conflicts": conflicts,
              "applied": False}
    raw = cur.get("dhcp_staticlist") or ""
    sane = ("&#" not in raw) and (len(existing) == raw.count("<")) and \
        all([len(e["mac"]) == 17 and e["ip"].count(".") == 3 for e in existing])
    report["parse_ok"] = sane
    if apply and to_add and not sane:
        report["apply_refused"] = "existing list did not parse cleanly"
    elif apply and to_add:
        new_raw = build_staticlist(existing + to_add)
        res = _asus_dhcp(base, user, pw, new_list=new_raw)
        after = parse_staticlist(res.get("after"))
        report["applied"] = True
        report["apply_status"] = res.get("apply_status")
        report["count_after"] = len(after)
        after_macs = [e["mac"] for e in after]
        report["verified"] = all([a["mac"] in after_macs for a in to_add]) and \
            all([e["mac"] in after_macs for e in existing])
    STATUS["router_dhcp"] = report
    _publish()
    log.warning(f"[{APP}] router dhcp: {report}")


@service
def shelly_guard_router_clients():
    """Snapshot of the router's client list (MAC -> IP/name/online) into sensor.shelly_guard."""
    task.create(_router_clients_now)


def _router_conn():
    ents = hass.config_entries.async_entries("asusrouter")
    d = dict(ents[0].data)
    d.update(dict(ents[0].options or {}))
    port = d.get("port") or (8443 if d.get("ssl") or d.get("use_ssl") else 80)
    proto = "https" if (d.get("ssl") or d.get("use_ssl") or port in (443, 8443)) else "http"
    return f"{proto}://{d.get('host')}:{port}", d.get("username"), d.get("password")


@pyscript_executor
def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)


def _router_clients_now():
    base, user, pw = _router_conn()
    cur = _asus_dhcp(base, user, pw, clients=True)
    snap = {"static": [{"mac": e["mac"], "ip": e["ip"], "name": (e["rest"][-1] if e["rest"] else "")}
                       for e in parse_staticlist(cur.get("dhcp_staticlist"))],
            "clients": cur.get("clients", {}),
            "at": datetime.datetime.now().isoformat(timespec="seconds")}
    _write_json(os.path.join(BACKUP_DIR, "router_snapshot.json"), snap)
    state.set("sensor.shelly_guard_router", value=len(snap["clients"]),
              new_attributes={"static": snap["static"], "clients": snap["clients"], "at": snap["at"],
                              "friendly_name": "Shelly Guard router snapshot", "icon": "mdi:router-network"})
    STATUS["router_snapshot"] = f"{len(snap['static'])} reservations, {len(snap['clients'])} clients at {snap['at']}"
    _publish()


@service
def shelly_guard_router_edit(changes=None, dry_run=True):
    """changes: list of {"mac": .., "ip": .., "name": ..} to add/replace, and/or {"remove": MAC}.
    Only the MACs listed are touched; everything else in the reservation list is kept."""
    task.create(_router_edit_now, changes or [], str(dry_run).lower() != "false")


def _router_edit_now(changes, dry_run):
    base, user, pw = _router_conn()
    cur = _asus_dhcp(base, user, pw)
    raw = cur.get("dhcp_staticlist") or ""
    existing = parse_staticlist(raw)
    sane = ("&#" not in raw) and len(existing) == raw.count("<")
    items = [dict(e) for e in existing]
    log_lines = []
    for ch in changes:
        if ch.get("remove"):
            m = ch["remove"].upper()
            before = len(items)
            items = [e for e in items if e["mac"] != m]
            log_lines.append(f"remove {m}: {before - len(items)} entry")
            continue
        m, ip, name = ch["mac"].upper(), ch["ip"], ch.get("name", "")
        clash = [e for e in items if e["ip"] == ip and e["mac"] != m]
        if clash:
            log_lines.append(f"SKIP {m} {ip}: ip used by {clash[0]['mac']}")
            continue
        hit = [e for e in items if e["mac"] == m]
        if hit:
            hit[0]["ip"] = ip
            if name:
                hit[0]["rest"] = ["", name.replace(" ", "_")[:32]]
            log_lines.append(f"update {m} -> {ip}")
        else:
            items.append({"mac": m, "ip": ip, "rest": ["", name.replace(" ", "_")[:32]]})
            log_lines.append(f"add {m} -> {ip}")
    report = {"dry_run": dry_run, "parse_ok": sane, "before": len(existing), "after_planned": len(items),
              "steps": log_lines}
    if not dry_run and sane:
        res = _asus_dhcp(base, user, pw, new_list=build_staticlist(items))
        after = parse_staticlist(res.get("after"))
        report["after"] = len(after)
        report["verified"] = sorted([(e["mac"], e["ip"]) for e in after]) == sorted([(e["mac"], e["ip"]) for e in items])
    STATUS["router_edit"] = report
    _publish()
    log.warning(f"[{APP}] router edit: {report}")


@service
def shelly_guard_audit(fix=False):
    """List (and with fix=true remove) duplicated scripts/webhooks on Gen2+ devices."""
    report = []
    for mac, dev in _shelly_inventory().items():
        if dev["gen"] == 1:
            continue
        u, p = dev.get("user") or SHELLY_USER, dev.get("password") or SHELLY_PASS
        addr = _dev_addr(dev)
        try:
            scripts = (_rpc(addr, "Script.List", user=u, password=p) or {}).get("scripts", [])
            hooks = (_rpc(addr, "Webhook.List", user=u, password=p) or {}).get("hooks", [])
        except Exception:
            continue
        seen = {}
        for sc in scripts:
            key = sc.get("name")
            if key in seen:
                report.append(f"{dev['name']}: duplicate script '{key}' id={sc['id']}")
                if str(fix).lower() == "true":
                    try:
                        _rpc(addr, "Script.Stop", {"id": sc["id"]}, user=u, password=p)
                    except Exception:
                        pass
                    _rpc(addr, "Script.Delete", {"id": sc["id"]}, user=u, password=p)
            else:
                seen[key] = sc["id"]
        seen = {}
        for h in hooks:
            key = (h.get("name"), h.get("event"), h.get("cid"), tuple(h.get("urls") or []))
            if key in seen:
                report.append(f"{dev['name']}: duplicate webhook {key[0]}/{key[1]} id={h['id']}")
                if str(fix).lower() == "true":
                    _rpc(addr, "Webhook.Delete", {"id": h["id"]}, user=u, password=p)
            else:
                seen[key] = h["id"]
    STATUS["audit"] = report or ["no duplicates"]
    _publish()
    log.warning(f"[{APP}] audit fix={fix}: {report}")


@service
def shelly_guard_harden_all():
    """Disable factory-reset-from-switch/input on every reachable Shelly (same as a check run)."""
    shelly_guard_check()


@service
def shelly_guard_sync_netalertx():
    """Push HA device names, areas and vendor to NetAlertX (by MAC)."""
    if not (NAX_URL and NAX_TOKEN):
        log.error(f"[{APP}] netalertx_url/netalertx_token not configured")
        return
    ok, missing = 0, []
    for mac, dev in _shelly_inventory().items():
        cm = colon_mac(mac)
        code, txt = _nax_update(NAX_URL, NAX_TOKEN, cm, "devName", dev["name"])
        if code == 200 and "false" not in txt.lower():
            ok += 1
            _nax_update(NAX_URL, NAX_TOKEN, cm, "devVendor", "Shelly")
            if dev["area"]:
                _nax_update(NAX_URL, NAX_TOKEN, cm, "devLocation", dev["area"])
            note = dev["model"] or "Shelly"
            if dev.get("label") and dev["label"] != dev["name"]:
                note += f" | HA: {dev['label']}"
            _nax_update(NAX_URL, NAX_TOKEN, cm, "devComments", note + " (via HA)")
        else:
            missing.append(f"{dev['name']} {cm} [{code}]")
    log.warning(f"[{APP}] NetAlertX: {ok} renamed; not found/failed: {missing}")
    STATUS["netalertx"] = {"renamed": ok, "failed": missing}
    _publish()


@time_trigger("startup")
def _startup():
    global BACKUP_DIR
    BACKUP_DIR = _resolve_dir(BACKUP_DIR)
    log.warning(f"[{APP}] backups in {BACKUP_DIR} (config keys: {sorted(CFG.keys())}, /backup exists: {os.path.isdir('/backup')})")
    task.sleep(120)  # let the Shelly integration settle
    _publish()
    shelly_guard_check()


@time_trigger("cron(*/10 * * * *)")
def _periodic_check():
    shelly_guard_check()


@time_trigger("cron(17 4 * * *)")
def _nightly():
    task.unique("shelly_guard_nightly", kill_me=True)
    shelly_guard_backup_all()
    if NAX_URL and NAX_TOKEN:
        shelly_guard_sync_netalertx()

# Firmware updates that re-enable "reset from switch" are caught by the 10-minute check above.
