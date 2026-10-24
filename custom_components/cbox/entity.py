"""Base entity for the cBox integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from connbox import CboxError
from homeassistant.const import CONF_HOST
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo, format_mac
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CboxCoordinator


class CboxEntity(CoordinatorEntity[CboxCoordinator]):
    """An entity attached to the stove device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: CboxCoordinator, key: str) -> None:
        super().__init__(coordinator)
        mac = format_mac(coordinator.data.mac)
        self._attr_unique_id = f"{mac}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            connections={(CONNECTION_NETWORK_MAC, mac)},
            manufacturer="Fumis",
            model="Connection Box",
            name="Pellet stove",
            sw_version=f"{coordinator.data.firmwareVersion} ({coordinator.data.firmwareDate})",
            configuration_url=f"http://{coordinator.config_entry.data[CONF_HOST]}",
        )

    async def _async_send(self, command: Callable[..., Awaitable[Any]], *args: Any) -> None:
        """Send a command to the stove then refresh its state."""
        try:
            await command(*args)
        except CboxError as err:
            raise HomeAssistantError(f"Error sending command to the cBox: {err}") from err
        await self.coordinator.async_refresh()
