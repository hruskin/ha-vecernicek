"""Konstanty integrace Večerníček."""

from datetime import timedelta

DOMAIN = "vecernicek"

# kolik dní dopředu stahovat (ČT zveřejňuje program cca 2 týdny předem)
DNY = 7
# od této hodiny se zobrazuje epizoda následujícího dne
PREPNUTI_HODINA = 19

INTERVAL_AKTUALIZACE = timedelta(hours=24)
INTERVAL_PO_CHYBE = timedelta(minutes=30)

URL_PROGRAM = "https://www.ceskatelevize.cz/tv-program/{}/"
URL_CT = "https://www.ceskatelevize.cz/"
HOST_CT = "www.ceskatelevize.cz"

# stránka programu má cca 300 kB, větší odpověď se odmítne
MAX_VELIKOST_ODPOVEDI = 5 * 1024 * 1024
# maximální délka stavu entity v HA
MAX_DELKA_STAVU = 255
