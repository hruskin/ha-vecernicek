"""Konstanty integrace Večerníček."""

from datetime import timedelta

DOMAIN = "vecernicek"

# volba: kolik dní dopředu stahovat (ČT zveřejňuje program cca 2 týdny předem)
CONF_DNY = "dny"
VYCHOZI_DNY = 7
# aspoň dnešek a zítřek, jinak by po přepnutí neměl senzor co ukázat
MIN_DNY = 2
MAX_DNY = 14
# volba: od tohoto času se zobrazuje epizoda následujícího dne
CONF_CAS_PREPNUTI = "cas_prepnuti"
VYCHOZI_CAS_PREPNUTI = "19:00:00"

INTERVAL_AKTUALIZACE = timedelta(hours=24)
INTERVAL_PO_CHYBE = timedelta(minutes=10)
# kolik stránek programu stahovat současně
SOUBEZNE_STAHOVANI = 2

URL_PROGRAM = "https://www.ceskatelevize.cz/tv-program/{}/"
URL_CT = "https://www.ceskatelevize.cz/"
HOST_CT = "www.ceskatelevize.cz"

# stránka programu má cca 300 kB, větší odpověď se odmítne
MAX_VELIKOST_ODPOVEDI = 5 * 1024 * 1024
# maximální délka stavu entity v HA
MAX_DELKA_STAVU = 255
