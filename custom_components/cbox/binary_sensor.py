"""Binary sensor entities for the cBox integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CboxConfigEntry, CboxCoordinator
from .entity import CboxEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CboxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the stove alarm."""
    async_add_entities([CboxAlarmBinarySensor(entry.runtime_data)])


class CboxAlarmBinarySensor(CboxEntity, BinarySensorEntity):
    """On when the stove reports an alarm."""

    _attr_translation_key = "alarm"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: CboxCoordinator) -> None:
        super().__init__(coordinator, "alarm")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.is_alarm
