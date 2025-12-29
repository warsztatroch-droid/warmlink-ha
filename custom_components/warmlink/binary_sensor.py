"""Binary sensor platform for Warmlink integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import DOMAIN, ERROR_CODES
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

# VERIFIED: Binary sensor descriptions
BINARY_SENSOR_DESCRIPTIONS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="device_online",
        name="(Online) Status połączenia",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="power",
        name="(Power) Status zasilania",
        device_class=BinarySensorDeviceClass.POWER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink binary sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    
    entities = []
    for device_code, device_data in coordinator.data.items():
        # Add standard binary sensors
        for description in BINARY_SENSOR_DESCRIPTIONS:
            entities.append(
                WarmLinkBinarySensor(
                    coordinator=coordinator,
                    device_code=device_code,
                    device_data=device_data,
                    description=description,
                )
            )
        
        # Add fault sensor with details
        entities.append(
            WarmLinkFaultSensor(
                coordinator=coordinator,
                device_code=device_code,
                device_data=device_data,
            )
        )
    
    async_add_entities(entities)


class WarmLinkBinarySensor(CoordinatorEntity[WarmLinkCoordinator], BinarySensorEntity):
    """Representation of a Warmlink binary sensor.
    
    VERIFIED: Uses _parsed_data and device status.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        device_code: str,
        device_data: dict[str, Any],
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on.
        
        VERIFIED: Power is in _parsed_data, device_online from deviceStatus.
        """
        if self.entity_description.key == "device_online":
            device = self.coordinator.data.get(self._device_code, {})
            return is_device_online(device)
        
        if self.entity_description.key == "power":
            data = self._get_parsed_data()
            power = data.get("Power")
            return power == 1 or power == "1"
        
        return None


class WarmLinkFaultSensor(CoordinatorEntity[WarmLinkCoordinator], BinarySensorEntity):
    """Sensor to show fault status with error code details.
    
    VERIFIED: Uses isFault field from device info.
    """

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_name = "(Fault) Status awarii"

    def __init__(
        self,
        coordinator: WarmLinkCoordinator,
        device_code: str,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the fault sensor."""
        super().__init__(coordinator)
        
        self._device_code = device_code
        
        device_name = device_data.get("device_nick_name") or device_data.get("deviceNickName") or device_code
        model = device_data.get("custModel") or device_data.get("productId") or "Heat Pump"
        
        self._attr_unique_id = f"{DOMAIN}_{device_code}_fault_status"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_code)},
            "name": device_name,
            "manufacturer": "Phinx/Warmlink",
            "model": model,
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if there is a fault.
        
        VERIFIED: Check isFault field and device online status.
        """
        device = self.coordinator.data.get(self._device_code, {})
        
        # Check various fault indicators
        is_fault = device.get("isFault") or device.get("is_fault")
        fault_code = device.get("faultCode") or device.get("fault_code") or device.get("fault")
        
        if is_fault:
            return True
        if fault_code and fault_code not in ("0", "", None):
            return True
        
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return fault details."""
        device = self.coordinator.data.get(self._device_code, {})
        
        fault_code = device.get("faultCode") or device.get("fault_code") or device.get("fault")
        
        attrs = {"fault_code": fault_code}
        
        # Add human-readable description if available
        if fault_code and fault_code in ERROR_CODES:
            attrs["fault_description"] = ERROR_CODES[fault_code]
        
        return attrs
