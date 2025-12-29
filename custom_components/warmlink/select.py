"""Select platform for Warmlink integration - mode selection and options."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import is_device_online
from .const import DOMAIN, CONF_LANGUAGE, SELECT_PARAMS
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

# Translation keys for select entities
SELECT_TRANSLATIONS = {
    "en": {
        # Main
        "Mode": "Operating Mode",
        # System (H)
        "H07": "Control Mode",
        "H18": "Electric Heater Stage",
        "H20": "3-way Valve Polarity",
        "H21": "Temperature Unit",
        "H25": "Temp Control Selection",
        "H28": "DHW Function",
        "H30": "Indoor Unit Type",
        "H31": "Circulation Pump Type",
        "H37": "DHW Temp Sourcing",
        "H38": "Language",
        # Zone (Z)
        "Z01": "Multi-Zone Control",
        # Fan (F)
        "F01": "Fan Motor Type",
        "F10": "Fan Quantity",
        # Compressor (C)
        "C04": "Model Selection",
        "C06": "Frequency Control Mode",
        # Pump (P)
        "P01": "Main Pump Mode",
        "P05": "DHW Pump Mode",
        "P06": "Main Pump Manual Control",
        # Protection (A)
        "A21": "Sensor Type",
        "A26": "Refrigerant Type",
        # EEV (E)
        "E01": "EEV Adjust Mode",
    },
    "pl": {
        # Główne
        "Mode": "Tryb pracy",
        # System (H)
        "H07": "Tryb sterowania",
        "H18": "Stopień grzałki elektrycznej",
        "H20": "Polaryzacja zaworu 3-drogowego",
        "H21": "Jednostka temperatury",
        "H25": "Wybór sterowania temperaturą",
        "H28": "Funkcja CWU",
        "H30": "Typ jednostki wewnętrznej",
        "H31": "Typ pompy obiegowej",
        "H37": "Źródło temp. CWU",
        "H38": "Język",
        # Strefa (Z)
        "Z01": "Sterowanie wielostrefowe",
        # Wentylator (F)
        "F01": "Typ silnika wentylatora",
        "F10": "Liczba wentylatorów",
        # Sprężarka (C)
        "C04": "Wybór modelu",
        "C06": "Tryb sterowania częstotliwością",
        # Pompa (P)
        "P01": "Tryb głównej pompy",
        "P05": "Tryb pompy CWU",
        "P06": "Ręczne sterowanie główną pompą",
        # Zabezpieczenie (A)
        "A21": "Typ czujnika",
        "A26": "Typ czynnika chłodniczego",
        # EEV (E)
        "E01": "Tryb regulacji EEV",
    },
}

# Option translations for Polish
SELECT_OPTIONS_PL = {
    "Mode": {
        "0": "Ciepła woda",
        "1": "Ogrzewanie",
        "2": "Chłodzenie",
        "3": "CW + Ogrzewanie",
        "4": "CW + Chłodzenie",
    },
    "H07": {
        "0": "Sterowanie wyświetlaczem",
        "1": "Zdalne sterowanie",
    },
    "H18": {
        "1": "Stopień 1",
        "2": "Stopień 2",
        "3": "Stopień 3",
    },
    "H20": {
        "0": "CW - ZAŁ",
        "1": "CW - WYŁ",
    },
    "H21": {
        "0": "°C",
        "1": "°F",
    },
    "H25": {
        "0": "Temp. wody wylotowej",
        "1": "Temp. pokojowa",
        "2": "Temp. bufora",
        "3": "Temp. wody wlotowej",
    },
    "H28": {
        "0": "Wyłączone",
        "1": "Włączone",
        "2": "Tylko CWU",
    },
    "H30": {
        "0": "Brak",
        "1": "Typ 1",
        "2": "Typ 2",
        "3": "Typ 3",
    },
    "H31": {
        "0": "Bez detekcji przepływu",
        "1": "Grundfos 25-75",
        "2": "Grundfos 25-105",
        "3": "Grundfos 25-125",
        "4": "APM25 9-130",
        "5": "APM25 12-130",
    },
    "H37": {
        "0": "Czujnik zbiornika CWU",
        "1": "Zewnętrzny Modbus",
    },
    "H38": {
        "0": "Angielski",
        "1": "Chiński",
        "2": "Polski",
        "3": "Niemiecki",
        "4": "Francuski",
        "5": "Włoski",
        "6": "Hiszpański",
        "7": "Portugalski",
        "8": "Rosyjski",
        "9": "Czeski",
        "10": "Węgierski",
        "11": "Rumuński",
        "12": "Turecki",
        "13": "Grecki",
    },
    "Z01": {
        "0": "Brak",
        "1": "Strefa 1-S",
        "2": "Strefa 2-S",
        "3": "Strefa 1&2-S",
        "4": "Strefa 1-T",
        "5": "Strefa 2-T",
        "6": "Strefa 1&2-T",
        "7": "Strefa 1-P",
        "8": "Strefa 2-P",
        "9": "Strefa 1&2-P",
    },
    "F01": {
        "1": "Podwójny",
        "3": "DC",
        "4": "DC zewn. sterownik",
    },
    "F10": {
        "0": "Jeden wentylator",
        "1": "Dwa wentylatory",
    },
    "C04": {
        "0": "Model 0",
        "1": "Model 1",
        "2": "Model 2",
        "3": "Model 3",
    },
    "C06": {
        "0": "Auto",
        "1": "Ręczny",
    },
    "P01": {
        "0": "Ciągły",
        "1": "Interwałowy",
        "2": "Na żądanie",
    },
    "P05": {
        "0": "Wyłączona",
        "1": "Włączona",
        "2": "Auto",
    },
    "P06": {
        "0": "Auto",
        "1": "Ręcznie ZAŁ",
        "2": "Ręcznie WYŁ",
    },
    "A21": {
        "0": "5K",
        "1": "2K",
    },
    "A26": {
        "0": "R32",
        "1": "R290",
        "2": "R32-1",
        "3": "R290-1",
        "4": "R32-2",
        "5": "R290-2",
    },
    "E01": {
        "0": "Auto",
        "1": "Ręczny",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Warmlink select entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: WarmLinkCoordinator = data["coordinator"]
    api = data["api"]
    language = entry.data.get(CONF_LANGUAGE, "en")

    entities = []
    for device_code, device_data in coordinator.data.items():
        for param_code, param_info in SELECT_PARAMS.items():
            # Mode is always available, others check if device has parameter
            parsed_data = device_data.get("_parsed_data", {})
            if param_code == "Mode" or param_code in parsed_data:
                entities.append(
                    WarmLinkSelect(
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


class WarmLinkSelect(CoordinatorEntity[WarmLinkCoordinator], SelectEntity):
    """Representation of a Warmlink select entity."""

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
        """Initialize the select entity."""
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

        self._attr_unique_id = f"{DOMAIN}_{device_code}_{param_code}_select"

        # Get translated name
        translations = SELECT_TRANSLATIONS.get(language, SELECT_TRANSLATIONS["en"])
        self._attr_name = translations.get(param_code, param_info.get("name", param_code))

        self._attr_icon = param_info.get("icon", "mdi:form-select")

        # Build options list based on language
        self._options_map = param_info.get("options", {})
        if language == "pl" and param_code in SELECT_OPTIONS_PL:
            self._options_map = SELECT_OPTIONS_PL[param_code]
        
        # Options are the display values
        self._attr_options = list(self._options_map.values())
        
        # Reverse map for value lookup
        self._value_to_option = self._options_map
        self._option_to_value = {v: k for k, v in self._options_map.items()}

        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_code)},
            "name": device_name,
            "manufacturer": "Phinx/Warmlink",
            "model": model,
        }

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        device = self.coordinator.data.get(self._device_code, {})
        parsed_data = device.get("_parsed_data", {})
        value = parsed_data.get(self._param_code)

        if value is not None:
            # Convert value to string for lookup
            str_value = str(int(value)) if isinstance(value, float) else str(value)
            return self._value_to_option.get(str_value)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator.data.get(self._device_code, {})
        return is_device_online(device) and super().available

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = self._option_to_value.get(option)
        if value is None:
            _LOGGER.error("Unknown option: %s", option)
            return

        _LOGGER.info(
            "Setting %s to %s (%s) for device %s",
            self._param_code,
            option,
            value,
            self._device_code,
        )

        if self._param_code == "Mode":
            success = await self._api.set_mode(self._device_code, value)
        else:
            success = await self._api._control_device(
                self._device_code, self._param_code, value
            )

        if success:
            # Optimistically update the value
            device = self.coordinator.data.get(self._device_code, {})
            parsed_data = device.get("_parsed_data", {})
            parsed_data[self._param_code] = int(value)
            self.async_write_ha_state()

            # Request a refresh
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set %s", self._param_code)
