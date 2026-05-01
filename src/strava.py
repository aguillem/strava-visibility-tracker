"""
Strava API client module.

Handles authentication and all data fetching from the Strava API.
"""

import logging
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import requests

_TOKEN_URL = "https://www.strava.com/oauth/token"
_API_BASE = "https://www.strava.com/api/v3"

logger = logging.getLogger(__name__)


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
    logger.info("Requesting access token...")
    response = requests.post(
        _TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    if not response.ok:
        logger.error("Authentication with the Strava API failed (HTTP %d).", response.status_code)
        sys.exit(1)
    logger.info("Access token obtained.")
    return response.json()["access_token"]


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
    headers = {"Authorization": f"Bearer {access_token}"}
    params: dict = {"per_page": 200, "page": 1}

    if mode == "partial":
        if date_from is not None:
            params["after"] = int(
                datetime(date_from.year, date_from.month, date_from.day, tzinfo=UTC).timestamp()
            )
        if date_to is not None:
            next_day = date_to + timedelta(days=1)
            params["before"] = int(
                datetime(next_day.year, next_day.month, next_day.day, tzinfo=UTC).timestamp()
            )

    logger.info("Fetching activities (mode=%s)...", mode)
    all_activities = []

    while True:
        logger.info("Fetching page %d...", params["page"])
        response = requests.get(f"{_API_BASE}/athlete/activities", headers=headers, params=params)

        if response.status_code == 429:
            logger.error("Strava API rate limit reached. Please wait before running again.")
            sys.exit(1)

        if not response.ok:
            logger.error(
                "Strava API error (HTTP %d) while fetching activities.", response.status_code
            )
            sys.exit(1)

        page = response.json()
        if not page:
            break

        for raw in page:
            sport_type = raw.get("sport_type", raw.get("type", ""))
            if activity_types and sport_type not in activity_types:
                continue

            logger.debug(
                "Fetching details for '%s' (%s, id=%d)...", raw["name"], sport_type, raw["id"]
            )
            detail = _fetch_activity_detail(access_token, raw["id"])

            all_activities.append(
                Activity(
                    id=raw["id"],
                    name=raw["name"],
                    activity_type=sport_type,
                    start_date=date.fromisoformat(raw["start_date_local"][:10]),
                    visibility=raw["visibility"],
                    has_pr=_has_personal_record(detail),
                )
            )

        params["page"] += 1

    count = len(all_activities)
    logger.info("Fetched %d %s.", count, "activity" if count == 1 else "activities")
    return all_activities


def _fetch_activity_detail(access_token: str, activity_id: int) -> dict:
    """
    Fetch the full detail of a single activity, including segment efforts.

    Retries once on 5xx errors.
    Exits gracefully on 429 rate limit errors.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{_API_BASE}/activities/{activity_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        logger.error("Strava API rate limit reached. Please wait before running again.")
        sys.exit(1)

    if response.status_code >= 500:
        logger.warning(
            "Server error (HTTP %d) for activity %d, retrying...", response.status_code, activity_id
        )
        response = requests.get(url, headers=headers)
        if response.status_code >= 500:
            logger.error(
                "Strava API server error (HTTP %d) for activity %d after retry.",
                response.status_code,
                activity_id,
            )
            sys.exit(1)

    if not response.ok:
        logger.error(
            "Strava API error (HTTP %d) for activity %d.", response.status_code, activity_id
        )
        sys.exit(1)

    return response.json()


def _has_personal_record(activity_detail: dict) -> bool:
    """
    Return True if the activity contains at least one segment effort with pr_rank = 1.

    Returns False if the activity has no segment efforts.
    """
    return any(effort.get("pr_rank") == 1 for effort in activity_detail.get("segment_efforts", []))
