"""
Strava Visibility Tracker

Entry point and orchestration.

Detects activities that have a segment PR but are not publicly visible,
and generates a Markdown report listing them for manual review.
"""

import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from config import ConfigError, load_config
from report import ReportData, generate_report, print_summary, write_report
from strava import Activity, RateLimitError, StravaAPIError, fetch_activities, get_access_token

logger = logging.getLogger(__name__)


def find_hidden_prs(activities: list[Activity]) -> list[Activity]:
    """Return activities that have a PR but are not visible to everyone."""
    return [a for a in activities if a.has_pr and a.visibility in ("followers_only", "only_me")]


def main() -> None:
    """
    Main orchestration function.

    1. Load and validate configuration
    2. Authenticate with Strava
    3. Fetch activities
    4. Find hidden PRs
    5. Generate and write the report
    6. Print summary to console
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    load_dotenv()

    try:
        config = load_config()
    except ConfigError as e:
        logger.error(str(e))
        sys.exit(1)

    date_range = f"{config.date_from} → {config.date_to}" if config.date_from else "all time"
    types_display = ", ".join(config.activity_types) if config.activity_types else "all"
    logger.info(
        "Mode: %s | Date range: %s | Activity types: %s", config.mode, date_range, types_display
    )

    try:
        access_token = get_access_token(
            config.strava_client_id,
            config.strava_client_secret,
            config.strava_refresh_token,
        )
    except StravaAPIError as e:
        logger.error(str(e))
        sys.exit(1)

    is_partial = False
    try:
        activities = fetch_activities(
            access_token,
            config.mode,
            config.date_from,
            config.date_to,
            config.activity_types,
        )
    except RateLimitError as e:
        activities = e.partial_activities
        logger.warning(
            "Rate limit reached after %d activities. Generating partial report.", len(activities)
        )
        is_partial = True
    except StravaAPIError as e:
        logger.error(str(e))
        sys.exit(1)

    hidden_prs = find_hidden_prs(activities)
    logger.info("Hidden PRs found: %d", len(hidden_prs))

    now = datetime.now()
    data = ReportData(
        generated_at=now,
        mode=config.mode,
        date_from=str(config.date_from) if config.date_from else None,
        date_to=str(config.date_to) if config.date_to else None,
        activity_types=config.activity_types,
        scanned_count=len(activities),
        hidden_prs=hidden_prs,
        is_partial=is_partial,
    )

    content = generate_report(data)
    path = write_report(content, now)
    print_summary(data)
    print(f"\nReport written to: {path}")


if __name__ == "__main__":
    main()
