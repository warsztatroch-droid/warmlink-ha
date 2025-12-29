"""Climate platform for Warmlink integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import (
    DOMAIN,
    HVAC_MODE_OFF,
    HVAC_MODE_HEATING,
    HVAC_MODE_COOLING,
    HVAC_MODE_HOT_WATER,
    HVAC_MODE_HEATING_HOT_WATER,
    HVAC_MODE_COOLING_HOT_WATER,
)
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

# Map Warmlink modes to Home Assistant HVAC modes
WARMLINK_TO_HA_HVAC = {
    HVAC_MODE_OFF: HVACMode.OFF,
    HVAC_MODE_HEATING: HVACMode.HEAT,
    HVAC_MODE_COOLING: HVACMode.COOL,
    HVAC_MODE_HOT_WATER: HVACMode.HEAT,  # Hot water only
    HVAC_MODE_HEATING_HOT_WATER: HVACMode.HEAT,
    HVAC_MODE_COOLING_HOT_WATER: HVACMode.COOL,
}

HA_TO_WARMLINK_HVAC = {
    HVACMode.OFF: HVAC_MODE_OFF,
    HVACMode.HEAT: HVAC_MODE_HEATING,
    HVACMode.COOL: HVAC_MODE_COOLING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink climate entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    
    entities = []
    for device_code, device_data in coordinator.data.items():
        entities.append(
            WarmLinkClimate(
                coordinator=coordinator,
                device_code=device_code,
                device_data=device_data,
            )
        )
    
    async_add_entities(entities)


class WarmLinkClimate(CoordinatorEntity[WarmLinkCoordinator], ClimateEntity):
    """Representation of a Warmlink heat pump climate entity.
    
    VERIFIED: Uses _parsed_data dict with keys: Power, Mode, T01-T05, R01-R03
    """

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = 20
    _attr_max_temp = 55
    _attr_target_temperature_step = 1

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        device_code: str,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        
        self._device_code = device_code
        self._device_data = device_data
        
        # VERIFIED: API returns device_nick_name or deviceNickName
        device_name = device_data.get("device_nick_name") or device_data.get("deviceNickName") or device_code
        model = device_data.get("custModel") or device_data.get("productId") or "Heat Pump"
        
        self._attr_unique_id = f"{DOMAIN}_{device_code}_climate"
        self._attr_name = "Pompa ciepła"
        
        # Device info for grouping entities
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
        """Return the current temperature.
        
        VERIFIED: T02 = outlet temperature (water going to system)
        """
        data = self._get_parsed_data()
        temp = data.get("T02")  # Outlet temperature
        
        if temp is not None:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature.
        
        VERIFIED: R01 = water setpoint, R02 = room setpoint (if applicable)
        """
        data = self._get_parsed_data()
        
        # R01 is the main water temperature setpoint
        temp = data.get("R01")
        
        if temp is not None:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode.
        
        VERIFIED: Power (0/1), Mode (1=heating, 2=cooling, 3=hot_water, etc.)
        """
        data = self._get_parsed_data()
        
        # Check if device is powered on
        power = data.get("Power")
        if power == 0 or power == "0":
            return HVACMode.OFF
        
        # Get current mode
        mode = str(int(data.get("Mode", 0)))
        
        return WARMLINK_TO_HA_HVAC.get(mode, HVACMode.OFF)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.api.set_power(self._device_code, False)
        else:
            # Turn on first if off
            if self.hvac_mode == HVACMode.OFF:
                await self.coordinator.api.set_power(self._device_code, True)
            
            # Set mode
            warmlink_mode = HA_TO_WARMLINK_HVAC.get(hvac_mode, HVAC_MODE_HEATING)
            await self.coordinator.api.set_mode(self._device_code, warmlink_mode)
        
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature.
        
        VERIFIED: R01 is main water setpoint.
        """
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            # Use R01 for main temperature setpoint
            await self.coordinator.api.set_temperature(self._device_code, "R01", temperature)
            await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.coordinator.api.set_power(self._device_code, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.coordinator.api.set_power(self._device_code, False)
        await self.coordinator.async_request_refresh()
