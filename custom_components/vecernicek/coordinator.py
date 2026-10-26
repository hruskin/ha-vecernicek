"""Koordinátor stahující program Večerníčku."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DNY,
    DOMAIN,
    HOST_CT,
    INTERVAL_AKTUALIZACE,
    INTERVAL_PO_CHYBE,
    MAX_VELIKOST_ODPOVEDI,
    SOUBEZNE_STAHOVANI,
    URL_PROGRAM,
)
from .parser import parsuj_program

_LOGGER = logging.getLogger(__name__)

type Program = dict[str, dict[str, str | None]]
type VecernicekConfigEntry = ConfigEntry[VecernicekCoordinator]


class VecernicekCoordinator(DataUpdateCoordinator[Program]):
    """Jednou denně stáhne program na DNY dní dopředu (datum ISO -> epizoda)."""

    config_entry: VecernicekConfigEntry

    def __init__(self, hass: HomeAssistant, entry: VecernicekConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=INTERVAL_AKTUALIZACE,
        )
        self._session = async_get_clientsession(hass)
        self._semafor = asyncio.Semaphore(SOUBEZNE_STAHOVANI)

    async def _stahni_den(self, datum: date) -> dict[str, str | None] | None:
        async with self._semafor:
            return await self._stahni_den_bez_omezeni(datum)

    async def _stahni_den_bez_omezeni(self, datum: date) -> dict[str, str | None] | None:
        url = URL_PROGRAM.format(datum.strftime("%d.%m.%Y"))
        async with self._session.get(
            url, timeout=aiohttp.ClientTimeout(total=30)
        ) as odpoved:
            odpoved.raise_for_status()
            if odpoved.url.scheme != "https" or odpoved.url.host != HOST_CT:
                raise UpdateFailed(f"Neočekávané přesměrování na {odpoved.url}")
            data = bytearray()
            async for kus in odpoved.content.iter_chunked(64 * 1024):
                data.extend(kus)
                if len(data) > MAX_VELIKOST_ODPOVEDI:
                    raise UpdateFailed("Odpověď ČT je příliš velká")
        return parsuj_program(data.decode("utf-8", errors="replace"), datum)

    async def _async_update_data(self) -> Program:
        dnes = dt_util.now().date()
        dny = [dnes + timedelta(days=posun) for posun in range(DNY)]
        vysledky = await asyncio.gather(
            *(self._stahni_den(datum) for datum in dny), return_exceptions=True
        )

        # ponechá dříve stažené dny, které se teď nepodařilo načíst; zahodí minulé
        program: Program = {
            k: v for k, v in (self.data or {}).items() if k >= dnes.isoformat()
        }
        chyby: list[str] = []
        for datum, vysledek in zip(dny, vysledky, strict=True):
            if isinstance(vysledek, Exception):
                # např. TimeoutError nemá text, proto i název výjimky
                popis = type(vysledek).__name__
                if str(vysledek):
                    popis += f": {vysledek}"
                chyby.append(f"{datum.isoformat()} ({popis})")
            elif vysledek:
                program[datum.isoformat()] = vysledek

        self.update_interval = INTERVAL_PO_CHYBE if chyby else INTERVAL_AKTUALIZACE
        if len(chyby) == len(dny) and not program:
            raise UpdateFailed(f"Program ČT se nepodařilo stáhnout: {chyby[0]}")
        if chyby:
            _LOGGER.warning(
                "Nepodařilo se stáhnout program na %s; další pokus za %d min",
                ", ".join(chyby),
                INTERVAL_PO_CHYBE.total_seconds() // 60,
            )
        return dict(sorted(program.items()))
