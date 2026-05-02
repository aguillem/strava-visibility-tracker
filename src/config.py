"""
Configuration module.

Reads, validates and exposes all input parameters from environment variables.
"""

import os
from dataclasses import dataclass
from datetime import date, timedelta


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""


_KNOWN_ACTIVITY_TYPES = {
    "AlpineSki",
    "BackcountrySki",
    "Badminton",
    "Canoeing",
    "Crossfit",
    "EBikeRide",
    "Elliptical",
    "EMountainBikeRide",
    "Golf",
    "GravelRide",
    "Handcycle",
    "HighIntensityIntervalTraining",
    "Hike",
    "IceSkate",
    "InlineSkate",
    "Kayaking",
    "Kitesurf",
    "MountainBikeRide",
    "NordicSki",
    "Pickleball",
    "Pilates",
    "Racquetball",
    "Ride",
    "RockClimbing",
    "RollerSki",
    "Rowing",
    "Run",
    "Sail",
    "Skateboard",
    "Snowboard",
    "Snowshoe",
    "Soccer",
    "Squash",
    "StairStepper",
    "StandUpPaddling",
    "Surfing",
    "Swim",
    "TableTennis",
    "Tennis",
    "TrailRun",
    "Velomobile",
    "VirtualRide",
    "VirtualRow",
    "VirtualRun",
    "Walk",
    "WeightTraining",
    "Wheelchair",
    "Windsurf",
    "Workout",
    "Yoga",
}


@dataclass
class Config:
    """Holds all validated configuration parameters for a script run."""

    mode: str
    date_from: date | None
    date_to: date | None
    activity_types: list[str]
    strava_client_id: str
    strava_client_secret: str
    strava_refresh_token: str


def load_config() -> Config:
    """
    Read and validate all parameters from environment variables.

    Returns a Config instance with all validated values.
    Raises ConfigError if any required parameter is missing or invalid.
    """
    raw_mode = os.getenv("MODE")
    today = date.today()

    if raw_mode is None or raw_mode == "partial":
        mode = "partial"
        if os.getenv("DATE_FROM") is None:
            date_from = today - timedelta(days=30)
            date_to = today
        else:
            date_from = _parse_date(os.getenv("DATE_FROM"), "DATE_FROM")
            date_to = _parse_date(os.getenv("DATE_TO"), "DATE_TO") or today
    elif raw_mode == "full":
        mode = "full"
        date_from = None
        date_to = None
    else:
        raise ConfigError(f"Invalid value for MODE: '{raw_mode}'. Must be 'full' or 'partial'.")

    if date_from is not None and date_to is not None and date_from > date_to:
        raise ConfigError(
            f"DATE_FROM ({date_from}) must be before or equal to DATE_TO ({date_to})."
        )

    client_id = os.getenv("STRAVA_CLIENT_ID", "")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET", "")
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN", "")

    for name, value in [
        ("STRAVA_CLIENT_ID", client_id),
        ("STRAVA_CLIENT_SECRET", client_secret),
        ("STRAVA_REFRESH_TOKEN", refresh_token),
    ]:
        if not value:
            raise ConfigError(f"Missing required environment variable: {name}.")

    return Config(
        mode=mode,
        date_from=date_from,
        date_to=date_to,
        activity_types=_parse_activity_types(os.getenv("ACTIVITY_TYPES")),
        strava_client_id=client_id,
        strava_client_secret=client_secret,
        strava_refresh_token=refresh_token,
    )


def _parse_activity_types(raw: str | None) -> list[str]:
    """
    Parse a comma-separated list of activity types.

    Logs a warning for any unrecognised type.
    Returns an empty list if no filter is specified (meaning all types are included).
    """
    import logging

    logger = logging.getLogger(__name__)

    if raw is None:
        return []
    types = [t.strip() for t in raw.split(",") if t.strip()]
    for t in types:
        if t not in _KNOWN_ACTIVITY_TYPES:
            logger.warning("'%s' is not a recognised Strava activity type.", t)
    return types


def _parse_date(raw: str | None, param_name: str) -> date | None:
    """
    Parse an ISO 8601 date string (YYYY-MM-DD).

    Returns None if the input is None.
    Raises ConfigError if the format is invalid.
    """
    if raw is None:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ConfigError(f"Invalid date format for {param_name}: '{raw}'. Expected YYYY-MM-DD.")
