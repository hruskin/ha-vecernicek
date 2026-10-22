# Večerníček pro Home Assistant

Custom integrace, která vytvoří senzor `sensor.vecernicek` s názvem epizody
Večerníčku z TV programu ČT (ČT :D). Do 19:00 ukazuje dnešní epizodu, potom
epizodu následujícího dne.

## Instalace

1. Zkopírujte `custom_components/vecernicek` do `/config/custom_components/`.
2. Restartujte Home Assistant.
3. Nastavení → Zařízení a služby → Přidat integraci → **Večerníček**.

## Senzor

- **stav** – název epizody (pokud díl nemá vlastní název, název seriálu)
- **atributy** – `datum`, `cas`, `serial`, `popis`, `url`, `program`
  (seznam epizod na nadcházející dny)

Program se stahuje jednou denně na 7 dní dopředu; v 19:00 se senzor jen
přepne na další den. Při chybě stahování se pokus opakuje po 30 minutách.
Ruční obnovení: akce `homeassistant.update_entity` na `sensor.vecernicek`.

Data se parsují z HTML stránky https://www.ceskatelevize.cz/tv-program/ –
při změně jejího formátu je potřeba upravit `parser.py`.
