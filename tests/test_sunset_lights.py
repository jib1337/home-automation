from datetime import date
from zoneinfo import ZoneInfo

import pytest

from homeauto.config import Location
from homeauto.sunset_lights import main, sunset_time, trigger_time

SYDNEY = Location("Sydney", -33.8688, 151.2093, ZoneInfo("Australia/Sydney"))


def test_sunset_is_local_evening():
    # Summer solstice in Sydney: sunset is just after 20:00 AEDT.
    sunset = sunset_time(SYDNEY, date(2026, 12, 21))
    assert sunset.utcoffset().total_seconds() == 11 * 3600
    assert (sunset.hour, sunset.minute) >= (20, 0)
    assert sunset.hour < 21


def test_trigger_time_applies_offset():
    day = date(2026, 6, 21)
    assert (sunset_time(SYDNEY, day) - trigger_time(SYDNEY, day, -15)).total_seconds() == 900


def test_dry_run_does_not_need_credentials(tmp_path, monkeypatch):
    config = tmp_path / "config.toml"
    config.write_text(
        '[location]\nlatitude = -33.8688\nlongitude = 151.2093\ntimezone = "Australia/Sydney"\n'
        '[sunset_lights]\ndevices = ["192.0.2.1"]\n'
    )
    monkeypatch.setenv("HOMEAUTO_CONFIG", str(config))
    monkeypatch.delenv("TAPO_USERNAME", raising=False)
    assert main(["--dry-run"]) == 0


def test_missing_devices_fails(tmp_path, monkeypatch):
    config = tmp_path / "config.toml"
    config.write_text(
        '[location]\nlatitude = 0\nlongitude = 0\ntimezone = "UTC"\n[sunset_lights]\n'
    )
    monkeypatch.setenv("HOMEAUTO_CONFIG", str(config))
    assert main(["--dry-run"]) == 1
