"""Senzor s názvem epizody Večerníčku."""

from __future__ import annotations

from datetime import date, time, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CONF_CAS_PREPNUTI, DOMAIN, VYCHOZI_CAS_PREPNUTI
from .coordinator import VecernicekConfigEntry, VecernicekCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VecernicekConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    cas_prepnuti = dt_util.parse_time(
        entry.options.get(CONF_CAS_PREPNUTI, VYCHOZI_CAS_PREPNUTI)
    ) or dt_util.parse_time(VYCHOZI_CAS_PREPNUTI)
    async_add_entities([VecernicekSensor(entry.runtime_data, cas_prepnuti)])


def _zobrazovany_den(cas_prepnuti: time) -> date:
    """Do času přepnutí dnešek, potom zítřek."""
    ted = dt_util.now()
    if ted.time() >= cas_prepnuti:
        return ted.date() + timedelta(days=1)
    return ted.date()


class VecernicekSensor(CoordinatorEntity[VecernicekCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_translation_key = "vecernicek"
    # celý program a popisy nemá smysl ukládat do historie
    _unrecorded_attributes = frozenset({"program", "popis", "url"})

    def __init__(self, coordinator: VecernicekCoordinator, cas_prepnuti: time) -> None:
        super().__init__(coordinator)
        self._cas_prepnuti = cas_prepnuti
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Večerníček",
            manufacturer="Česká televize",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.ceskatelevize.cz/tv-program/",
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # v čase přepnutí se jen přepne na další den, nic se nestahuje
        self.async_on_remove(
            async_track_time_change(
                self.hass,
                self._prepni,
                hour=self._cas_prepnuti.hour,
                minute=self._cas_prepnuti.minute,
                second=self._cas_prepnuti.second,
            )
        )

    @callback
    def _prepni(self, _now: Any) -> None:
        self.async_write_ha_state()

    def _epizoda(self) -> dict[str, str | None] | None:
        return (self.coordinator.data or {}).get(_zobrazovany_den(self._cas_prepnuti).isoformat())

    @property
    def native_value(self) -> str | None:
        epizoda = self._epizoda()
        return epizoda["epizoda"] if epizoda else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        den = _zobrazovany_den(self._cas_prepnuti).isoformat()
        epizoda = self._epizoda() or {}
        return {
            "datum": den,
            "cas": epizoda.get("cas"),
            "serial": epizoda.get("serial"),
            "popis": epizoda.get("popis"),
            "url": epizoda.get("url"),
            "program": [
                v for k, v in (self.coordinator.data or {}).items() if k >= den
            ],
        }
