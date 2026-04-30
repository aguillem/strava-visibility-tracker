"""
Strava API client module.

Handles authentication and all data fetching from the Strava API.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class Activity:
    """Represents a Strava activity with the fields relevant to this tool."""

    id: int
    name: str
    activity_type: str
    start_date: date
    visibility: str  # "public", "followers_only" or "only_me"
    has_pr: bool


def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    """
    Obtain a fresh access token from the Strava OAuth endpoint.

    Uses the refresh token grant type.
    Exits with a descriptive error message if authentication fails.
    """
    ...


def fetch_activities(
    access_token: str,
    mode: str,
    date_from: date | None,
    date_to: date | None,
    activity_types: list[str],
) -> list[Activity]:
    """
    Fetch all activities matching the given filters from the Strava API.

    Handles pagination automatically.
    Applies activity type filtering.
    Respects rate limits and handles API errors gracefully.
    """
    ...


def _fetch_activity_detail(access_token: str, activity_id: int) -> dict:
    """
    Fetch the full detail of a single activity, including segment efforts.

    Retries once on 5xx errors.
    Exits gracefully on 429 rate limit errors.
    """
    ...


def _has_personal_record(activity_detail: dict) -> bool:
    """
    Return True if the activity contains at least one segment effort with pr_rank = 1.

    Returns False if the activity has no segment efforts.
    """
    ...
