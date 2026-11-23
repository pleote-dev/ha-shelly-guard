"""Sensor platform for Shelly Guard."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_UPDATE
from .manager import ShellyGuardManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    manager: ShellyGuardManager = hass.data[DOMAIN]["manager"]
    async_add_entities([ShellyGuardSensor(manager, entry)])


class ShellyGuardSensor(SensorEntity):
    """Represents Shelly Guard overall status (value = factory resets currently detected)."""

    _attr_name = "Shelly Guard"
    _attr_icon = "mdi:shield-sync"
    _attr_has_entity_name = False

    def __init__(self, manager: ShellyGuardManager, entry: ConfigEntry) -> None:
        self._manager = manager
        self._attr_unique_id = f"{entry.entry_id}_status"

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._handle_update)
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        return len(self._manager.status.get("reset_detected") or [])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            **self._manager.status,
            "backup_dir": self._manager.backup_dir,
        }
