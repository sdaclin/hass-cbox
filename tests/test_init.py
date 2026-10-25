"""Tests for the cBox setup and coordinator."""

from unittest.mock import AsyncMock

from connbox import CboxConnectionError
from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.climate import HVACMode
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_TEMPERATURE, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.cbox.const import DEFAULT_SCAN_INTERVAL, MAX_TOLERATED_FAILURES

from .conftest import build_info

CLIMATE = "climate.pellet_stove"


async def test_setup_and_unload(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    assert init_integration.state is ConfigEntryState.LOADED
    await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()
    assert init_integration.state is ConfigEntryState.NOT_LOADED


async def test_setup_retry_when_unreachable(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_cbox: AsyncMock
) -> None:
    mock_cbox.fetch_info.side_effect = CboxConnectionError
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def _poll(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    freezer.tick(DEFAULT_SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done(wait_background_tasks=True)


async def test_failed_poll_is_retried(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock, freezer: FrozenDateTimeFactory
) -> None:
    mock_cbox.fetch_info.side_effect = [CboxConnectionError, build_info(temperatureSetpoint=23)]
    await _poll(hass, freezer)
    assert hass.states.get(CLIMATE).attributes[ATTR_TEMPERATURE] == 23


async def test_last_state_kept_while_failures_are_tolerated(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock, freezer: FrozenDateTimeFactory
) -> None:
    mock_cbox.fetch_info.side_effect = CboxConnectionError
    for _ in range(MAX_TOLERATED_FAILURES):
        await _poll(hass, freezer)
        assert hass.states.get(CLIMATE).state == HVACMode.HEAT

    await _poll(hass, freezer)
    assert hass.states.get(CLIMATE).state == STATE_UNAVAILABLE


async def test_failures_reset_after_success(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock, freezer: FrozenDateTimeFactory
) -> None:
    mock_cbox.fetch_info.side_effect = CboxConnectionError
    for _ in range(MAX_TOLERATED_FAILURES):
        await _poll(hass, freezer)

    mock_cbox.fetch_info.side_effect = None
    await _poll(hass, freezer)

    mock_cbox.fetch_info.side_effect = CboxConnectionError
    for _ in range(MAX_TOLERATED_FAILURES):
        await _poll(hass, freezer)
        assert hass.states.get(CLIMATE).state == HVACMode.HEAT
