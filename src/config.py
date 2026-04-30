"""
Configuration module.

Reads, validates and exposes all input parameters from environment variables.
"""

from dataclasses import dataclass
from datetime import date


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
    ...


def _parse_activity_types(raw: str | None) -> list[str]:
    """
    Parse a comma-separated list of activity types.

    Logs a warning for any unrecognised type.
    Returns an empty list if no filter is specified (meaning all types are included).
    """
    ...


def _parse_date(raw: str | None, param_name: str) -> date | None:
    """
    Parse an ISO 8601 date string (YYYY-MM-DD).

    Returns None if the input is None.
    Exits with a descriptive error message if the format is invalid.
    """
    ...
