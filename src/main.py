"""
Strava Visibility Tracker

Entry point and orchestration.

Detects Strava activity visibility inconsistencies based on segment personal records
and generates a Markdown report listing activities that should be reviewed.
"""

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
    ...


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
    ...


if __name__ == "__main__":
    main()
