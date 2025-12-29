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

# Translation keys for switch entities (primary switches only)
SWITCH_TRANSLATIONS = {
    "en": {
        "Power": "(Power) Main Power",
        # System (H)
        "H01": "(H01) Remote On/Off Control",
        "H02": "(H02) Manual Defrost",
        "H03": "(H03) Holiday Mode",
        "H04": "(H04) Silent Mode",
        "H05": "(H05) ECO Mode",
        "H06": "(H06) Anti-Legionella",
        "H08": "(H08) Display Lock",
        "H09": "(H09) Child Lock",
        "H11": "(H11) Auto Restart",
        "H12": "(H12) Energy Saving Mode",
        "H13": "(H13) Boost Mode",
        "H14": "(H14) Night Mode",
        "H15": "(H15) Frost Protection",
        "H16": "(H16) DHW Priority",
        "H17": "(H17) Quiet Mode",
        # Disinfection (G)
        "G05": "(G05) Disinfection Enable",
        # Fan (F)
        "F07": "(F07) Fan Variable Speed",
        "F08": "(F08) Fan Auto Speed",
        # Pump (P)
        "P03": "(P03) Pump Anti-Block",
        "P04": "(P04) DHW Pump Enable",
        "P07": "(P07) Circulation Pump Enable",
        "P08": "(P08) Solar Pump Enable",
        "P09": "(P09) Boiler Pump Enable",
        # Protection (A)
        "A01": "(A01) High Pressure Protection",
        "A02": "(A02) Low Pressure Protection",
        "A07": "(A07) Electric Heater Enable",
        "A08": "(A08) Emergency Mode Enable",
        "A09": "(A09) Compressor Preheating",
        "A10": "(A10) Antifreeze Enable",
        "A11": "(A11) Exhaust Overtemp Protect",
        "A12": "(A12) Flow Switch Enable",
        "A13": "(A13) Water Level Switch Enable",
        "A14": "(A14) Phase Loss Protection",
        "A15": "(A15) Phase Sequence Protection",
        # Defrost (D)
        "D04": "(D04) Force Defrost",
        "D05": "(D05) Auto Defrost Enable",
        "D06": "(D06) Electric Defrost Enable",
        "D07": "(D07) Hot Gas Defrost Enable",
        # Zone (Z)
        "Z14": "(Z14) Zone 1 Enable",
        "Z15": "(Z15) Zone 2 Enable",
        "Z16": "(Z16) Mixing Valve Enable",
        # EEV (E)
        "E04": "(E04) EEV Manual Mode",
        "E05": "(E05) EEV Auto Adjust",
        # Compressor (C)
        "C05": "(C05) Compressor Manual Mode",
        "C07": "(C07) Dual Compressor",
        "C08": "(C08) Compressor Rotation",
    },
    "pl": {
        "Power": "(Power) Zasilanie główne",
        # System (H)
        "H01": "(H01) Zdalne wł/wył",
        "H02": "(H02) Ręczne odszranianie",
        "H03": "(H03) Tryb urlopowy",
        "H04": "(H04) Tryb cichy",
        "H05": "(H05) Tryb ECO",
        "H06": "(H06) Anty-legionella",
        "H08": "(H08) Blokada wyświetlacza",
        "H09": "(H09) Blokada rodzicielska",
        "H11": "(H11) Auto restart",
        "H12": "(H12) Tryb oszczędzania energii",
        "H13": "(H13) Tryb boost",
        "H14": "(H14) Tryb nocny",
        "H15": "(H15) Ochrona przed mrozem",
        "H16": "(H16) Priorytet CWU",
        "H17": "(H17) Tryb cichy",
        # Dezynfekcja (G)
        "G05": "(G05) Włącz dezynfekcję",
        # Wentylator (F)
        "F07": "(F07) Zmienna prędkość wentylatora",
        "F08": "(F08) Auto prędkość wentylatora",
        # Pompa (P)
        "P03": "(P03) Anty-zablokowanie pompy",
        "P04": "(P04) Włącz pompę CWU",
        "P07": "(P07) Włącz pompę obiegową",
        "P08": "(P08) Włącz pompę solarną",
        "P09": "(P09) Włącz pompę kotła",
        # Ochrona (A)
        "A01": "(A01) Ochrona wysokiego ciśnienia",
        "A02": "(A02) Ochrona niskiego ciśnienia",
        "A07": "(A07) Włącz grzałkę elektryczną",
        "A08": "(A08) Włącz tryb awaryjny",
        "A09": "(A09) Podgrzewanie sprężarki",
        "A10": "(A10) Włącz ochronę przed zamarzaniem",
        "A11": "(A11) Ochrona przegrzania wylotu",
        "A12": "(A12) Włącz presostat przepływu",
        "A13": "(A13) Włącz czujnik poziomu wody",
        "A14": "(A14) Ochrona zanikania fazy",
        "A15": "(A15) Ochrona sekwencji faz",
        # Odszranianie (D)
        "D04": "(D04) Wymuś odszranianie",
        "D05": "(D05) Włącz auto odszranianie",
        "D06": "(D06) Odszranianie elektryczne",
        "D07": "(D07) Odszranianie gorącym gazem",
        # Strefa (Z)
        "Z14": "(Z14) Włącz strefę 1",
        "Z15": "(Z15) Włącz strefę 2",
        "Z16": "(Z16) Włącz zawór mieszający",
        # EEV (E)
        "E04": "(E04) Tryb ręczny EEV",
        "E05": "(E05) Auto regulacja EEV",
        # Sprężarka (C)
        "C05": "(C05) Tryb ręczny sprężarki",
        "C07": "(C07) Podwójna sprężarka",
        "C08": "(C08) Rotacja sprężarek",
    },
}

# Icons by category prefix
SWITCH_ICONS = {
    "Power": "mdi:power",
    "H": "mdi:cog",           # System
    "G": "mdi:bacteria",      # Disinfection
    "A": "mdi:shield-check",  # Protection
    "F": "mdi:fan",           # Fan
    "D": "mdi:snowflake",     # Defrost
    "Z": "mdi:home-floor-1",  # Zone
    "P": "mdi:pump",          # Pump
    "E": "mdi:valve",         # EEV
    "L": "mdi:server",        # Central control
    "M": "mdi:timer",         # Mode timers
    "W": "mdi:water-pump",    # Water pump timers
    "K": "mdi:clock-outline", # Schedule
    "R": "mdi:thermometer",   # Thermostat
    "S": "mdi:solar-power",   # SG Ready
    "T": "mdi:thermometer",   # Thermostat
}

def get_switch_icon(code: str) -> str:
    """Get icon for switch based on code or prefix."""
    if code in SWITCH_ICONS:
        return SWITCH_ICONS[code]
    if code:
        prefix = code[0].upper()
        return SWITCH_ICONS.get(prefix, "mdi:toggle-switch")
    return "mdi:toggle-switch"


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
        parsed_data = device_data.get("_parsed_data", {})
        
        for param_code, param_info in SWITCH_PARAMS.items():
            # Power switch is always available
            # Others only if device has this parameter
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

    _LOGGER.info("Setting up %d switch entities for Warmlink", len(entities))
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
