"""Data update coordinator for the cBox integration."""

from __future__ import annotations

from connbox import Cbox, CboxError, CboxInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER

type CboxConfigEntry = ConfigEntry[CboxCoordinator]


class CboxCoordinator(DataUpdateCoordinator[CboxInfo]):
    """Poll the cBox with a single GET ALLS per update."""

    config_entry: CboxConfigEntry

    def __init__(self, hass: HomeAssistant, entry: CboxConfigEntry, cbox: Cbox) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.cbox = cbox

    async def _async_update_data(self) -> CboxInfo:
        try:
            return await self.cbox.fetch_info()
        except CboxError as err:
            raise UpdateFailed(f"Error communicating with the cBox: {err}") from err
