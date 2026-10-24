# home-automation

Scripts for controlling home IoT devices.

## Setup

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp config.example.toml config.toml   # then edit location and device IPs
export TAPO_USERNAME='you@example.com' TAPO_PASSWORD='...'   # Tapo app login
```

Requires Python 3.11+. Must run on the same LAN as the devices (e.g. a Raspberry Pi or home server).

## Scripts

### `sunset_lights` — Tapo lights on at sunset

Calculates today's sunset for `[location]`, waits until sunset plus `offset_minutes`,
then switches on every device in `[sunset_lights].devices`.
Devices are controlled directly over the LAN with [python-kasa](https://github.com/python-kasa/python-kasa).

```sh
python -m homeauto.sunset_lights --dry-run   # show today's sunset and the plan
python -m homeauto.sunset_lights --now       # test: switch on immediately
python -m homeauto.sunset_lights             # wait for sunset, then switch on
```

Schedule it once a day, before the earliest sunset of the year, e.g. with cron:

```cron
0 12 * * * cd /path/to/home-automation && TAPO_USERNAME=... TAPO_PASSWORD=... .venv/bin/python -m homeauto.sunset_lights >> sunset_lights.log 2>&1
```

If it starts after the trigger time it does nothing (pass `--now` to force).

## Tests

```sh
pip install -r requirements-dev.txt
python -m pytest
```
