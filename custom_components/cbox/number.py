"""Number entities for the cBox integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import MAX_POWER, MIN_POWER
from .coordinator import CboxConfigEntry, CboxCoordinator
from .entity import CboxEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CboxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the stove power level."""
    async_add_entities([CboxPowerNumber(entry.runtime_data)])


class CboxPowerNumber(CboxEntity, NumberEntity):
    """The burn power level of the stove."""

    _attr_translation_key = "power"
    _attr_native_min_value = MIN_POWER
    _attr_native_max_value = MAX_POWER
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: CboxCoordinator) -> None:
        super().__init__(coordinator, "power")

    @property
    def native_value(self) -> float:
        return self.coordinator.data.powerSetpoint

    async def async_set_native_value(self, value: float) -> None:
        await self._async_send(self.coordinator.cbox.change_power_setpoint, int(value))
