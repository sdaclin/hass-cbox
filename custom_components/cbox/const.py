"""Constants for the cBox integration."""

from datetime import timedelta
from logging import Logger, getLogger

from connbox import FanStatus, StoveStatus

DOMAIN = "cbox"
LOGGER: Logger = getLogger(__package__)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

MIN_TEMPERATURE = 12
MAX_TEMPERATURE = 50
MIN_POWER = 1
MAX_POWER = 5

STATUSES_OFF = {StoveStatus.OFF, StoveStatus.OFF_TIMER}
STATUSES_HEATING = {
    StoveStatus.TESTFIRE,
    StoveStatus.HEATUP,
    StoveStatus.FUELIGN,
    StoveStatus.IGNTEST,
    StoveStatus.BURNING,
}

FAN_MODES: dict[str, FanStatus] = {
    "off": FanStatus.OFF,
    "1": FanStatus.SPEED_1,
    "2": FanStatus.SPEED_2,
    "3": FanStatus.SPEED_3,
    "4": FanStatus.SPEED_4,
    "5": FanStatus.SPEED_5,
    "high": FanStatus.HIGH,
    "auto": FanStatus.AUTO,
}
