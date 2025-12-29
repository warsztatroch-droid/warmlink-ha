"""Config flow for Warmlink integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    SelectOptionDict,
)

from .api import WarmLinkAPI, WarmLinkAuthError, WarmLinkConnectionError
from .const import DOMAIN, DEFAULT_NAME, CONF_LANGUAGE, CONF_DEVICES, SUPPORTED_LANGUAGES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_LANGUAGE, default="pl"): SelectSelector(
            SelectSelectorConfig(
                options=SUPPORTED_LANGUAGES,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="language",
            )
        ),
    }
)


class WarmLinkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Warmlink."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._user_input: dict[str, Any] = {}
        self._devices: dict[str, dict] = {}
        self._api: WarmLinkAPI | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - login."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate credentials by attempting login
                session = async_get_clientsession(self.hass)
                self._api = WarmLinkAPI(
                    session=session,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
                
                await self._api.login()
                
                # Set unique ID based on username
                await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                self._abort_if_unique_id_configured()
                
                # Store user input for later
                self._user_input = user_input
                
                # Fetch devices
                self._devices = await self._api.get_devices()
                
                if not self._devices:
                    errors["base"] = "no_devices"
                else:
                    # Go to device selection step
                    return await self.async_step_devices()

            except WarmLinkAuthError:
                errors["base"] = "invalid_auth"
            except WarmLinkConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_devices = user_input.get(CONF_DEVICES, [])
            
            if not selected_devices:
                errors["base"] = "no_devices_selected"
            else:
                # Create entry with selected devices
                data = {
                    **self._user_input,
                    CONF_DEVICES: selected_devices,
                }
                
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({self._user_input[CONF_USERNAME]})",
                    data=data,
                )

        # Build device options list
        device_options = []
        for device_code, device_info in self._devices.items():
            # Get device name
            device_name = (
                device_info.get("device_nick_name") or 
                device_info.get("deviceNickName") or 
                device_code
            )
            # Get model info
            model = device_info.get("custModel") or device_info.get("productId") or ""
            # Get online status
            status = device_info.get("deviceStatus") or device_info.get("device_status") or ""
            is_online = status.upper() == "ONLINE"
            status_icon = "🟢" if is_online else "🔴"
            
            # Build label
            if model:
                label = f"{status_icon} {device_name} ({model})"
            else:
                label = f"{status_icon} {device_name}"
            
            device_options.append(
                SelectOptionDict(value=device_code, label=label)
            )

        # Default: select all devices
        default_selection = list(self._devices.keys())

        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICES, default=default_selection): SelectSelector(
                    SelectSelectorConfig(
                        options=device_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        multiple=True,
                        translation_key="devices",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="devices",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "device_count": str(len(self._devices)),
            },
        )


class WarmLinkOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Warmlink."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._devices: dict[str, dict] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Update options
            new_data = {**self.config_entry.data}
            
            if CONF_DEVICES in user_input:
                new_data[CONF_DEVICES] = user_input[CONF_DEVICES]
            if CONF_LANGUAGE in user_input:
                new_data[CONF_LANGUAGE] = user_input[CONF_LANGUAGE]
            
            # Update config entry data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
            )
            
            return self.async_create_entry(
                title="",
                data={
                    "update_interval": user_input.get("update_interval", 60),
                },
            )

        # Fetch current devices
        try:
            session = async_get_clientsession(self.hass)
            api = WarmLinkAPI(
                session=session,
                username=self.config_entry.data[CONF_USERNAME],
                password=self.config_entry.data[CONF_PASSWORD],
            )
            await api.login()
            self._devices = await api.get_devices()
        except Exception:
            _LOGGER.exception("Failed to fetch devices for options")
            self._devices = {}

        # Build device options
        device_options = []
        for device_code, device_info in self._devices.items():
            device_name = (
                device_info.get("device_nick_name") or 
                device_info.get("deviceNickName") or 
                device_code
            )
            model = device_info.get("custModel") or ""
            status = device_info.get("deviceStatus") or ""
            is_online = status.upper() == "ONLINE"
            status_icon = "🟢" if is_online else "🔴"
            
            if model:
                label = f"{status_icon} {device_name} ({model})"
            else:
                label = f"{status_icon} {device_name}"
            
            device_options.append(
                SelectOptionDict(value=device_code, label=label)
            )

        # Current selection
        current_devices = self.config_entry.data.get(CONF_DEVICES, list(self._devices.keys()))

        schema_dict = {
            vol.Optional(
                "update_interval",
                default=self.config_entry.options.get("update_interval", 60),
            ): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
            vol.Required(
                CONF_LANGUAGE,
                default=self.config_entry.data.get(CONF_LANGUAGE, "en"),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=SUPPORTED_LANGUAGES,
                    mode=SelectSelectorMode.DROPDOWN,
                    translation_key="language",
                )
            ),
        }

        # Add device selector if we have devices
        if device_options:
            schema_dict[vol.Required(CONF_DEVICES, default=current_devices)] = SelectSelector(
                SelectSelectorConfig(
                    options=device_options,
                    mode=SelectSelectorMode.DROPDOWN,
                    multiple=True,
                    translation_key="devices",
                )
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
        )
