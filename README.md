# cBox for Home Assistant

[![Open your Home Assistant instance and open this repository in the Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sdaclin&repository=hass-cbox&category=integration)
[![Validate](https://github.com/sdaclin/hass-cbox/actions/workflows/validate.yaml/badge.svg)](https://github.com/sdaclin/hass-cbox/actions/workflows/validate.yaml)
[![hassfest](https://github.com/sdaclin/hass-cbox/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/sdaclin/hass-cbox/actions/workflows/hassfest.yaml)

Control a pellet stove equipped with a [Fumis Alpha](https://fumis.si/en/about-fumis/fumis-combustion-controllers/fumis-alpha)
controller and its **Connection Box** (a.k.a. `connBox` / `cBox`) from Home Assistant, locally, without any cloud.

The Fumis Alpha controller is used by many brands: Palazzetti, Jotul, TurboFonte, Godin, Fonte Flamme, Invicta,
Casatelli, Alpis, Faizen, HETA… It has been tested with a Jotul PF 1033.

The integration relies on the [connbox](https://github.com/sdaclin/cbox) library.

## Installation

### Marketplace / HACS

1. Click the badge above, or in Home Assistant open **Marketplace** (or **HACS** on older versions), then
   **⋮ > Custom repositories**, add `https://github.com/sdaclin/hass-cbox` with the type **Integration**.
2. Download **cBox** and restart Home Assistant.

### Manual

Copy `custom_components/cbox` into the `custom_components` folder of your Home Assistant configuration and restart.

## Configuration

**Settings > Devices & services > Add integration > cBox**, then enter the host name or IP address of the
Connection Box. Giving the cBox a fixed IP address on your router is recommended. If it changes later, use
**Reconfigure** on the integration entry.

## Entities

| Entity | Description |
|---|---|
| Climate | Turn the stove on/off (`heat` / `off`), set the target temperature (12–50 °C), choose the room fan speed (`off`, `1`–`5`, `high`, `auto`). Shows the room temperature and whether the stove is heating. |
| Power level | Burn power, from 1 to 5. |
| Status | Detailed stove state (heating up, burning, cooling, alarms…). |
| Pellet consumption | Total pellets burnt in kg, usable in the Energy dashboard. |
| Alarm | On when the stove reports an alarm (chimney, door, no pellet…). |
| Probe T2–T5 temperature | Raw probe temperatures, diagnostic, disabled by default. |

The stove is polled every 30 seconds.

## Known limitations

- While the stove shuts down (fire stop, cleaning, cooling), it is still reported as `heat` with an `idle` action.
- Some stoves (e.g. Jotul PF 1033) don't allow turning the room fan off: `off` falls back to speed 1.

## Development

```sh
uv sync --all-groups
uv run pytest
uv run --group lint ruff check .
docker compose up  # Home Assistant on http://localhost:8123 + a simulated cBox reachable as "simulator"
```

## License

[LGPL-2.1](LICENSE)
