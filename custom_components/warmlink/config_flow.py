"""Config flow for Warmlink integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import WarmLinkAPI, WarmLinkAuthError, WarmLinkConnectionError
from .const import DOMAIN, DEFAULT_NAME, CONF_LANGUAGE, SUPPORTED_LANGUAGES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_LANGUAGE, default="en"): SelectSelector(
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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate credentials by attempting login
                session = async_get_clientsession(self.hass)
                api = WarmLinkAPI(
                    session=session,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
                
                await api.login()
                
                # Set unique ID based on username
                await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({user_input[CONF_USERNAME]})",
                    data=user_input,
                )

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


class WarmLinkOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Warmlink."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
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
            ),
        )
