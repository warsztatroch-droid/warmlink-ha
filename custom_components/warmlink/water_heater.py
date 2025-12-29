"""Water heater platform for Warmlink integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import DOMAIN
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

# Water heater operation modes
OPERATION_MODES = ["eco", "boost", "off"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink water heater entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    
    entities = []
    for device_code, device_data in coordinator.data.items():
        # Only add water heater if device has T04 (tank temperature)
        parsed_data = device_data.get("_parsed_data", {})
        if "T04" in parsed_data or "R01" in parsed_data:
            entities.append(
                WarmLinkWaterHeater(
                    coordinator=coordinator,
                    device_code=device_code,
                    device_data=device_data,
                )
            )
    
    async_add_entities(entities)


class WarmLinkWaterHeater(CoordinatorEntity[WarmLinkCoordinator], WaterHeaterEntity):
    """Representation of a Warmlink water heater (hot water tank).
    
    VERIFIED: Uses _parsed_data for temperatures.
    """

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_operation_list = OPERATION_MODES
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _attr_min_temp = 35
    _attr_max_temp = 60

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        device_code: str,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the water heater entity."""
        super().__init__(coordinator)
        
        self._device_code = device_code
        
        device_name = device_data.get("device_nick_name") or device_data.get("deviceNickName") or device_code
        model = device_data.get("custModel") or device_data.get("productId") or "Heat Pump"
        
        self._attr_unique_id = f"{DOMAIN}_{device_code}_water_heater"
        self._attr_name = "Zasobnik CWU"
        
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
    def available(self) -> bool:
        """Return True if device is online."""
        device = self.coordinator.data.get(self._device_code, {})
        return is_device_online(device) and super().available

    @property
    def current_temperature(self) -> float | None:
        """Return the current tank temperature.
        
        VERIFIED: T04 is tank temperature.
        """
        data = self._get_parsed_data()
        temp = data.get("T04")
        
        if temp is not None:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target hot water temperature.
        
        VERIFIED: R01 is water setpoint.
        """
        data = self._get_parsed_data()
        temp = data.get("R01")
        
        if temp is not None:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def current_operation(self) -> str | None:
        """Return current operation mode.
        
        VERIFIED: Power and Mode from _parsed_data.
        """
        data = self._get_parsed_data()
        
        power = data.get("Power")
        mode = data.get("Mode")
        
        if power == 0 or power == "0":
            return "off"
        
        # Modes 3, 4, 5 include hot water
        if mode in (3, 4, 5, "3", "4", "5"):
            return "eco"
        
        return "off"

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target hot water temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            # Set R01 - water setpoint
            await self.coordinator.api.set_temperature(
                self._device_code, "R01", temperature
            )
            await self.coordinator.async_request_refresh()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode."""
        if operation_mode == "off":
            # Turn off device
            await self.coordinator.api.set_power(self._device_code, False)
        elif operation_mode == "eco":
            # Enable hot water mode (mode 3)
            await self.coordinator.api.set_power(self._device_code, True)
            await self.coordinator.api.set_mode(self._device_code, "3")
        elif operation_mode == "boost":
            # Enable high temp disinfection - mode 3 + high setpoint
            await self.coordinator.api.set_power(self._device_code, True)
            await self.coordinator.api.set_mode(self._device_code, "3")
            # TODO: Set high temperature for disinfection if needed
        
        await self.coordinator.async_request_refresh()
