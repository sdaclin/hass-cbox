"""Diagnostics support for the cBox integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .coordinator import CboxConfigEntry

TO_REDACT = {"MAC"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: CboxConfigEntry) -> dict[str, Any]:
    """Return the raw GET ALLS answer of the cBox."""
    raw = await entry.runtime_data.cbox.get_info("ALLS")
    return {
        "firmware_version": entry.runtime_data.data.firmwareVersion,
        "raw_status": entry.runtime_data.data.rawStatus,
        "get_alls": {**raw, "DATA": async_redact_data(raw.get("DATA", {}), TO_REDACT)},
    }
