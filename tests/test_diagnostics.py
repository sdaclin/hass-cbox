"""Tests for the cBox diagnostics."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cbox.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics_redact_mac(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    result = await async_get_config_entry_diagnostics(hass, init_integration)
    assert result["get_alls"]["DATA"]["MAC"] == "**REDACTED**"
    assert result["raw_status"] == 6
