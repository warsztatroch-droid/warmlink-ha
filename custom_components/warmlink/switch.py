"""Switch platform for Warmlink integration - binary controls."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import DOMAIN, CONF_LANGUAGE, SWITCH_PARAMS
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

# Translation keys for switch entities
SWITCH_TRANSLATIONS = {
    "en": {
        # System (H)
        "Power": "Power",
        "H01": "Power-off Memory",
        "H05": "Cooling Function",
        "H22": "Silent Mode",
        "H27": "EVI Function",
        "H33": "Fan+Comp Driver Integrated",
        "H36": "Weather Compensation",
        # Disinfection (G)
        "G05": "Disinfection",
        # Protection (A)
        "A11": "Low Pressure Sensor",
        "A29": "High Pressure Sensor",
        # Fan (F)
        "F22": "Manual Fan Speed",
        # Defrost (D)
        "D21": "Electric Heater Defrost",
        "D26": "Defrost Cascade Communication",
        # Zone (Z)
        "Z17": "Weather Comp Zone 2",
    },
    "pl": {
        # System (H)
        "Power": "Zasilanie",
        "H01": "Pamięć po wyłączeniu",
        "H05": "Funkcja chłodzenia",
        "H22": "Tryb cichy",
        "H27": "Funkcja EVI",
        "H33": "Zintegrowany sterownik wentyl.+sprężarki",
        "H36": "Kompensacja pogodowa",
        # Dezynfekcja (G)
        "G05": "Dezynfekcja",
        # Zabezpieczenie (A)
        "A11": "Czujnik niskiego ciśnienia",
        "A29": "Czujnik wysokiego ciśnienia",
        # Wentylator (F)
        "F22": "Ręczna prędkość wentylatora",
        # Odszranianie (D)
        "D21": "Grzałka odszraniania",
        "D26": "Komunikacja kaskady odszraniania",
        # Strefa (Z)
        "Z17": "Kompensacja pogodowa strefa 2",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink switch entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    api = data["api"]
    language = entry.data.get(CONF_LANGUAGE, "en")

    entities = []
    for device_code, device_data in coordinator.data.items():
        for param_code, param_info in SWITCH_PARAMS.items():
            # Power switch is always available
            # Others only if device has this parameter
            parsed_data = device_data.get("_parsed_data", {})
            if param_code == "Power" or param_code in parsed_data:
                entities.append(
                    WarmLinkSwitch(
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


class WarmLinkSwitch(CoordinatorEntity[WarmLinkCoordinator], SwitchEntity):
    """Representation of a Warmlink switch entity."""

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
        """Initialize the switch entity."""
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

        self._attr_unique_id = f"{DOMAIN}_{device_code}_{param_code}_switch"

        # Get translated name
        translations = SWITCH_TRANSLATIONS.get(language, SWITCH_TRANSLATIONS["en"])
        self._attr_name = translations.get(param_code, param_info.get("name", param_code))

        self._attr_icon = param_info.get("icon", "mdi:toggle-switch")

        # Power switch gets special device class
        if param_code == "Power":
            self._attr_device_class = SwitchDeviceClass.SWITCH

        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_code)},
            "name": device_name,
            "manufacturer": "Phinx/Warmlink",
            "model": model,
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        device = self.coordinator.data.get(self._device_code, {})
        parsed_data = device.get("_parsed_data", {})
        value = parsed_data.get(self._param_code)

        if value is not None:
            # Handle string or numeric values
            if isinstance(value, str):
                return value == "1" or value.lower() == "on"
            return bool(value)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator.data.get(self._device_code, {})
        # Power switch available even when offline (to turn on)
        if self._param_code == "Power":
            return super().available
        return is_device_online(device) and super().available

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.info(
            "Turning ON %s for device %s",
            self._param_code,
            self._device_code,
        )

        if self._param_code == "Power":
            success = await self._api.set_power(self._device_code, True)
        else:
            success = await self._api._control_device(
                self._device_code, self._param_code, "1"
            )

        if success:
            # Optimistically update the value
            device = self.coordinator.data.get(self._device_code, {})
            parsed_data = device.get("_parsed_data", {})
            parsed_data[self._param_code] = 1
            self.async_write_ha_state()

            # Request a refresh
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on %s", self._param_code)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.info(
            "Turning OFF %s for device %s",
            self._param_code,
            self._device_code,
        )

        if self._param_code == "Power":
            success = await self._api.set_power(self._device_code, False)
        else:
            success = await self._api._control_device(
                self._device_code, self._param_code, "0"
            )

        if success:
            # Optimistically update the value
            device = self.coordinator.data.get(self._device_code, {})
            parsed_data = device.get("_parsed_data", {})
            parsed_data[self._param_code] = 0
            self.async_write_ha_state()

            # Request a refresh
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off %s", self._param_code)
