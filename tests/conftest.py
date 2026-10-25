"""Fixtures for the cBox tests."""

from collections.abc import Generator
from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from connbox import CboxInfo, FanStatus, StoveStatus
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cbox.const import DOMAIN

HOST = "192.168.1.20"
MAC = "aa:bb:cc:dd:ee:ff"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations in all tests."""


@pytest.fixture(autouse=True)
def no_retry_delay() -> Generator[None]:
    """Don't wait between poll retries."""
    with patch("custom_components.cbox.coordinator.RETRY_DELAY", 0):
        yield


def build_info(**overrides) -> CboxInfo:
    info = CboxInfo(
        timestamp=datetime(2026, 10, 24, 10, 0),
        mac=MAC.upper(),
        status=StoveStatus.BURNING,
        fanSetpoint=FanStatus.AUTO,
        powerSetpoint=3,
        temperatureSetpoint=21,
        t1=19.6,
        t2=0,
        t3=133,
        t4=0,
        t5=49,
        pelletQttyTotalKg=42,
        firmwareVersion=48,
        firmwareDate=date(2023, 7, 26),
        rawStatus=StoveStatus.BURNING.value,
    )
    for key, value in overrides.items():
        setattr(info, key, value)
    return info


@pytest.fixture
def mock_cbox() -> Generator[AsyncMock]:
    """Mock the connbox client used by the integration and the config flow."""
    with (
        patch("custom_components.cbox.Cbox", autospec=True) as cbox_class,
        patch("custom_components.cbox.config_flow.Cbox", new=cbox_class),
    ):
        cbox = cbox_class.return_value
        cbox.fetch_info.return_value = build_info()
        cbox.get_info.return_value = {"SUCCESS": True, "DATA": {"MAC": MAC.upper(), "STATUS": 6}}
        yield cbox


@pytest.fixture
def config_entry() -> MockConfigEntry:
    return MockConfigEntry(domain=DOMAIN, title="Pellet stove", data={CONF_HOST: HOST}, unique_id=MAC)


@pytest.fixture
async def init_integration(hass: HomeAssistant, config_entry: MockConfigEntry, mock_cbox: AsyncMock) -> MockConfigEntry:
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
