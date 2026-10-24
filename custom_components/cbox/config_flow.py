"""Config flow for the cBox integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from connbox import Cbox, CboxError, CboxInfo
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .const import DOMAIN, LOGGER

DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


class CboxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for cBox."""

    VERSION = 1

    async def _async_fetch_info(self, host: str, errors: dict[str, str]) -> CboxInfo | None:
        try:
            return await Cbox(async_get_clientsession(self.hass), host).fetch_info()
        except CboxError:
            errors["base"] = "cannot_connect"
        except Exception:
            LOGGER.exception("Unexpected error while connecting to the cBox")
            errors["base"] = "unknown"
        return None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None and (info := await self._async_fetch_info(user_input[CONF_HOST], errors)):
            await self.async_set_unique_id(format_mac(info.mac))
            self._abort_if_unique_id_configured(updates=user_input)
            return self.async_create_entry(title="Pellet stove", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(DATA_SCHEMA, user_input),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a host change."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()
        if user_input is not None and (info := await self._async_fetch_info(user_input[CONF_HOST], errors)):
            await self.async_set_unique_id(format_mac(info.mac))
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(entry, data_updates=user_input)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(DATA_SCHEMA, user_input or entry.data),
            errors=errors,
        )
