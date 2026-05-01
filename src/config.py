"""
Configuration module.

Reads, validates and exposes all input parameters from environment variables.
"""
import logging
import os
import sys
from dataclasses import dataclass
from datetime import date, timedelta

logger = logging.getLogger(__name__)

_KNOWN_ACTIVITY_TYPES = {
    "AlpineSki", "BackcountrySki", "Badminton", "Canoeing", "Crossfit",
    "EBikeRide", "Elliptical", "EMountainBikeRide", "Golf", "GravelRide",
    "Handcycle", "HighIntensityIntervalTraining", "Hike", "IceSkate",
    "InlineSkate", "Kayaking", "Kitesurf", "MountainBikeRide", "NordicSki",
    "Pickleball", "Pilates", "Racquetball", "Ride", "RockClimbing",
    "RollerSki", "Rowing", "Run", "Sail", "Skateboard", "Snowboard",
    "Snowshoe", "Soccer", "Squash", "StairStepper", "StandUpPaddling",
    "Surfing", "Swim", "TableTennis", "Tennis", "TrailRun", "Velomobile",
    "VirtualRide", "VirtualRow", "VirtualRun", "Walk", "WeightTraining",
    "Wheelchair", "Windsurf", "Workout", "Yoga",
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
    Exits with a descriptive error message if any required parameter is missing or invalid.
    """
    raw_mode = os.getenv("MODE")
    today = date.today()

    if raw_mode is None:
        # Default: partial scan of the last 30 days
        mode = "partial"
        date_from = today - timedelta(days=30)
        date_to = today
    elif raw_mode == "full":
        mode = "full"
        date_from = None
        date_to = None
    elif raw_mode == "partial":
        mode = "partial"
        if os.getenv("DATE_FROM") is None:
            logger.error("DATE_FROM is required when MODE=partial.")
            sys.exit(1)
        date_from = _parse_date(os.getenv("DATE_FROM"), "DATE_FROM")
        date_to = _parse_date(os.getenv("DATE_TO"), "DATE_TO") or today
    else:
        logger.error("Invalid value for MODE: '%s'. Must be 'full' or 'partial'.", raw_mode)
        sys.exit(1)

    if date_from is not None and date_to is not None and date_from > date_to:
        logger.error("DATE_FROM (%s) must be before or equal to DATE_TO (%s).", date_from, date_to)
        sys.exit(1)

    return Config(
        mode=mode,
        date_from=date_from,
        date_to=date_to,
        activity_types=_parse_activity_types(os.getenv("ACTIVITY_TYPES")),
        strava_client_id=os.getenv("STRAVA_CLIENT_ID", ""),
        strava_client_secret=os.getenv("STRAVA_CLIENT_SECRET", ""),
        strava_refresh_token=os.getenv("STRAVA_REFRESH_TOKEN", ""),
    )


def _parse_activity_types(raw: str | None) -> list[str]:
    """
    Parse a comma-separated list of activity types.

    Logs a warning for any unrecognised type.
    Returns an empty list if no filter is specified (meaning all types are included).
    """
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
    Exits with a descriptive error message if the format is invalid.
    """
    if raw is None:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        logger.error("Invalid date format for %s: '%s'. Expected YYYY-MM-DD.", param_name, raw)
        sys.exit(1)
