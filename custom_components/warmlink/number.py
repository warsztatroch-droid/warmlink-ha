"""Number platform for Warmlink integration - temperature setpoints and parameters."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import DOMAIN, CONF_LANGUAGE, WRITABLE_PARAMS
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

# Translation keys for number entities
NUMBER_TRANSLATIONS = {
    "en": {
        "R01": "DHW Target Temperature",
        "R02": "Heating Target Temperature",
        "R03": "Cooling Target Temperature",
        "R70": "Room Target Temperature",
        "R04": "Heating On Difference",
        "R05": "Heating Standby Difference",
        "R06": "Cooling On Difference",
        "R07": "Cooling Standby Difference",
        "R16": "DHW On Difference",
        "R17": "DHW Standby Difference",
        "Z02": "Zone 1 Target Room Temp",
        "Z04": "Zone 2 Target Room Temp",
        "G01": "Disinfection Temperature",
        "G02": "Disinfection Duration",
        "G04": "Disinfection Interval",
        "F18": "Min Fan Speed Cooling",
        "F19": "Min Fan Speed Heating",
        "F25": "Max Fan Speed Cooling",
        "F26": "Max Fan Speed Heating",
        "D01": "Defrost Start Temperature",
        "D03": "Defrost Interval",
        "D19": "Max Defrost Time",
        "C02": "Min Compressor Frequency",
        "C03": "Max Compressor Frequency",
    },
    "pl": {
        "R01": "Temperatura zadana CWU",
        "R02": "Temperatura zadana ogrzewania",
        "R03": "Temperatura zadana chłodzenia",
        "R70": "Temperatura zadana pokojowa",
        "R04": "Różnica włączenia ogrzewania",
        "R05": "Różnica standby ogrzewania",
        "R06": "Różnica włączenia chłodzenia",
        "R07": "Różnica standby chłodzenia",
        "R16": "Różnica włączenia CWU",
        "R17": "Różnica standby CWU",
        "Z02": "Strefa 1 temperatura pokojowa",
        "Z04": "Strefa 2 temperatura pokojowa",
        "G01": "Temperatura dezynfekcji",
        "G02": "Czas dezynfekcji",
        "G04": "Interwał dezynfekcji",
        "F18": "Min obroty wentylatora chłodzenie",
        "F19": "Min obroty wentylatora grzanie",
        "F25": "Max obroty wentylatora chłodzenie",
        "F26": "Max obroty wentylatora grzanie",
        "D01": "Temperatura startu odszraniania",
        "D03": "Interwał odszraniania",
        "D19": "Max czas odszraniania",
        "C02": "Min częstotliwość sprężarki",
        "C03": "Max częstotliwość sprężarki",
    },
}

# Icons for number entities
NUMBER_ICONS = {
    "R01": "mdi:water-thermometer",
    "R02": "mdi:radiator",
    "R03": "mdi:snowflake-thermometer",
    "R70": "mdi:home-thermometer",
    "R04": "mdi:thermometer-plus",
    "R05": "mdi:thermometer-minus",
    "R06": "mdi:thermometer-plus",
    "R07": "mdi:thermometer-minus",
    "R16": "mdi:thermometer-plus",
    "R17": "mdi:thermometer-minus",
    "Z02": "mdi:home-thermometer-outline",
    "Z04": "mdi:home-thermometer-outline",
    "G01": "mdi:bacteria-outline",
    "G02": "mdi:timer-outline",
    "G04": "mdi:calendar-clock",
    "F18": "mdi:fan-speed-1",
    "F19": "mdi:fan-speed-1",
    "F25": "mdi:fan-speed-3",
    "F26": "mdi:fan-speed-3",
    "D01": "mdi:snowflake-thermometer",
    "D03": "mdi:timer-sand",
    "D19": "mdi:timer-outline",
    "C02": "mdi:sine-wave",
    "C03": "mdi:sine-wave",
}

# Primary setpoints to show by default (others are diagnostics)
PRIMARY_SETPOINTS = ["R01", "R02", "R03", "R70"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink number entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    api = data["api"]
    language = entry.data.get(CONF_LANGUAGE, "en")

    entities = []
    for device_code, device_data in coordinator.data.items():
        for param_code, param_info in WRITABLE_PARAMS.items():
            # Check if device has this parameter
            parsed_data = device_data.get("_parsed_data", {})
            if param_code in parsed_data or param_code in PRIMARY_SETPOINTS:
                entities.append(
                    WarmLinkNumber(
                        coordinator=coordinator,
                        api=api,
                        device_code=device_code,
                        device_data=device_data,
                        param_code=param_code,
                        param_info=param_info,
                        language=language,
                    )
                )

    async_add_entities(entities)


class WarmLinkNumber(CoordinatorEntity[WarmLinkCoordinator], NumberEntity):
    """Representation of a Warmlink number entity for setpoints."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        api,
        device_code: str,
        device_data: dict[str, Any],
        param_code: str,
        param_info: dict[str, Any],
        language: str = "en",
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)

        self._api = api
        self._device_code = device_code
        self._param_code = param_code
        self._param_info = param_info
        self._language = language

        device_name = (
            device_data.get("device_nick_name")
            or device_data.get("deviceNickName")
            or device_code
        )
        model = device_data.get("custModel") or device_data.get("productId") or "Heat Pump"

        self._attr_unique_id = f"{DOMAIN}_{device_code}_{param_code}"
        
        # Get translated name
        translations = NUMBER_TRANSLATIONS.get(language, NUMBER_TRANSLATIONS["en"])
        self._attr_name = translations.get(param_code, param_info.get("name", param_code))

        # Set number attributes
        self._attr_native_min_value = param_info.get("min", 0)
        self._attr_native_max_value = param_info.get("max", 100)
        self._attr_native_step = param_info.get("step", 0.5)
        self._attr_mode = NumberMode.SLIDER if param_code in PRIMARY_SETPOINTS else NumberMode.BOX
        self._attr_icon = NUMBER_ICONS.get(param_code, "mdi:thermometer")

        # Set device class and unit based on param type
        unit = param_info.get("unit", "")
        if unit == "°C":
            self._attr_device_class = NumberDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif unit == "Hz":
            self._attr_native_unit_of_measurement = "Hz"
        elif unit == "rpm":
            self._attr_native_unit_of_measurement = "rpm"
        elif unit == "min":
            self._attr_native_unit_of_measurement = "min"
        elif unit == "days":
            self._attr_native_unit_of_measurement = "days"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_code)},
            "name": device_name,
            "manufacturer": "Phinx/Warmlink",
            "model": model,
        }

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        device = self.coordinator.data.get(self._device_code, {})
        parsed_data = device.get("_parsed_data", {})
        value = parsed_data.get(self._param_code)

        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator.data.get(self._device_code, {})
        return is_device_online(device) and super().available

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.info(
            "Setting %s to %.1f for device %s",
            self._param_code,
            value,
            self._device_code,
        )

        success = await self._api.set_temperature(
            self._device_code, self._param_code, value
        )

        if success:
            # Optimistically update the value
            device = self.coordinator.data.get(self._device_code, {})
            parsed_data = device.get("_parsed_data", {})
            parsed_data[self._param_code] = value
            self.async_write_ha_state()

            # Request a refresh
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set %s", self._param_code)
