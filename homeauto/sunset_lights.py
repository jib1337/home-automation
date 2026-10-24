"""Turn Tapo lights on at sunset.

Run once a day (e.g. from cron at noon). The script works out today's sunset
for the configured location, sleeps until then (plus the configured offset),
and switches the configured devices on.

    python -m homeauto.sunset_lights            # wait for sunset, then switch on
    python -m homeauto.sunset_lights --now      # switch on immediately
    python -m homeauto.sunset_lights --dry-run  # print the plan, touch nothing
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import date, datetime, timedelta

from astral import LocationInfo
from astral.sun import sun

from homeauto.config import Location, load_config, location_from_config, tapo_credentials
from homeauto.tapo import set_power

log = logging.getLogger("sunset_lights")


def sunset_time(location: Location, day: date) -> datetime:
    info = LocationInfo(
        location.name, "", str(location.timezone), location.latitude, location.longitude
    )
    return sun(info.observer, date=day, tzinfo=location.timezone)["sunset"]


def trigger_time(location: Location, day: date, offset_minutes: int) -> datetime:
    """Sunset shifted by `offset_minutes` (negative means before sunset)."""
    return sunset_time(location, day) + timedelta(minutes=offset_minutes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--now", action="store_true", help="switch on immediately")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    config = load_config()
    location = location_from_config(config)
    settings = config.get("sunset_lights", {})
    devices = settings.get("devices", [])
    offset = int(settings.get("offset_minutes", 0))
    if not devices:
        log.error("No devices listed under [sunset_lights] in the config")
        return 1

    now = datetime.now(location.timezone)
    target = trigger_time(location, now.date(), offset)
    log.info(
        "Sunset in %s today: %s; lights on at %s",
        location.name,
        sunset_time(location, now.date()).strftime("%H:%M"),
        target.strftime("%H:%M"),
    )

    if args.dry_run:
        log.info("Dry run: would switch on %s", ", ".join(devices))
        return 0

    if not args.now:
        if now >= target:
            log.info("Already past %s; nothing to do (use --now to force)", target.strftime("%H:%M"))
            return 0
        wait = (target - now).total_seconds()
        log.info("Sleeping %.0f minutes", wait / 60)
        time.sleep(wait)

    username, password = tapo_credentials()
    results = asyncio.run(set_power(devices, True, username, password))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
