"""
Strava Visibility Tracker

Entry point and orchestration.

Detects Strava activity visibility inconsistencies based on segment personal records
and generates a Markdown report listing activities that should be reviewed.
"""
from datetime import datetime

from dotenv import load_dotenv

from config import load_config
from report import ReportData, generate_report, print_summary, write_report
from strava import Activity, fetch_activities, get_access_token


def classify_activities(activities: list[Activity]) -> tuple[list[Activity], list[Activity]]:
    """
    Classify activities into two inconsistency cases.

    Case A: has a PR but visibility is followers_only or only_me
    Case B: no PR but visibility is public

    Returns a tuple (case_a, case_b).
    """
    case_a = [a for a in activities if a.has_pr and a.visibility in ("followers_only", "only_me")]
    case_b = [a for a in activities if not a.has_pr and a.visibility == "public"]
    return case_a, case_b


def main() -> None:
    """
    Main orchestration function.

    1. Load and validate configuration
    2. Authenticate with Strava
    3. Fetch activities
    4. Classify inconsistencies
    5. Generate and write the report
    6. Print summary to console
    """
    load_dotenv()

    config = load_config()
    access_token = get_access_token(
        config.strava_client_id,
        config.strava_client_secret,
        config.strava_refresh_token,
    )
    activities = fetch_activities(
        access_token,
        config.mode,
        config.date_from,
        config.date_to,
        config.activity_types,
    )
    case_a, case_b = classify_activities(activities)

    now = datetime.now()
    data = ReportData(
        generated_at=now,
        mode=config.mode,
        date_from=str(config.date_from) if config.date_from else None,
        date_to=str(config.date_to) if config.date_to else None,
        activity_types=config.activity_types,
        scanned_count=len(activities),
        case_a=case_a,
        case_b=case_b,
    )

    content = generate_report(data)
    path = write_report(content, now)
    print_summary(data)
    print(f"\nReport written to: {path}")


if __name__ == "__main__":
    main()
