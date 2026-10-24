"""Tests for the cBox setup and coordinator."""

from unittest.mock import AsyncMock

from connbox import CboxConnectionError
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.cbox.const import DEFAULT_SCAN_INTERVAL


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


async def test_entities_unavailable_when_update_fails(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock, freezer: FrozenDateTimeFactory
) -> None:
    mock_cbox.fetch_info.side_effect = CboxConnectionError
    freezer.tick(DEFAULT_SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get("climate.pellet_stove").state == STATE_UNAVAILABLE
