"""Coordinator for Warmlink integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WarmLinkAPI, WarmLinkAPIError, is_device_online
from .const import (
    DOMAIN,
    PROTOCOL_CODES_ALL,
)

_LOGGER = logging.getLogger(__name__)


class WarmLinkCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage fetching Warmlink data.
    
    Uses verified Warmlink API endpoints:
    - Protocol codes: Power, Mode, T01-T05, R01-R03
    - API returns deviceStatus: "ONLINE"/"OFFLINE"
    """

    def __init__(
        self,
        hass: HomeAssistant,
        api: WarmLinkAPI,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API.
        
        Uses getDataByCode with protocol codes from Modbus CSV mapping.
        Returns dict with device_code as key, device data as value.
        """
        try:
            # Get device list - returns objectResult with device_code, deviceStatus, etc.
            devices = await self.api.get_devices()
            
            for device_code, device_info in devices.items():
                # Only fetch data for online devices
                if not is_device_online(device_info):
                    _LOGGER.debug("Skipping offline device: %s", device_code)
                    continue
                
                # Fetch data using all protocol codes for comprehensive monitoring
                data = await self.api.get_device_data(device_code, PROTOCOL_CODES_ALL)
                
                # Parse data into device info
                # API returns: {"code": "T01", "value": "27.0", "rangeStart": "0", "rangeEnd": "70"}
                device_info["_parsed_data"] = {}
                device_info["_ranges"] = {}
                
                for code, code_data in data.items():
                    value = code_data.get("value")
                    if value is not None:
                        try:
                            # Try to convert to float for numeric values
                            device_info["_parsed_data"][code] = float(value)
                        except (ValueError, TypeError):
                            device_info["_parsed_data"][code] = value
                    
                    # Store range info for setpoints
                    range_start = code_data.get("range_start")
                    range_end = code_data.get("range_end")
                    if range_start and range_end:
                        try:
                            device_info["_ranges"][code] = {
                                "min": float(range_start),
                                "max": float(range_end),
                            }
                        except (ValueError, TypeError):
                            pass
                
                _LOGGER.debug(
                    "Device %s: Power=%s, Mode=%s, T01=%.1f, T02=%.1f, T04=%.1f, R01=%.1f", 
                    device_code,
                    device_info["_parsed_data"].get("Power"),
                    device_info["_parsed_data"].get("Mode"),
                    device_info["_parsed_data"].get("T01", 0),
                    device_info["_parsed_data"].get("T02", 0),
                    device_info["_parsed_data"].get("T04", 0),
                    device_info["_parsed_data"].get("R01", 0),
                )
            
            return devices
            
        except WarmLinkAPIError as ex:
            raise UpdateFailed(f"Error communicating with API: {ex}") from ex
