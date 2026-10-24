"""Tests for the cBox entities."""

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from connbox import CboxCommandError, FanStatus, StoveStatus
from homeassistant.components.climate import (
    ATTR_FAN_MODE,
    ATTR_HVAC_ACTION,
    ATTR_HVAC_MODE,
    SERVICE_SET_FAN_MODE,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_TEMPERATURE,
    SERVICE_TURN_OFF,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate import (
    DOMAIN as CLIMATE_DOMAIN,
)
from homeassistant.components.number import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cbox.sensor import SENSORS

from .conftest import build_info

CLIMATE = "climate.pellet_stove"


async def test_climate_state(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    state = hass.states.get(CLIMATE)
    assert state.state == HVACMode.HEAT
    assert state.attributes[ATTR_HVAC_ACTION] == HVACAction.HEATING
    assert state.attributes["current_temperature"] == 19.6
    assert state.attributes[ATTR_TEMPERATURE] == 21
    assert state.attributes[ATTR_FAN_MODE] == "auto"


@pytest.mark.parametrize(
    ("status", "mode", "action"),
    [
        (StoveStatus.OFF, HVACMode.OFF, HVACAction.OFF),
        (StoveStatus.HEATUP, HVACMode.HEAT, HVACAction.HEATING),
        (StoveStatus.COOL, HVACMode.HEAT, HVACAction.IDLE),
        (StoveStatus.UNKNOWN, HVACMode.HEAT, HVACAction.IDLE),
        (StoveStatus.NOPELLET_ALAR, HVACMode.OFF, HVACAction.OFF),
    ],
)
async def test_climate_status_mapping(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_cbox: AsyncMock,
    status: StoveStatus,
    mode: HVACMode,
    action: HVACAction,
) -> None:
    raw = 42 if status is StoveStatus.UNKNOWN else status.value
    mock_cbox.fetch_info.return_value = build_info(status=status, rawStatus=raw)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get(CLIMATE)
    assert state.state == mode
    assert state.attributes[ATTR_HVAC_ACTION] == action


async def test_climate_commands(hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock) -> None:
    await hass.services.async_call(
        CLIMATE_DOMAIN, SERVICE_SET_TEMPERATURE, {ATTR_ENTITY_ID: CLIMATE, ATTR_TEMPERATURE: 22.4}, blocking=True
    )
    mock_cbox.change_temperature_setpoint.assert_awaited_once_with(22)

    await hass.services.async_call(
        CLIMATE_DOMAIN, SERVICE_SET_FAN_MODE, {ATTR_ENTITY_ID: CLIMATE, ATTR_FAN_MODE: "3"}, blocking=True
    )
    mock_cbox.change_fan_setpoint.assert_awaited_once_with(FanStatus.SPEED_3)

    await hass.services.async_call(
        CLIMATE_DOMAIN, SERVICE_SET_HVAC_MODE, {ATTR_ENTITY_ID: CLIMATE, ATTR_HVAC_MODE: HVACMode.OFF}, blocking=True
    )
    mock_cbox.power_off.assert_awaited_once()

    mock_cbox.fetch_info.return_value = build_info(status=StoveStatus.OFF, rawStatus=0)
    await hass.services.async_call(
        CLIMATE_DOMAIN, SERVICE_SET_HVAC_MODE, {ATTR_ENTITY_ID: CLIMATE, ATTR_HVAC_MODE: HVACMode.HEAT}, blocking=True
    )
    mock_cbox.power_on.assert_awaited_once()

    await hass.services.async_call(CLIMATE_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: CLIMATE}, blocking=True)
    assert mock_cbox.power_off.await_count == 2


async def test_command_error(hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock) -> None:
    mock_cbox.power_off.side_effect = CboxCommandError
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            {ATTR_ENTITY_ID: CLIMATE, ATTR_HVAC_MODE: HVACMode.OFF},
            blocking=True,
        )


async def test_power_number(hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock) -> None:
    entity_id = "number.pellet_stove_power_level"
    assert hass.states.get(entity_id).state == "3"
    await hass.services.async_call(
        NUMBER_DOMAIN, SERVICE_SET_VALUE, {ATTR_ENTITY_ID: entity_id, ATTR_VALUE: 5}, blocking=True
    )
    mock_cbox.change_power_setpoint.assert_awaited_once_with(5)


async def test_sensors(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    assert hass.states.get("sensor.pellet_stove_status").state == "burning"
    assert hass.states.get("sensor.pellet_stove_pellet_consumption").state == "42"
    assert hass.states.get("sensor.pellet_stove_probe_t3_temperature") is None  # disabled by default
    assert hass.states.get("binary_sensor.pellet_stove_alarm").state == STATE_OFF


async def test_alarm(hass: HomeAssistant, config_entry: MockConfigEntry, mock_cbox: AsyncMock) -> None:
    mock_cbox.fetch_info.return_value = build_info(status=StoveStatus.DOOR_ALARM, rawStatus=247)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get("binary_sensor.pellet_stove_alarm").state == STATE_ON
    assert hass.states.get("sensor.pellet_stove_status").state == "door_alarm"


def test_status_options_are_translated() -> None:
    translations = Path(__file__).parents[1] / "custom_components/cbox/translations"
    status = next(description for description in SENSORS if description.key == "status")
    for file in translations.glob("*.json"):
        states = json.loads(file.read_text())["entity"]["sensor"]["status"]["state"]
        assert set(states) == set(status.options), file.name
