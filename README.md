<p align="center">
  <img src="images/icon.png" alt="Shelly Guard" width="128" />
</p>

<p align="center">
  <strong>🇬🇧 English</strong> · <a href="README.pt.md">🇵🇹 Português</a>
</p>

# Shelly Guard — Custom Integration for Home Assistant (HACS)

**Shelly Guard** is a custom integration for **Home Assistant** (installable via **HACS** and configured 100% through the UI) that protects your **Shelly (Gen1, Gen2, Gen3, and Gen4)** devices against accidental factory resets and hardware failures, providing **versioned automatic backups**, **auto-restore**, **Range Extender support**, **warranty tracking**, and a **dedicated sidebar dashboard**.

---

![Shelly Guard Dashboard](https://github.com/user-attachments/assets/ed0b7c7c-1d2a-4013-9b24-c20e671d26d8)

---

> **Disclaimer:** Shelly Guard is an independent community project. It is **not** affiliated with, endorsed by, or officially connected to **Shelly** / **Shelly Group** (Allterco Robotics) or **Home Assistant**.

---

## Features

* **100% UI-Configured (HACS):** Install via HACS and configure directly under *Settings → Devices & Services* (Config Flow & Options Flow, with English and Portuguese translations).
* **Versioned Automatic Backups:** Backs up every Shelly device known to Home Assistant (full config, names, profiles, relays/covers, actions, scripts, schedules, webhooks, and KVS), keeping a new snapshot only when the configuration changes.
* **Automatic Hardening:** Disables *factory reset from switch/input* (preventing accidental resets from toggling a wall switch 5×) and ensures every device has a configured name.
* **Factory-Reset Detection & Auto-Restore:** Detects devices that return in factory-default state and automatically restores their full configuration from the latest backup (including static IP and authentication).
* **Neighbor AP Scan for Reset Devices:** If a Shelly goes offline, asks nearby online Gen2+ Shellys to run `WiFi.Scan` and notifies you of its recovery SSID (`Shelly...`) and nearest neighbor.
* **Full Range Extender Support (Gen2+/Pro):**
  * Uses `host:port` (NAT `mport`) across all operations;
  * Queries `WiFi.ListAPClients` on Range Extender hosts before raising false factory-reset alerts;
  * Automatically updates the Home Assistant Shelly integration's `host` and `port` when a device connects through a Range Extender.
* **Faulty List & Replacement Wizard:**
  * Manually mark any device as **Faulty** (preserving its latest backup and invoice/warranty details even if removed from HA);
  * When a **new Shelly** joins Home Assistant, a modal lets you choose whether it is a **brand-new device** or a **replacement for a faulty/offline device**, automatically restoring the old device's backup onto the new hardware and archiving the old unit as *Replaced*.
* **Purchase & Warranty Tracking:**
  * Stores **purchase date**, **warranty duration** (default 36 months), **vendor/store**, **invoice number**, and notes per device (in `/share/shelly_guard/metadata.json`);
  * Displays warranty status badges (*Valid*, *Expiring soon*, *Expired*) and highlights store + invoice on faulty units for quick RMA claims.
* **Dedicated Sidebar Dashboard (`Shelly Guard`):**
  * Automatically served by the integration via an authenticated API (`/api/shelly_guard/state`) with automatic **English / Portuguese** UI localization following your Home Assistant user language;
  * Header shortcuts for **Reload**, **Backup All**, and **Full Check**;
  * Clickable KPIs, quick filters, live search, direct `http://host:port` links, firmware version & active **Upgrade** button (enabled only when an update is available), and per-device **Check** button.
* **Optional Integrations:** Sync names/areas to **NetAlertX** (configured in Options), audit duplicate scripts/webhooks, and manage **ASUS Router** DHCP static reservations (when `AsusRouter` is installed).

---

## Installation via HACS (Recommended)

Click the button below to open this repository directly in HACS on your Home Assistant instance:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=pleote-dev&repository=ha-shelly-guard&category=integration)

Or manually:

1. In Home Assistant, open **HACS** → **⋮** (top-right) → **Custom repositories**.
2. Add `https://github.com/pleote-dev/ha-shelly-guard` with category **Integration** → **Add**.
3. Search for **Shelly Guard** → **Download** → **Restart Home Assistant**.
4. Go to **Settings → Devices & Services → Add Integration** → search for **Shelly Guard**.
5. Review the options (backup directory, check interval, `auto_restore`, `harden`, optional notification service) and click **Submit**.

The **Shelly Guard** panel will appear automatically in your sidebar and `sensor.shelly_guard` will become active.

### Manual Installation (without HACS)
Copy `custom_components/shelly_guard` into `/config/custom_components/shelly_guard`, restart Home Assistant, and add **Shelly Guard** under **Settings → Devices & Services**.

---

## Available Services

| Service | Description |
| --- | --- |
| `shelly_guard.check` | Checks all Shellys, applies hardening, resolves Range Extender clients / resets, and updates backups. |
| `shelly_guard.check_device` | Runs check and backup for a single device (`mac: "AABBCCDDEEFF"`). |
| `shelly_guard.backup_all` | Immediately backs up all reachable Shelly devices. |
| `shelly_guard.restore` | Restores a device from backup (`mac`, optional `host`, `dry_run: true\|false`, optional `backup_mac` for hardware replacement). |
| `shelly_guard.scan` | Asks online Gen2+ Shellys to scan Wi-Fi for factory-reset APs. |
| `shelly_guard.audit` | Lists (and with `fix: true` removes) duplicate scripts and webhooks on Gen2+. |
| `shelly_guard.router_dhcp` | Compares/adds static DHCP reservations on an ASUS router (skips Range Extender clients). |
| `shelly_guard.sync_netalertx` | Pushes HA device names and areas to NetAlertX (when configured in Options). |
| `shelly_guard.set_metadata` | Saves purchase date, warranty months, vendor, invoice number, and notes for a device. |
| `shelly_guard.set_lifecycle` | Marks a device as `active`, `faulty`, or `replaced`. |
| `shelly_guard.confirm_new_device` | Confirms a newly detected Shelly as a brand-new device. |
| `shelly_guard.replace_device` | Restores backup from `old_mac` onto `new_mac` and archives the old device as replaced. |
| `shelly_guard.reload` | Reloads the Shelly Guard integration. |

---

## Range Extender Notes

* On Gen2/Pro Shellys, **Range Extender** uses NAT (`192.168.33.0/24`) and exposes each client on a dedicated port of the host Shelly (`http://<HOST_IP>:<mport>`).
* To keep `mport` stable across reboots, set a **static IP** in `192.168.33.x` on the client Shelly and disable its own AP.
* If a Shelly switches to a Range Extender (or its `mport` changes), Shelly Guard automatically discovers it via `WiFi.ListAPClients` and updates the Home Assistant config entry.

---

## License

MIT — see [LICENSE](LICENSE).
