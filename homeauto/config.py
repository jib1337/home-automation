"""Loads config.toml and device credentials from the environment."""

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    timezone: ZoneInfo


def load_config(path: Path | None = None) -> dict:
    """Read the TOML config from `path`, $HOMEAUTO_CONFIG, or the repo root."""
    path = path or Path(os.environ.get("HOMEAUTO_CONFIG", DEFAULT_CONFIG_PATH))
    if not path.exists():
        raise SystemExit(
            f"Config not found at {path}. Copy config.example.toml to config.toml and edit it."
        )
    with path.open("rb") as f:
        return tomllib.load(f)


def location_from_config(config: dict) -> Location:
    loc = config["location"]
    return Location(
        name=loc.get("name", "home"),
        latitude=float(loc["latitude"]),
        longitude=float(loc["longitude"]),
        timezone=ZoneInfo(loc["timezone"]),
    )


def tapo_credentials() -> tuple[str, str]:
    """Tapo devices authenticate with the TP-Link/Tapo app account."""
    username = os.environ.get("TAPO_USERNAME")
    password = os.environ.get("TAPO_PASSWORD")
    if not username or not password:
        raise SystemExit("Set TAPO_USERNAME and TAPO_PASSWORD (your Tapo app login).")
    return username, password
