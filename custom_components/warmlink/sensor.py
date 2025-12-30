"""Sensor platform for Warmlink integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfVolumeFlowRate,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import DOMAIN, CONF_LANGUAGE, ALL_SENSOR_PARAMS
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class WarmLinkSensorEntityDescription(SensorEntityDescription):
    """Describes Warmlink sensor entity with translation key."""

    translation_key_id: str | None = None


# All sensor descriptions based on Modbus CSV mapping
SENSOR_DESCRIPTIONS: tuple[WarmLinkSensorEntityDescription, ...] = (
    # === TEMPERATURE SENSORS (from Modbus registers 2045-2068) ===
    WarmLinkSensorEntityDescription(
        key="T01",
        translation_key="t01",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
    ),
    WarmLinkSensorEntityDescription(
        key="T02",
        translation_key="t02",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
    ),
    WarmLinkSensorEntityDescription(
        key="T03",
        translation_key="t03",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T04",
        translation_key="t04",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    WarmLinkSensorEntityDescription(
        key="T05",
        translation_key="t05",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T06",
        translation_key="t06",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake-alert",
    ),
    WarmLinkSensorEntityDescription(
        key="T07",
        translation_key="t07",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-thermometer",
    ),
    WarmLinkSensorEntityDescription(
        key="T08",
        translation_key="t08",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-boiler",
    ),
    WarmLinkSensorEntityDescription(
        key="T09",
        translation_key="t09",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer",
    ),
    WarmLinkSensorEntityDescription(
        key="T10",
        translation_key="t10",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T11",
        translation_key="t11",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T12",
        translation_key="t12",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-high",
    ),
    WarmLinkSensorEntityDescription(
        key="T14",
        translation_key="t14",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T49",
        translation_key="t49",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T50",
        translation_key="t50",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T51",
        translation_key="t51",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T55",
        translation_key="t55",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    
    # === SETPOINT SENSORS ===
    WarmLinkSensorEntityDescription(
        key="R01",
        translation_key="r01",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
    ),
    WarmLinkSensorEntityDescription(
        key="R02",
        translation_key="r02",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radiator",
    ),
    WarmLinkSensorEntityDescription(
        key="R03",
        translation_key="r03",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake-thermometer",
    ),
    WarmLinkSensorEntityDescription(
        key="R70",
        translation_key="r70",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer-outline",
    ),
    
    # === PRESSURE SENSOR ===
    WarmLinkSensorEntityDescription(
        key="T15",
        translation_key="t15",
        native_unit_of_measurement="bar",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge-low",
    ),
    
    # === COMPRESSOR AND FAN SENSORS ===
    WarmLinkSensorEntityDescription(
        key="T27",
        translation_key="t27",
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    WarmLinkSensorEntityDescription(
        key="T28",
        translation_key="t28",
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    WarmLinkSensorEntityDescription(
        key="T29",
        translation_key="t29",
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    WarmLinkSensorEntityDescription(
        key="T30",
        translation_key="t30",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    WarmLinkSensorEntityDescription(
        key="T31",
        translation_key="t31",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    WarmLinkSensorEntityDescription(
        key="T32",
        translation_key="t32",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    
    # === ELECTRICAL SENSORS ===
    WarmLinkSensorEntityDescription(
        key="T34",
        translation_key="t34",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T35",
        translation_key="t35",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T36",
        translation_key="t36",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T37",
        translation_key="t37",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="T38",
        translation_key="t38",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
    ),
    
    # === FLOW SENSOR ===
    WarmLinkSensorEntityDescription(
        key="T39",
        translation_key="t39",
        native_unit_of_measurement="L/min",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-pump",
    ),
    
    # === ENERGY AND POWER SENSORS ===
    WarmLinkSensorEntityDescription(
        key="Power In(Total)",
        translation_key="power_in_total",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    WarmLinkSensorEntityDescription(
        key="Capacity Out(Total)",
        translation_key="capacity_out_total",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
    ),
    WarmLinkSensorEntityDescription(
        key="COP/EER(Total)",
        translation_key="cop_eer_total",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    WarmLinkSensorEntityDescription(
        key="Power In(ODU)",
        translation_key="power_in_odu",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="Capacity Out(ODU)",
        translation_key="capacity_out_odu",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="Heating Con.(ODU)",
        translation_key="heating_consumption",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    WarmLinkSensorEntityDescription(
        key="Heating Gen.(ODU)",
        translation_key="heating_generated",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    WarmLinkSensorEntityDescription(
        key="Cooling Con.(ODU)",
        translation_key="cooling_consumption",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    WarmLinkSensorEntityDescription(
        key="Cooling Gen.(ODU)",
        translation_key="cooling_generated",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    WarmLinkSensorEntityDescription(
        key="DHW Con.(ODU)",
        translation_key="dhw_consumption",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    WarmLinkSensorEntityDescription(
        key="DHW Gen.(ODU)",
        translation_key="dhw_generated",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    WarmLinkSensorEntityDescription(
        key="Comsuption Power",
        translation_key="consumption_power",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    
    # === STATUS SENSORS ===
    WarmLinkSensorEntityDescription(
        key="ModeState",
        translation_key="mode_state",
        native_unit_of_measurement=None,
        icon="mdi:information-outline",
    ),
    
    # === VERSION SENSORS ===
    WarmLinkSensorEntityDescription(
        key="code_version",
        translation_key="code_version",
        native_unit_of_measurement=None,
        icon="mdi:tag",
    ),
    WarmLinkSensorEntityDescription(
        key="MainBoard Version",
        translation_key="mainboard_version",
        native_unit_of_measurement=None,
        icon="mdi:chip",
    ),
    WarmLinkSensorEntityDescription(
        key="DisplayVer",
        translation_key="display_version",
        native_unit_of_measurement=None,
        icon="mdi:monitor",
    ),
    
    # === ZONE SENSORS ===
    WarmLinkSensorEntityDescription(
        key="Zone 1 Room Temp",
        translation_key="zone1_room_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer",
    ),
    WarmLinkSensorEntityDescription(
        key="Zone 2 Room Temp",
        translation_key="zone2_room_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer",
    ),
    WarmLinkSensorEntityDescription(
        key="Zone 2 Mixing Temp",
        translation_key="zone2_mixing_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="Zone 2 Mixing Valve",
        translation_key="zone2_mixing_valve",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:valve",
    ),
    
    # === INDOOR CLIMATE SENSORS ===
    WarmLinkSensorEntityDescription(
        key="DP4",
        translation_key="indoor_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="DP5",
        translation_key="indoor_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WarmLinkSensorEntityDescription(
        key="DP6",
        translation_key="dew_point_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

# Operating mode mapping
MODE_STATE_MAP = {
    "0": "Cooling",
    "1": "Heating",
    "2": "Defrost",
    "3": "Disinfection",
    "4": "Hot Water",
}

MODE_STATE_MAP_PL = {
    "0": "Chłodzenie",
    "1": "Grzanie",
    "2": "Odszranianie",
    "3": "Dezynfekcja",
    "4": "Ciepła woda",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    language = entry.data.get(CONF_LANGUAGE, "en")
    
    entities = []
    
    # Track which keys we've added from SENSOR_DESCRIPTIONS
    added_keys = set()
    
    for device_code, device_data in coordinator.data.items():
        # Add predefined sensors with full descriptions
        for description in SENSOR_DESCRIPTIONS:
            added_keys.add(description.key)
            entities.append(
                WarmLinkSensor(
                    coordinator=coordinator,
                    device_code=device_code,
                    device_data=device_data,
                    description=description,
                    language=language,
                )
            )
        
        # Add dynamic sensors from ALL_SENSOR_PARAMS that aren't in SENSOR_DESCRIPTIONS
        for code, param_info in ALL_SENSOR_PARAMS.items():
            if code in added_keys:
                continue  # Skip if already added with predefined description
            
            entities.append(
                WarmLinkDynamicSensor(
                    coordinator=coordinator,
                    device_code=device_code,
                    device_data=device_data,
                    param_code=code,
                    param_info=param_info,
                    language=language,
                )
            )
    
    async_add_entities(entities)


class WarmLinkSensor(CoordinatorEntity[WarmLinkCoordinator], SensorEntity):
    """Representation of a Warmlink sensor."""

    _attr_has_entity_name = True
    entity_description: WarmLinkSensorEntityDescription

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        device_code: str,
        device_data: dict[str, Any],
        description: WarmLinkSensorEntityDescription,
        language: str = "en",
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self.entity_description = description
        self._device_code = device_code
        self._language = language
        
        device_name = device_data.get("device_nick_name") or device_data.get("deviceNickName") or device_code
        model = device_data.get("custModel") or device_data.get("productId") or "Heat Pump"
        
        self._attr_unique_id = f"{DOMAIN}_{device_code}_{description.key}"
        self._attr_translation_key = description.translation_key
        
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
        """Return the sensor value."""
        data = self._get_parsed_data()
        value = data.get(self.entity_description.key)
        
        if value is None:
            return None
        
        # Handle ModeState with translation
        if self.entity_description.key == "ModeState":
            mode_map = MODE_STATE_MAP_PL if self._language == "pl" else MODE_STATE_MAP
            return mode_map.get(str(value), str(value))
        
        # Values are already floats from coordinator
        if isinstance(value, (int, float)):
            return value
        
        # Try to convert string to float for numeric sensors
        if self.entity_description.device_class in [
            SensorDeviceClass.TEMPERATURE,
            SensorDeviceClass.POWER,
            SensorDeviceClass.ENERGY,
            SensorDeviceClass.VOLTAGE,
            SensorDeviceClass.CURRENT,
            SensorDeviceClass.PRESSURE,
        ]:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        return value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator.data.get(self._device_code, {})
        
        # Check if device is online
        if not is_device_online(device):
            return False
        
        # Check if we have data for this sensor
        data = device.get("_parsed_data", {})
        return self.entity_description.key in data and super().available


class WarmLinkDynamicSensor(CoordinatorEntity[WarmLinkCoordinator], SensorEntity):
    """Dynamic sensor created from ALL_SENSOR_PARAMS (Modbus CSV).
    
    Creates sensors for all parameters from modbus_params.py that don't have
    explicit SENSOR_DESCRIPTIONS entries.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        device_code: str,
        device_data: dict[str, Any],
        param_code: str,
        param_info: dict[str, Any],
        language: str = "en",
    ) -> None:
        """Initialize the dynamic sensor."""
        super().__init__(coordinator)
        
        self._device_code = device_code
        self._param_code = param_code
        self._param_info = param_info
        self._language = language
        
        device_name = device_data.get("device_nick_name") or device_data.get("deviceNickName") or device_code
        model = device_data.get("custModel") or device_data.get("productId") or "Heat Pump"
        
        self._attr_unique_id = f"{DOMAIN}_{device_code}_{param_code}"
        
        # Create name with code prefix: "(T01) Inlet Water Temp"
        param_name = param_info.get("name", param_code)
        self._attr_name = f"({param_code}) {param_name}"
        
        # Determine device class and unit from param_info
        unit = param_info.get("unit", "")
        data_type = param_info.get("data_type", "")
        category = param_info.get("category", "")
        
        self._setup_sensor_properties(unit, data_type, category)
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_code)},
            "name": device_name,
            "manufacturer": "Phinx/Warmlink",
            "model": model,
        }

    def _setup_sensor_properties(self, unit: str, data_type: str, category: str) -> None:
        """Set up sensor properties based on param info."""
        # Map units to HA units and device classes
        if unit == "°C" or data_type == "TEMP":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "Hz":
            self._attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:sine-wave"
        elif unit == "V":
            self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
            self._attr_device_class = SensorDeviceClass.VOLTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "A":
            self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
            self._attr_device_class = SensorDeviceClass.CURRENT
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "kW":
            self._attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "kWh":
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif unit == "L/min":
            self._attr_native_unit_of_measurement = "L/min"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:water-pump"
        elif unit == "bar":
            self._attr_native_unit_of_measurement = "bar"
            self._attr_device_class = SensorDeviceClass.PRESSURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "rpm":
            self._attr_native_unit_of_measurement = "rpm"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:fan"
        elif unit == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "min":
            self._attr_native_unit_of_measurement = "min"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:timer-outline"
        elif unit == "steps":
            self._attr_native_unit_of_measurement = "steps"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:stairs"
        else:
            # Default for unknown units
            self._attr_state_class = SensorStateClass.MEASUREMENT
            if category == "temperatures":
                self._attr_icon = "mdi:thermometer"
            elif category == "compressor":
                self._attr_icon = "mdi:engine"
            elif category == "fan":
                self._attr_icon = "mdi:fan"
            elif category == "pump":
                self._attr_icon = "mdi:water-pump"
            elif category == "defrost":
                self._attr_icon = "mdi:snowflake"
            elif category == "zones":
                self._attr_icon = "mdi:home-thermometer"

    def _get_parsed_data(self) -> dict[str, Any]:
        """Get parsed data from coordinator."""
        device = self.coordinator.data.get(self._device_code, {})
        return device.get("_parsed_data", {})

    @property
    def native_value(self) -> float | str | None:
        """Return the sensor value."""
        data = self._get_parsed_data()
        value = data.get(self._param_code)
        
        if value is None:
            return None
        
        # Values are already floats from coordinator
        if isinstance(value, (int, float)):
            return value
        
        # Try to convert string to float
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator.data.get(self._device_code, {})
        
        # Check if device is online
        if not is_device_online(device):
            return False
        
        # Check if we have data for this sensor
        data = device.get("_parsed_data", {})
        return self._param_code in data and super().available
