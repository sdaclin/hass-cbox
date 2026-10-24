"""Tests for the cBox config flow."""

from unittest.mock import AsyncMock

import pytest
from connbox import CboxConnectionError
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cbox.const import DOMAIN

from .conftest import HOST, MAC, build_info


async def test_user_flow(hass: HomeAssistant, mock_cbox: AsyncMock) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: HOST})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_HOST: HOST}
    assert result["result"].unique_id == MAC


@pytest.mark.parametrize(("error", "reason"), [(CboxConnectionError, "cannot_connect"), (RuntimeError, "unknown")])
async def test_user_flow_errors(hass: HomeAssistant, mock_cbox: AsyncMock, error: type[Exception], reason: str) -> None:
    mock_cbox.fetch_info.side_effect = error
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: HOST})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": reason}

    mock_cbox.fetch_info.side_effect = None
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: HOST})
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_already_configured(
    hass: HomeAssistant, mock_cbox: AsyncMock, config_entry: MockConfigEntry
) -> None:
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: "10.0.0.2"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert config_entry.data[CONF_HOST] == "10.0.0.2"


async def test_reconfigure_flow(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    result = await init_integration.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: "10.0.0.2"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert init_integration.data[CONF_HOST] == "10.0.0.2"


async def test_reconfigure_flow_other_device(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_cbox: AsyncMock
) -> None:
    mock_cbox.fetch_info.return_value = build_info(mac="11:22:33:44:55:66")
    result = await init_integration.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: "10.0.0.2"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unique_id_mismatch"
