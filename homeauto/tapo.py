"""Controls Tapo devices directly over the local network via python-kasa."""

import asyncio
import logging

from kasa import Discover

log = logging.getLogger(__name__)


async def _set_power(host: str, on: bool, username: str, password: str) -> bool:
    device = None
    try:
        device = await Discover.discover_single(host, username=username, password=password)
        if device is None:
            log.error("%s: no device responded", host)
            return False
        await device.update()
        await (device.turn_on() if on else device.turn_off())
        log.info("%s (%s): turned %s", host, device.alias, "on" if on else "off")
        return True
    except Exception:
        log.exception("%s: failed to turn %s", host, "on" if on else "off")
        return False
    finally:
        if device is not None:
            await device.disconnect()


async def set_power(hosts: list[str], on: bool, username: str, password: str) -> dict[str, bool]:
    """Switch every host concurrently; returns host -> success."""
    results = await asyncio.gather(*(_set_power(h, on, username, password) for h in hosts))
    return dict(zip(hosts, results))
