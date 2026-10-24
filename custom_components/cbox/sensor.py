"""Sensor entities for the cBox integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from connbox import CboxInfo, StoveStatus
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfMass, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import CboxConfigEntry, CboxCoordinator
from .entity import CboxEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class CboxSensorEntityDescription(SensorEntityDescription):
    """Describe a cBox sensor."""

    value_fn: Callable[[CboxInfo], StateType]


def _probe(key: str, attr: str) -> CboxSensorEntityDescription:
    return CboxSensorEntityDescription(
        key=key,
        translation_key=key,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda info: getattr(info, attr),
    )


SENSORS: tuple[CboxSensorEntityDescription, ...] = (
    CboxSensorEntityDescription(
        key="status",
        translation_key="status",
        device_class=SensorDeviceClass.ENUM,
        options=[status.name.lower() for status in StoveStatus],
        value_fn=lambda info: info.status.name.lower(),
    ),
    CboxSensorEntityDescription(
        key="pellet_consumption",
        translation_key="pellet_consumption",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda info: info.pelletQttyTotalKg,
    ),
    _probe("temperature_2", "t2"),
    _probe("temperature_3", "t3"),
    _probe("temperature_4", "t4"),
    _probe("temperature_5", "t5"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CboxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the stove sensors."""
    async_add_entities(CboxSensor(entry.runtime_data, description) for description in SENSORS)


class CboxSensor(CboxEntity, SensorEntity):
    """A value reported by the stove."""

    entity_description: CboxSensorEntityDescription

    def __init__(self, coordinator: CboxCoordinator, description: CboxSensorEntityDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data)
