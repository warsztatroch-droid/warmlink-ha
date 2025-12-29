"""Sensor platform for Warmlink integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfPressure, UnitOfFrequency
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import DOMAIN
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

# Sensor descriptions based on Modbus CSV mapping and API testing
SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    # Temperature sensors - from Modbus registers 2045-2068
    SensorEntityDescription(
        key="T01",
        name="Inlet Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="T02",
        name="Outlet Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="T03",
        name="Coil Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="T04",
        name="Ambient Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="T05",
        name="Suction Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="T07",
        name="Buffer Tank Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="T08",
        name="DHW Tank Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-boiler",
    ),
    SensorEntityDescription(
        key="T09",
        name="Room Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer",
    ),
    SensorEntityDescription(
        key="T12",
        name="Exhaust Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Setpoint sensors
    SensorEntityDescription(
        key="R01",
        name="DHW Target Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
    ),
    SensorEntityDescription(
        key="R02",
        name="Heating Target Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radiator",
    ),
    SensorEntityDescription(
        key="R03",
        name="Cooling Target Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake-thermometer",
    ),
    SensorEntityDescription(
        key="R70",
        name="Room Target Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer-outline",
    ),
    # Compressor and system sensors
    SensorEntityDescription(
        key="T30",
        name="Compressor Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    SensorEntityDescription(
        key="T39",
        name="Water Flow Rate",
        native_unit_of_measurement="L/min",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-pump",
    ),
    # Energy and efficiency sensors
    SensorEntityDescription(
        key="Power In(Total)",
        name="Power Consumption",
        native_unit_of_measurement="kW",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SensorEntityDescription(
        key="Capacity Out(Total)",
        name="Heating Capacity",
        native_unit_of_measurement="kW",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
    ),
    SensorEntityDescription(
        key="COP/EER(Total)",
        name="COP / EER",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    
    entities = []
    for device_code, device_data in coordinator.data.items():
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                WarmLinkSensor(
                    coordinator=coordinator,
                    device_code=device_code,
                    device_data=device_data,
                    description=description,
                )
            )
    
    async_add_entities(entities)


class WarmLinkSensor(CoordinatorEntity[WarmLinkCoordinator], SensorEntity):
    """Representation of a Warmlink sensor.
    
    VERIFIED: Uses _parsed_data dict with keys like T01, T02, R01, etc.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        device_code: str,
        device_data: dict[str, Any],
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self.entity_description = description
        self._device_code = device_code
        
        device_name = device_data.get("device_nick_name") or device_data.get("deviceNickName") or device_code
        model = device_data.get("custModel") or device_data.get("productId") or "Heat Pump"
        
        self._attr_unique_id = f"{DOMAIN}_{device_code}_{description.key}"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_code)},
            "name": device_name,
            "manufacturer": "Phinx/Warmlink",
            "model": model,
        }

    def _get_parsed_data(self) -> dict[str, Any]:
        """Get parsed data from coordinator."""
        device = self.coordinator.data.get(self._device_code, {})
        return device.get("_parsed_data", {})

    @property
    def native_value(self) -> float | str | None:
        """Return the sensor value.
        
        VERIFIED: Values are already parsed to float in coordinator.
        """
        data = self._get_parsed_data()
        value = data.get(self.entity_description.key)
        
        if value is None:
            return None
        
        # Values are already floats from coordinator
        if isinstance(value, (int, float)):
            return value
        
        # Try to convert string to float for numeric sensors
        if self.entity_description.device_class == SensorDeviceClass.TEMPERATURE:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        return value

    @property
    def available(self) -> bool:
        """Return if entity is available.
        
        VERIFIED: Check if device is online and has the data key.
        """
        device = self.coordinator.data.get(self._device_code, {})
        
        # Check if device is online
        if not is_device_online(device):
            return False
        
        # Check if we have data for this sensor
        data = device.get("_parsed_data", {})
        return self.entity_description.key in data and super().available
