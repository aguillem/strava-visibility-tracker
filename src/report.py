"""
Report generation module.

Builds the Markdown report from the list of inconsistent activities.
"""

import os
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
    is_partial: bool = False


def generate_report(data: ReportData) -> str:
    """
    Generate the full Markdown report content as a string.
    """
    total = len(data.case_a) + len(data.case_b)
    types_display = ", ".join(data.activity_types) if data.activity_types else "All"

    if data.date_from and data.date_to:
        date_range = f"{data.date_from} → {data.date_to}"
    else:
        date_range = "All time"

    lines = [
        "# Strava Visibility Report",
        "",
        f"Generated: {data.generated_at.isoformat(timespec='seconds')}",
        "",
    ]

    if data.is_partial:
        lines += [
            "> ⚠️ **Partial report** — the Strava API rate limit was reached before all activities"
            " could be fetched. The results below cover only the activities scanned so far.",
            "",
        ]

    lines += [
        f"- Mode: {data.mode}",
        f"- Date range: {date_range}",
        f"- Activity types filter: {types_display}",
        f"- Activities scanned: {data.scanned_count}",
        f"- Inconsistencies found: {total}",
        "",
        "---",
        "",
        "## Case A — Should be PUBLIC",
        "",
        "Activities that have a segment PR but are not visible to everyone.",
        "",
    ]

    if data.case_a:
        lines += ["| Name | Date | Type | Link |", "|------|------|------|------|"]
        for a in data.case_a:
            lines.append(
                f"| {a.name} | {a.start_date} | {a.activity_type} | {_activity_url(a.id)} |"
            )
    else:
        lines.append("_No inconsistencies found._")

    lines += [
        "",
        "---",
        "",
        "## Case B — Should be FOLLOWERS ONLY",
        "",
        "Activities with no segment PR that are public.",
        "",
    ]

    if data.case_b:
        lines += ["| Name | Date | Type | Link |", "|------|------|------|------|"]
        for a in data.case_b:
            lines.append(
                f"| {a.name} | {a.start_date} | {a.activity_type} | {_activity_url(a.id)} |"
            )
    else:
        lines.append("_No inconsistencies found._")

    return "\n".join(lines) + "\n"


def write_report(content: str, generated_at: datetime) -> str:
    """
    Write the report content to a Markdown file.

    The filename includes the run timestamp: strava-visibility-report-YYYYMMDD-HHmmss.md
    Returns the path of the generated file.
    """
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/strava-visibility-report-{generated_at.strftime('%Y%m%d-%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def print_summary(data: ReportData) -> None:
    """
    Print a short summary to stdout.

    Includes total activities scanned, Case A count and Case B count.
    """
    print(f"Activities scanned: {data.scanned_count}")
    print(f"Case A (should be public): {len(data.case_a)}")
    print(f"Case B (should be followers only): {len(data.case_b)}")


def _activity_url(activity_id: int) -> str:
    """
    Return the public Strava URL for a given activity ID.
    """
    return f"https://www.strava.com/activities/{activity_id}"
