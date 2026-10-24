"""The cBox (Fumis Alpha pellet stove) integration."""

from __future__ import annotations

from connbox import Cbox
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import CboxConfigEntry, CboxCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: CboxConfigEntry) -> bool:
    """Set up cBox from a config entry."""
    cbox = Cbox(async_get_clientsession(hass), entry.data[CONF_HOST])
    coordinator = CboxCoordinator(hass, entry, cbox)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: CboxConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
