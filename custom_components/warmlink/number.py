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
        # === TEMPERATURES (R) - Setpoints ===
        "R01": "DHW Target Temperature",
        "R02": "Heating Target Temperature",
        "R03": "Cooling Target Temperature",
        "R70": "Room Target Temperature",
        "R04": "Heating On Difference",
        "R05": "Heating Off Difference",
        "R06": "Cooling On Difference",
        "R07": "Cooling Off Difference",
        "R16": "DHW On Difference",
        "R17": "DHW Off Difference",
        "R08": "Min Cooling Target",
        "R09": "Max Cooling Target",
        "R10": "Min Heating Target",
        "R11": "Max Heating Target",
        "R36": "Min DHW Target",
        "R37": "Max DHW Target",
        # === ZONES (Z) ===
        "Z02": "Zone 1 Target Room Temp",
        "Z03": "Zone 1 Diff to Start",
        "Z04": "Zone 2 Target Room Temp",
        "Z05": "Zone 2 Diff to Start",
        "Z06": "Zone 1 Heating Target WT",
        "Z07": "Zone 2 Mixing Target WT",
        "Z08": "Mixing Valve Manual %",
        "Z09": "Mixing Valve Opening Time",
        "Z10": "Mixing Valve Closing Time",
        "Z11": "Mixing Valve P (PID)",
        "Z12": "Mixing Valve I (PID)",
        "Z13": "Mixing Valve PID Period",
        # === DISINFECTION (G) ===
        "G01": "Disinfection Temperature",
        "G02": "Disinfection Duration",
        "G03": "Disinfection Start Time",
        "G04": "Disinfection Interval",
        # === COMPRESSOR (C) ===
        "C01": "Manual Compressor Frequency",
        "C02": "Min Compressor Frequency",
        "C03": "Max Compressor Frequency",
        # === PUMP (P) ===
        "P02": "Pump Interval Time",
        "P10": "Circulation Pump Speed",
        # === FAN (F) ===
        "F18": "Min Fan Speed Cooling",
        "F19": "Min Fan Speed Heating",
        "F23": "Rated DC Fan Speed",
        "F25": "Max Fan Speed Cooling",
        "F26": "Max Fan Speed Heating",
        "F02": "Coil Temp Max Fan Cooling",
        "F03": "Coil Temp Min Fan Cooling",
        "F05": "Coil Temp Max Fan Heating",
        "F06": "Coil Temp Min Fan Heating",
        "F28": "CT Reduce Two Fans Cooling",
        "F29": "CT Stop Single Fan Cooling",
        # === DEFROST (D) ===
        "D01": "Defrost Start Ambient Temp",
        "D02": "Heating Time Before Defrost",
        "D03": "Defrost Interval",
        "D17": "Coil Temp Exit Defrost",
        "D19": "Max Defrost Time",
        "D20": "Defrost Frequency",
        # === PROTECTION (A) ===
        "A03": "Shutdown Ambient Temp",
        "A04": "Antifreeze Temp",
        "A05": "Antifreeze Temp Difference",
        "A06": "Max Exhaust Temp",
        "A22": "Min Antifreeze Temp",
        "A23": "Min Outlet Water Protect",
        "A24": "Excess Temp Diff Inlet/Outlet",
        "A25": "Min Evaporation Temp Cooling",
        "A27": "Temp Diff Limiting Frequency",
        "A28": "Temp Diff Outlet/DHW",
        "A31": "Electric Heater On AT",
        "A32": "Electric Heater Delays Comp",
        "A33": "Electric Heater Opening Diff",
        "A34": "Crank Preheating Time",
        "A35": "Electric Heater OFF Diff",
        "A30": "Min AT for Cooling",
        # === EEV (E) ===
        "E02": "Target Superheat Heating",
        "E03": "EEV Initial Steps Heating",
        "E07": "EEV Min Steps",
        "E08": "EEV Initial Steps Cooling",
        # === SYSTEM (H) ===
        "H10": "Unit Address",
        "H18": "Electric Heater Stage",
        "H29": "Operation Code",
        "H32": "Force Switch Mode Time",
    },
    "pl": {
        # === TEMPERATURY (R) - Setpointy ===
        "R01": "Temperatura zadana CWU",
        "R02": "Temperatura zadana ogrzewania",
        "R03": "Temperatura zadana chłodzenia",
        "R70": "Temperatura zadana pokojowa",
        "R04": "Różnica włączenia ogrzewania",
        "R05": "Różnica wyłączenia ogrzewania",
        "R06": "Różnica włączenia chłodzenia",
        "R07": "Różnica wyłączenia chłodzenia",
        "R16": "Różnica włączenia CWU",
        "R17": "Różnica wyłączenia CWU",
        "R08": "Min temp. chłodzenia",
        "R09": "Max temp. chłodzenia",
        "R10": "Min temp. ogrzewania",
        "R11": "Max temp. ogrzewania",
        "R36": "Min temp. CWU",
        "R37": "Max temp. CWU",
        # === STREFY (Z) ===
        "Z02": "Strefa 1 temperatura pokojowa",
        "Z03": "Strefa 1 różnica startu",
        "Z04": "Strefa 2 temperatura pokojowa",
        "Z05": "Strefa 2 różnica startu",
        "Z06": "Strefa 1 temp. wody ogrzewania",
        "Z07": "Strefa 2 temp. mieszania",
        "Z08": "Zawór mieszający ręcznie %",
        "Z09": "Czas otwarcia zaworu mieszającego",
        "Z10": "Czas zamknięcia zaworu mieszającego",
        "Z11": "Zawór mieszający P (PID)",
        "Z12": "Zawór mieszający I (PID)",
        "Z13": "Okres PID zaworu mieszającego",
        # === DEZYNFEKCJA (G) ===
        "G01": "Temperatura dezynfekcji",
        "G02": "Czas dezynfekcji",
        "G03": "Godzina startu dezynfekcji",
        "G04": "Interwał dezynfekcji",
        # === SPRĘŻARKA (C) ===
        "C01": "Ręczna częstotliwość sprężarki",
        "C02": "Min częstotliwość sprężarki",
        "C03": "Max częstotliwość sprężarki",
        # === POMPA (P) ===
        "P02": "Interwał pompy",
        "P10": "Prędkość pompy obiegowej",
        # === WENTYLATOR (F) ===
        "F18": "Min obroty wentylatora chłodzenie",
        "F19": "Min obroty wentylatora grzanie",
        "F23": "Nominalne obroty wentyl. DC",
        "F25": "Max obroty wentylatora chłodzenie",
        "F26": "Max obroty wentylatora grzanie",
        "F02": "Temp. wężownicy max obr. chłodz.",
        "F03": "Temp. wężownicy min obr. chłodz.",
        "F05": "Temp. wężownicy max obr. grzanie",
        "F06": "Temp. wężownicy min obr. grzanie",
        "F28": "Temp. redukcji do 1 wentylatora",
        "F29": "Temp. wyłączenia wentylatora",
        # === ODSZRANIANIE (D) ===
        "D01": "Temperatura startu odszraniania",
        "D02": "Czas grzania przed odszranianiem",
        "D03": "Interwał odszraniania",
        "D17": "Temp. wężownicy wyjścia z odsz.",
        "D19": "Max czas odszraniania",
        "D20": "Częstotliwość odszraniania",
        # === ZABEZPIECZENIE (A) ===
        "A03": "Temp. wyłączenia zewnętrzna",
        "A04": "Temperatura przeciwzamrożeniowa",
        "A05": "Różnica temp. przeciwzamroż.",
        "A06": "Max temperatura tłoczenia",
        "A22": "Min temp. przeciwzamrożeniowa",
        "A23": "Min temp. ochrony wody wylot.",
        "A24": "Nadmierna różnica wlot/wylot",
        "A25": "Min temp. parowania chłodzenie",
        "A27": "Różnica temp. ogranicz. częst.",
        "A28": "Różnica temp. wylot/CWU",
        "A31": "Temp. włączenia grzałki elektr.",
        "A32": "Opóźnienie grzałki przed spr.",
        "A33": "Różnica otwarcia grzałki elektr.",
        "A34": "Czas podgrzewania sprężarki",
        "A35": "Różnica wyłączenia grzałki",
        "A30": "Min temp. zewn. dla chłodzenia",
        # === EEV (E) ===
        "E02": "Docelowe przegrzanie grzania",
        "E03": "Początkowe kroki EEV grzanie",
        "E07": "Min kroki EEV",
        "E08": "Początkowe kroki EEV chłodzenie",
        # === SYSTEM (H) ===
        "H10": "Adres jednostki",
        "H18": "Stopień grzałki elektrycznej",
        "H29": "Kod operacji",
        "H32": "Czas wymuszonej zmiany trybu",
    },
}

# Icons for number entities by category
NUMBER_ICONS = {
    # Temperatures (R)
    "R01": "mdi:water-thermometer",
    "R02": "mdi:radiator",
    "R03": "mdi:snowflake-thermometer",
    "R70": "mdi:home-thermometer",
    "R04": "mdi:thermometer-plus",
    "R05": "mdi:thermometer-minus",
    "R06": "mdi:thermometer-plus",
    "R07": "mdi:thermometer-minus",
    "R08": "mdi:thermometer-low",
    "R09": "mdi:thermometer-high",
    "R10": "mdi:thermometer-low",
    "R11": "mdi:thermometer-high",
    "R16": "mdi:thermometer-plus",
    "R17": "mdi:thermometer-minus",
    "R36": "mdi:thermometer-water",
    "R37": "mdi:thermometer-water",
    # Zones (Z)
    "Z02": "mdi:home-thermometer-outline",
    "Z03": "mdi:delta",
    "Z04": "mdi:home-thermometer-outline",
    "Z05": "mdi:delta",
    "Z06": "mdi:thermometer-water",
    "Z07": "mdi:thermometer-water",
    "Z08": "mdi:valve",
    "Z09": "mdi:timer-outline",
    "Z10": "mdi:timer-outline",
    "Z11": "mdi:tune",
    "Z12": "mdi:tune",
    "Z13": "mdi:timer-cog",
    # Disinfection (G)
    "G01": "mdi:bacteria-outline",
    "G02": "mdi:timer-outline",
    "G03": "mdi:clock-start",
    "G04": "mdi:calendar-clock",
    # Compressor (C)
    "C01": "mdi:sine-wave",
    "C02": "mdi:sine-wave",
    "C03": "mdi:sine-wave",
    # Pump (P)
    "P02": "mdi:timer-outline",
    "P10": "mdi:pump",
    # Fan (F)
    "F02": "mdi:thermometer",
    "F03": "mdi:thermometer",
    "F05": "mdi:thermometer",
    "F06": "mdi:thermometer",
    "F18": "mdi:fan-speed-1",
    "F19": "mdi:fan-speed-1",
    "F23": "mdi:fan",
    "F25": "mdi:fan-speed-3",
    "F26": "mdi:fan-speed-3",
    "F28": "mdi:fan-minus",
    "F29": "mdi:fan-off",
    # Defrost (D)
    "D01": "mdi:snowflake-thermometer",
    "D02": "mdi:timer-sand",
    "D03": "mdi:timer-sand",
    "D17": "mdi:thermometer-check",
    "D19": "mdi:timer-outline",
    "D20": "mdi:sine-wave",
    # Protection (A)
    "A03": "mdi:power-plug-off",
    "A04": "mdi:snowflake-alert",
    "A05": "mdi:delta",
    "A06": "mdi:thermometer-alert",
    "A22": "mdi:snowflake-thermometer",
    "A23": "mdi:water-thermometer",
    "A24": "mdi:delta",
    "A25": "mdi:thermometer-low",
    "A27": "mdi:delta",
    "A28": "mdi:delta",
    "A30": "mdi:thermometer",
    "A31": "mdi:heating-coil",
    "A32": "mdi:timer-outline",
    "A33": "mdi:delta",
    "A34": "mdi:timer-outline",
    "A35": "mdi:delta",
    # EEV (E)
    "E02": "mdi:thermometer-chevron-up",
    "E03": "mdi:stairs-up",
    "E07": "mdi:stairs-down",
    "E08": "mdi:stairs-up",
    # System (H)
    "H10": "mdi:identifier",
    "H18": "mdi:heating-coil",
    "H29": "mdi:code-tags",
    "H32": "mdi:timer-cog",
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
