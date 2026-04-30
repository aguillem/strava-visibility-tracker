"""
Report generation module.

Builds the Markdown report from the list of inconsistent activities.
"""

from dataclasses import dataclass
from datetime import datetime

from strava import Activity


@dataclass
class ReportData:
    """Holds all data needed to generate the report."""

    generated_at: datetime
    mode: str
    date_from: str | None
    date_to: str | None
    activity_types: list[str]
    scanned_count: int
    case_a: list[Activity]  # has PR but not public
    case_b: list[Activity]  # no PR but public


def generate_report(data: ReportData) -> str:
    """
    Generate the full Markdown report content as a string.
    """
    ...


def write_report(content: str, generated_at: datetime) -> str:
    """
    Write the report content to a Markdown file.

    The filename includes the run timestamp: strava-visibility-report-YYYYMMDD-HHmmss.md
    Returns the path of the generated file.
    """
    ...


def print_summary(data: ReportData) -> None:
    """
    Print a short summary to stdout.

    Includes total activities scanned, Case A count and Case B count.
    """
    ...


def _activity_url(activity_id: int) -> str:
    """
    Return the public Strava URL for a given activity ID.
    """
    ...
