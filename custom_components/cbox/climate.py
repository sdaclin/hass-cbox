"""Climate entity for the cBox integration."""

from __future__ import annotations

from typing import Any

from connbox import StoveStatus
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    FAN_MODES,
    MAX_TEMPERATURE,
    MIN_TEMPERATURE,
    STATUSES_OFF,
    STATUSES_STARTING,
    STATUSES_STOPPING,
)
from .coordinator import CboxConfigEntry, CboxCoordinator
from .entity import CboxEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CboxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the stove climate entity."""
    async_add_entities([CboxClimate(entry.runtime_data)])


class CboxClimate(CboxEntity, ClimateEntity):
    """The pellet stove as a heater."""

    _attr_name = None
    _attr_translation_key = "stove"
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_fan_modes = list(FAN_MODES)
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_precision = PRECISION_TENTHS
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_min_temp = MIN_TEMPERATURE
    _attr_max_temp = MAX_TEMPERATURE

    def __init__(self, coordinator: CboxCoordinator) -> None:
        super().__init__(coordinator, "climate")

    @property
    def hvac_mode(self) -> HVACMode:
        info = self.coordinator.data
        if info.status in STATUSES_OFF or info.status in STATUSES_STOPPING or info.is_alarm:
            return HVACMode.OFF
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction:
        info = self.coordinator.data
        if info.status in STATUSES_OFF or info.is_alarm:
            return HVACAction.OFF
        if info.status in STATUSES_STARTING:
            return HVACAction.PREHEATING
        if info.status is StoveStatus.BURNING:
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def current_temperature(self) -> float:
        return self.coordinator.data.t1

    @property
    def target_temperature(self) -> float:
        return self.coordinator.data.temperatureSetpoint

    @property
    def fan_mode(self) -> str | None:
        fan = self.coordinator.data.fanSetpoint
        return next((mode for mode, status in FAN_MODES.items() if status is fan), None)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self._async_send(self.coordinator.cbox.power_off)
        else:
            await self._async_send(self.coordinator.cbox.power_on)

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self._async_send(self.coordinator.cbox.change_temperature_setpoint, round(temperature))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        await self._async_send(self.coordinator.cbox.change_fan_setpoint, FAN_MODES[fan_mode])
