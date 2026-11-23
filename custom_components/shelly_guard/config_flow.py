"""Config flow and Options flow for Shelly Guard."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_AUTO_RESTORE,
    CONF_BACKUP_DIR,
    CONF_CHECK_INTERVAL_MIN,
    CONF_HARDEN,
    CONF_KEEP_VERSIONS,
    CONF_NETALERTX_TOKEN,
    CONF_NETALERTX_URL,
    CONF_NOTIFY_SERVICE,
    CONF_SCAN_EVERY_MIN,
    CONF_SHELLY_PASSWORD,
    CONF_SHELLY_USER,
    CONF_SHOW_SIDEBAR,
    CONF_WIFI_PASSWORD,
    DEFAULT_AUTO_RESTORE,
    DEFAULT_BACKUP_DIR,
    DEFAULT_CHECK_INTERVAL_MIN,
    DEFAULT_HARDEN,
    DEFAULT_KEEP_VERSIONS,
    DEFAULT_SCAN_EVERY_MIN,
    DEFAULT_SHELLY_USER,
    DEFAULT_SHOW_SIDEBAR,
    DOMAIN,
)


class ShellyGuardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shelly Guard."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Shelly Guard", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BACKUP_DIR, default=DEFAULT_BACKUP_DIR): str,
                vol.Required(CONF_KEEP_VERSIONS, default=DEFAULT_KEEP_VERSIONS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=100)
                ),
                vol.Required(CONF_AUTO_RESTORE, default=DEFAULT_AUTO_RESTORE): bool,
                vol.Required(CONF_HARDEN, default=DEFAULT_HARDEN): bool,
                vol.Required(CONF_CHECK_INTERVAL_MIN, default=DEFAULT_CHECK_INTERVAL_MIN): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=1440)
                ),
                vol.Optional(CONF_NOTIFY_SERVICE, default=""): str,
                vol.Optional(CONF_SHELLY_USER, default=DEFAULT_SHELLY_USER): str,
                vol.Optional(CONF_SHELLY_PASSWORD, default=""): str,
                vol.Required(CONF_SHOW_SIDEBAR, default=DEFAULT_SHOW_SIDEBAR): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return ShellyGuardOptionsFlow(config_entry)


class ShellyGuardOptionsFlow(config_entries.OptionsFlow):
    """Handle Shelly Guard options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    def _val(self, key: str, default: Any = "") -> Any:
        if key in self._entry.options:
            return self._entry.options[key]
        return self._entry.data.get(key, default)

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BACKUP_DIR, default=self._val(CONF_BACKUP_DIR, DEFAULT_BACKUP_DIR)): str,
                vol.Required(CONF_KEEP_VERSIONS, default=self._val(CONF_KEEP_VERSIONS, DEFAULT_KEEP_VERSIONS)): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=100)
                ),
                vol.Required(CONF_AUTO_RESTORE, default=self._val(CONF_AUTO_RESTORE, DEFAULT_AUTO_RESTORE)): bool,
                vol.Required(CONF_HARDEN, default=self._val(CONF_HARDEN, DEFAULT_HARDEN)): bool,
                vol.Required(
                    CONF_CHECK_INTERVAL_MIN,
                    default=self._val(CONF_CHECK_INTERVAL_MIN, DEFAULT_CHECK_INTERVAL_MIN),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                vol.Required(
                    CONF_SCAN_EVERY_MIN,
                    default=self._val(CONF_SCAN_EVERY_MIN, DEFAULT_SCAN_EVERY_MIN),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
                vol.Optional(CONF_NOTIFY_SERVICE, default=self._val(CONF_NOTIFY_SERVICE, "")): str,
                vol.Optional(CONF_SHELLY_USER, default=self._val(CONF_SHELLY_USER, DEFAULT_SHELLY_USER)): str,
                vol.Optional(CONF_SHELLY_PASSWORD, default=self._val(CONF_SHELLY_PASSWORD, "")): str,
                vol.Optional(CONF_WIFI_PASSWORD, default=self._val(CONF_WIFI_PASSWORD, "")): str,
                vol.Optional(CONF_NETALERTX_URL, default=self._val(CONF_NETALERTX_URL, "")): str,
                vol.Optional(CONF_NETALERTX_TOKEN, default=self._val(CONF_NETALERTX_TOKEN, "")): str,
                vol.Required(CONF_SHOW_SIDEBAR, default=self._val(CONF_SHOW_SIDEBAR, DEFAULT_SHOW_SIDEBAR)): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
