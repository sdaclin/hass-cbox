"""Data update coordinator for the cBox integration."""

from __future__ import annotations

import asyncio

from connbox import Cbox, CboxError, CboxInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER, MAX_TOLERATED_FAILURES, RETRY_DELAY

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
        self._failures = 0

    async def _async_update_data(self) -> CboxInfo:
        try:
            info = await self._fetch_info_with_retry()
        except CboxError as err:
            self._failures += 1
            if self.data is not None and self._failures <= MAX_TOLERATED_FAILURES:
                LOGGER.debug("Keeping last known state after %s failed poll(s): %s", self._failures, err)
                return self.data
            raise UpdateFailed(f"Error communicating with the cBox: {err}") from err
        self._failures = 0
        return info

    async def _fetch_info_with_retry(self) -> CboxInfo:
        try:
            return await self.cbox.fetch_info()
        except CboxError as err:
            LOGGER.debug("Poll failed, retrying in %s s: %s", RETRY_DELAY, err)
        await asyncio.sleep(RETRY_DELAY)
        return await self.cbox.fetch_info()
