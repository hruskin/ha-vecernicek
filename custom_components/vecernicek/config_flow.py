"""Config flow integrace Večerníček."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TimeSelector,
)

from .const import (
    CONF_CAS_PREPNUTI,
    CONF_DNY,
    DOMAIN,
    MAX_DNY,
    MIN_DNY,
    VYCHOZI_CAS_PREPNUTI,
    VYCHOZI_DNY,
)


def _schema(options: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_CAS_PREPNUTI,
                default=options.get(CONF_CAS_PREPNUTI, VYCHOZI_CAS_PREPNUTI),
            ): TimeSelector(),
            vol.Required(
                CONF_DNY, default=options.get(CONF_DNY, VYCHOZI_DNY)
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_DNY, max=MAX_DNY, step=1, mode=NumberSelectorMode.BOX
                )
            ),
        }
    )


def _normalizuj(user_input: dict[str, Any]) -> dict[str, Any]:
    """NumberSelector vrací float, počet dní ukládáme jako int."""
    return {**user_input, CONF_DNY: int(user_input[CONF_DNY])}


class VecernicekConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="Večerníček", data={}, options=_normalizuj(user_input)
            )
        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return VecernicekOptionsFlow()


class VecernicekOptionsFlow(OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=_normalizuj(user_input))
        return self.async_show_form(
            step_id="init", data_schema=_schema(self.config_entry.options)
        )
