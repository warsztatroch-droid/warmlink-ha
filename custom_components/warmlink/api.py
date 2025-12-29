"""API client for Warmlink heat pumps via cloud.linked-go.com.

VERIFIED API endpoints and parameters via direct testing on 2024-12-29.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any

import aiohttp

from .const import (
    API_BASE_URL,
    API_TIMEOUT,
    APP_ID,
    LOGIN_SOURCE,
    AREA_CODE,
    ENDPOINT_LOGIN,
    ENDPOINT_USER_INFO,
    ENDPOINT_DEVICE_LIST,
    ENDPOINT_DEVICE_STATUS,
    ENDPOINT_DEVICE_CONTROL,
    ENDPOINT_DEVICE_DATA,
    ENDPOINT_DEVICE_FAULT,
    ENDPOINT_AUTH_DEVICE_LIST,
    PROTOCOL_CODES_STATUS,
    PROTOCOL_CODES_TEMPS,
    PROTOCOL_CODES_SETPOINTS,
)

_LOGGER = logging.getLogger(__name__)


class WarmLinkAPIError(Exception):
    """Base exception for Warmlink API errors."""


class WarmLinkAuthError(WarmLinkAPIError):
    """Authentication error."""


class WarmLinkConnectionError(WarmLinkAPIError):
    """Connection error."""


class WarmLinkAPI:
    """Warmlink API client.
    
    API Base: https://cloud.linked-go.com:449/crmservice/api
    Authentication: MD5 hashed password, x-token header
    Warmlink App ID: 16
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        base_url: str = API_BASE_URL,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._username = username
        self._password = password
        self._base_url = base_url
        
        self._token: str | None = None
        self._user_id: str | None = None
        self._devices: dict[str, dict[str, Any]] = {}
        
        self._headers = {
            "Content-Type": "application/json; charset=utf-8",
        }

    @property
    def is_authenticated(self) -> bool:
        """Check if we have a valid token."""
        return self._token is not None

    @property
    def devices(self) -> dict[str, dict[str, Any]]:
        """Return discovered devices."""
        return self._devices

    async def login(self) -> bool:
        """Authenticate with the Warmlink API.
        
        VERIFIED: Works with appId=16, loginSource=IOS, userName parameter.
        """
        password_md5 = hashlib.md5(self._password.encode()).hexdigest()
        
        data = {
            "userName": self._username,
            "password": password_md5,
            "type": "2",
            "loginSource": LOGIN_SOURCE,
            "appId": APP_ID,
            "areaCode": AREA_CODE,
        }
        
        try:
            response = await self._post(ENDPOINT_LOGIN, data)
            
            if response.get("error_msg") == "Success":
                result = response.get("objectResult", {})
                self._token = result.get("x-token")
                self._user_id = result.get("userId") or result.get("user_id")
                
                if self._token:
                    self._headers["x-token"] = self._token
                    _LOGGER.info("Successfully logged in to Warmlink API, user_id=%s", self._user_id)
                    return True
            
            error = response.get("error_msg", "Unknown error")
            error_code = response.get("error_code", "")
            raise WarmLinkAuthError(f"Login failed: {error} (code: {error_code})")
            
        except aiohttp.ClientError as ex:
            raise WarmLinkConnectionError(f"Connection error: {ex}") from ex

    async def get_devices(self) -> dict[str, dict[str, Any]]:
        """Fetch list of devices (owned + shared/authorized).
        
        VERIFIED: Returns devices with device_code, deviceStatus, productId, custModel, etc.
        Also fetches shared devices from getAuthDeviceList endpoint.
        """
        if not self.is_authenticated:
            await self.login()
        
        data = {
            "appId": APP_ID,
        }
        
        try:
            # Get owned devices
            response = await self._post(ENDPOINT_DEVICE_LIST, data)
            
            if response.get("error_msg") == "Success":
                devices = response.get("objectResult", [])
                
                for device in devices:
                    device_code = device.get("device_code") or device.get("deviceCode")
                    if device_code:
                        device["_ownership"] = "owned"
                        self._devices[device_code] = device
                        device_status = device.get("deviceStatus") or device.get("device_status")
                        model = device.get("custModel") or "Unknown"
                        _LOGGER.info(
                            "Discovered owned device: %s (model: %s, status: %s)", 
                            device_code, model, device_status
                        )
            
            # Get shared/authorized devices
            try:
                shared_response = await self._post(ENDPOINT_AUTH_DEVICE_LIST, data)
                
                if shared_response.get("error_msg") == "Success":
                    shared_devices = shared_response.get("objectResult", [])
                    
                    for device in shared_devices:
                        device_code = device.get("device_code") or device.get("deviceCode")
                        if device_code and device_code not in self._devices:
                            device["_ownership"] = "shared"
                            self._devices[device_code] = device
                            device_status = device.get("deviceStatus") or device.get("device_status")
                            model = device.get("custModel") or "Unknown"
                            _LOGGER.info(
                                "Discovered shared device: %s (model: %s, status: %s)", 
                                device_code, model, device_status
                            )
            except Exception as ex:
                # Shared devices endpoint might not work for all accounts
                _LOGGER.debug("Could not fetch shared devices: %s", ex)
            
            return self._devices
            
        except aiohttp.ClientError as ex:
            raise WarmLinkConnectionError(f"Failed to get devices: {ex}") from ex

    async def get_device_status(self, device_code: str) -> dict[str, Any]:
        """Get current status of a device."""
        if not self.is_authenticated:
            await self.login()
        
        data = {
            "deviceCode": device_code,
            "appId": APP_ID,
        }
        
        try:
            response = await self._post(ENDPOINT_DEVICE_STATUS, data)
            
            if response.get("error_msg") == "Success":
                status = response.get("objectResult", {})
                
                if device_code in self._devices:
                    self._devices[device_code]["_status"] = status
                
                return status
            
            return {}
            
        except aiohttp.ClientError as ex:
            _LOGGER.error("Failed to get device status: %s", ex)
            return {}

    async def get_device_data(
        self, device_code: str, protocol_codes: list[str] | None = None
    ) -> dict[str, Any]:
        """Fetch data points from device.
        
        VERIFIED: Returns code/value pairs with rangeStart/rangeEnd.
        
        Args:
            device_code: Device identifier
            protocol_codes: List of codes to fetch. If None, fetches common codes.
        """
        if not self.is_authenticated:
            await self.login()
        
        if protocol_codes is None:
            protocol_codes = PROTOCOL_CODES_STATUS + PROTOCOL_CODES_TEMPS + PROTOCOL_CODES_SETPOINTS
        
        data = {
            "deviceCode": device_code,
            "appId": APP_ID,
            "protocalCodes": protocol_codes,  # Note: API uses "protocal" (typo)
        }
        
        try:
            response = await self._post(ENDPOINT_DEVICE_DATA, data)
            
            if response.get("error_msg") == "Success":
                result = {}
                for item in response.get("objectResult", []):
                    code = item.get("code")
                    value = item.get("value")
                    if code and value is not None:
                        result[code] = {
                            "value": value,
                            "range_start": item.get("rangeStart"),
                            "range_end": item.get("rangeEnd"),
                        }
                
                # Update cached device data
                if device_code in self._devices:
                    self._devices[device_code]["_data"] = result
                
                return result
            
            return {}
            
        except aiohttp.ClientError as ex:
            _LOGGER.error("Failed to get device data: %s", ex)
            return {}

    async def get_device_faults(self, device_code: str) -> list[dict[str, Any]]:
        """Get fault history for device."""
        if not self.is_authenticated:
            await self.login()
        
        data = {
            "deviceCode": device_code,
            "appId": APP_ID,
        }
        
        try:
            response = await self._post(ENDPOINT_DEVICE_FAULT, data)
            
            if response.get("error_msg") == "Success":
                return response.get("objectResult", [])
            
            return []
            
        except aiohttp.ClientError as ex:
            _LOGGER.error("Failed to get device faults: %s", ex)
            return []

    async def set_power(self, device_code: str, power_on: bool) -> bool:
        """Turn device on or off."""
        return await self._control_device(device_code, "Power", "1" if power_on else "0")

    async def set_mode(self, device_code: str, mode: str) -> bool:
        """Set operation mode.
        
        Modes: 1=heating, 2=cooling, 3=hot_water, 4=heating+hw, 5=cooling+hw
        """
        return await self._control_device(device_code, "Mode", mode)

    async def set_temperature(self, device_code: str, param: str, temperature: float) -> bool:
        """Set target temperature.
        
        Args:
            device_code: Device identifier
            param: Temperature parameter (R01=heating, R02=cooling, R03=room)
            temperature: Target temperature
        """
        return await self._control_device(device_code, param, str(temperature))

    async def _control_device(self, device_code: str, param: str, value: str) -> bool:
        """Send control command to device."""
        if not self.is_authenticated:
            await self.login()
        
        data = {
            "deviceCode": device_code,
            "appId": APP_ID,
            "param": param,
            "value": value,
        }
        
        try:
            response = await self._post(ENDPOINT_DEVICE_CONTROL, data)
            
            if response.get("error_msg") == "Success":
                _LOGGER.info(
                    "Control command sent: device=%s, %s=%s", 
                    device_code, param, value
                )
                return True
            
            error = response.get("error_msg", "Unknown error")
            _LOGGER.error("Control command failed: %s", error)
            return False
            
        except aiohttp.ClientError as ex:
            _LOGGER.error("Failed to control device: %s", ex)
            return False

    async def _post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Send POST request to API."""
        url = f"{self._base_url}/{endpoint}?lang={AREA_CODE}"
        
        _LOGGER.debug("POST %s: %s", url, data)
        
        async with self._session.post(
            url,
            json=data,
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ssl=False,  # Some API servers have cert issues
        ) as response:
            response.raise_for_status()
            result = await response.json()
            _LOGGER.debug("Response: %s", result)
            return result

    async def close(self) -> None:
        """Close the API session."""
        self._token = None
        self._user_id = None
        self._devices.clear()


# Helper function to parse temperature from API value
def parse_temperature(value: str | None) -> float | None:
    """Parse temperature string to float."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# Helper to check if device is online
def is_device_online(device: dict[str, Any]) -> bool:
    """Check if device is online."""
    status = device.get("deviceStatus") or device.get("device_status") or ""
    return status.upper() == "ONLINE"
