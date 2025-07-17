from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NomaIQDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

USER_MODES = ["Manual", "Continuous", "Auto Dry"]
MODE_MAP = {
    "Manual": "Normal",
    "Continuous": "Persistent",
    "Auto Dry": "Auto",
}
AYLA_TO_HASS_MODE = {v: k for k, v in MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NomaIQDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device in coordinator.data:
        if getattr(device, "_device_model_number", None) == "AY028MHA1":
            entities.append(NomaIQDehumidifier(coordinator, device))

    async_add_entities(entities)


class NomaIQDehumidifier(CoordinatorEntity, HumidifierEntity):
    _attr_supported_features = HumidifierEntityFeature.MODES
    _attr_min_humidity = 30
    _attr_max_humidity = 80
    _attr_available_modes = USER_MODES
    _attr_device_class = "dehumidifier"

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = device._name or "Dehumidifier"
        self._attr_unique_id = f"{device._dsn}_humidifier"

    @property
    def is_on(self) -> bool:
        return self._device.get_property_value("power")

    @property
    def current_humidity(self) -> int | None:
        return self._device.get_property_value("indoor_humidity")

    @property
    def target_humidity(self) -> int:
        return self._device.get_property_value("humidity")

    async def async_set_humidity(self, humidity: int) -> None:
        await self._device.async_set_property_value("humidity", humidity)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.async_set_property_value("power", True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.async_set_property_value("power", False)
        await self.coordinator.async_request_refresh()

    @property
    def mode(self) -> str:
        raw_mode = self._device.get_property_value("mode")
        return AYLA_TO_HASS_MODE.get(raw_mode, "Manual")

    async def async_set_mode(self, mode: str) -> None:
        if mode in MODE_MAP:
            await self._device.async_set_property_value("mode", MODE_MAP[mode])
            await self.coordinator.async_request_refresh()
