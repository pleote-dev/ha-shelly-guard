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

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


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

    if show_sidebar and not domain_data.get("panel_registered"):
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

    async def _svc_check_device(call: ServiceCall) -> None:
        mac = call.data.get("mac", "")
        hass.async_create_task(manager.async_check_device(mac))

    async def _svc_backup_all(call: ServiceCall) -> None:
        hass.async_create_task(manager.async_backup_all())

    async def _svc_restore(call: ServiceCall) -> None:
        await manager.async_restore(
            mac=call.data.get("mac", ""),
            host=call.data.get("host"),
            dry_run=bool(call.data.get("dry_run", True)),
            backup_mac=call.data.get("backup_mac"),
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

    services: dict[str, Any] = {
        "check": _svc_check,
        "check_device": _svc_check_device,
        "backup_all": _svc_backup_all,
        "restore": _svc_restore,
        "scan": _svc_scan,
        "audit": _svc_audit,
        "router_dhcp": _svc_router_dhcp,
        "sync_netalertx": _svc_sync_nax,
        "reload": _svc_reload,
    }
    for name, handler in services.items():
        hass.services.async_register(DOMAIN, name, handler)

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
        for svc in (
            "check", "check_device", "backup_all", "restore",
            "scan", "audit", "router_dhcp", "sync_netalertx", "reload",
        ):
            if hass.services.has_service(DOMAIN, svc):
                hass.services.async_remove(DOMAIN, svc)
    return unload_ok
