"""Warmlink Heat Pump integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, UPDATE_INTERVAL, CONF_DEVICES
from .api import WarmLinkAPI
from .coordinator import WarmLinkCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.WATER_HEATER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Warmlink from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api = WarmLinkAPI(
        session=session,
        username=entry.data["username"],
        password=entry.data["password"],
    )

    try:
        await api.login()
    except Exception as ex:
        _LOGGER.error("Failed to login to Warmlink API: %s", ex)
        return False

    # Get selected devices from config
    selected_devices = entry.data.get(CONF_DEVICES)

    coordinator = WarmLinkCoordinator(
        hass,
        api=api,
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
        selected_devices=selected_devices,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["api"].close()

    return unload_ok
