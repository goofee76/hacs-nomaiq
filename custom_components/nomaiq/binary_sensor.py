from __future__ import annotations

import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import NomaIQDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class NomaIQTankFullSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.MOISTURE

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = f"{device._name} Tank Full"
        self._attr_unique_id = f"{device._dsn}_tank_full"

    @property
    def is_on(self) -> bool:
        return self._device.get_property_value("water_bucket_full")


class NomaIQFilterAlertSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = f"{device._name} Filter Alert"
        self._attr_unique_id = f"{device._dsn}_filter_alert"

    @property
    def is_on(self) -> bool:
        return self._device.get_property_value("filter_clean_alarm")


class NomaIQSensorFaultSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = f"{device._name} Sensor Fault"
        self._attr_unique_id = f"{device._dsn}_sensor_fault"

    @property
    def is_on(self) -> bool:
        return self._device.get_property_value("humidity_sensor_fault")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NomaIQDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device in coordinator.data:
        if getattr(device, "_device_model_number", None) == "AY028MHA1":
            entities.append(NomaIQTankFullSensor(coordinator, device))
            entities.append(NomaIQFilterAlertSensor(coordinator, device))
            entities.append(NomaIQSensorFaultSensor(coordinator, device))

    async_add_entities(entities)
