"""Parsování TV programu ČT – bez závislosti na Home Assistantu."""

from __future__ import annotations

from datetime import date
import html
import re
from urllib.parse import urljoin, urlsplit

from .const import HOST_CT, MAX_DELKA_STAVU, URL_CT

RE_BLOK = re.compile(r'(?s)<a href="/tv-program/Ve%C4%8Dern%C3%AD%C4%8Dek/">.*?</li>')
RE_CAS = re.compile(r'class="progTime">([^<]*)')
RE_SERIAL = re.compile(r'<h4><a href="([^"]*)" class="progTitle">([^<]*)')
RE_EPIZODA = re.compile(r"<h5>([^<]*)</h5>")
RE_POPIS = re.compile(r'class="hraji[^"]*">([^<]*)')


def _text(regex: re.Pattern[str], blok: str, skupina: int = 1) -> str | None:
    m = regex.search(blok)
    return html.unescape(m.group(skupina)).strip() if m else None


def _odkaz(href: str | None) -> str | None:
    """Vrátí absolutní odkaz jen tehdy, když vede na web ČT přes HTTPS."""
    if not href:
        return None
    url = urljoin(URL_CT, href)
    casti = urlsplit(url)
    if casti.scheme != "https" or casti.hostname != HOST_CT or casti.username:
        return None
    return url


def _zkrat(text: str | None) -> str | None:
    return text[:MAX_DELKA_STAVU] if text else text


def parsuj_program(stranka: str, datum: date) -> dict[str, str | None] | None:
    """Najde v HTML stránky programu blok Večerníčku a vrátí údaje o epizodě."""
    m = RE_BLOK.search(stranka)
    if not m:
        return None
    blok = m.group(0)
    serial = _zkrat(_text(RE_SERIAL, blok, 2))
    return {
        "datum": datum.isoformat(),
        "cas": _text(RE_CAS, blok),
        "serial": serial,
        "epizoda": _zkrat(_text(RE_EPIZODA, blok)) or serial,
        "popis": _text(RE_POPIS, blok),
        "url": _odkaz(_text(RE_SERIAL, blok, 1)),
    }
