"""
Unit tests for the report generation module.
"""

from datetime import date, datetime

from main import classify_activities
from report import ReportData, generate_report, print_summary, write_report
from strava import Activity


def _activity(
    id=1,
    name="Morning Run",
    activity_type="Run",
    start_date=date(2024, 2, 14),
    visibility="everyone",
    has_pr=False,
):
    return Activity(
        id=id,
        name=name,
        activity_type=activity_type,
        start_date=start_date,
        visibility=visibility,
        has_pr=has_pr,
    )


def _report_data(**kwargs):
    defaults = {
        "generated_at": datetime(2024, 6, 15, 8, 30, 0),
        "mode": "partial",
        "date_from": "2024-01-01",
        "date_to": "2024-03-31",
        "activity_types": ["Run"],
        "scanned_count": 10,
        "case_a": [],
        "case_b": [],
    }
    return ReportData(**{**defaults, **kwargs})


class TestGenerateReport:
    """Tests for generate_report()."""

    def test_full_mode_shows_all_time_date_range(self):
        report = generate_report(_report_data(mode="full", date_from=None, date_to=None))
        assert "All time" in report

    def test_report_contains_correct_header_metadata(self):
        data = _report_data(
            scanned_count=10,
            case_a=[_activity(id=1, visibility="followers_only", has_pr=True)],
            case_b=[_activity(id=2), _activity(id=3)],
        )
        report = generate_report(data)
        assert "Mode: partial" in report
        assert "2024-01-01" in report
        assert "2024-03-31" in report
        assert "Run" in report
        assert "Activities scanned: 10" in report
        assert "Inconsistencies found: 3" in report

    def test_case_a_section_lists_correct_activities(self):
        activity = _activity(
            id=123456789,
            name="Morning Run",
            activity_type="Run",
            start_date=date(2024, 2, 14),
            visibility="followers_only",
            has_pr=True,
        )
        report = generate_report(_report_data(case_a=[activity]))
        assert "Morning Run" in report
        assert "2024-02-14" in report
        assert "Run" in report
        assert "123456789" in report

    def test_case_b_section_lists_correct_activities(self):
        activity = _activity(
            id=987, name="Evening Ride", activity_type="Ride", visibility="everyone", has_pr=False
        )
        report = generate_report(_report_data(case_b=[activity]))
        assert "Evening Ride" in report
        assert "987" in report

    def test_no_inconsistencies_message_when_both_cases_empty(self):
        report = generate_report(_report_data(case_a=[], case_b=[]))
        assert "_No inconsistencies found._" in report

    def test_activity_link_format(self):
        activity = _activity(id=123456789, visibility="followers_only", has_pr=True)
        report = generate_report(_report_data(case_a=[activity]))
        assert "https://www.strava.com/activities/123456789" in report

    def test_report_does_not_contain_credentials(self):
        report = generate_report(_report_data())
        assert "STRAVA_CLIENT_SECRET" not in report
        assert "STRAVA_REFRESH_TOKEN" not in report
        assert "STRAVA_CLIENT_ID" not in report

    def test_partial_report_contains_warning_banner(self):
        report = generate_report(_report_data(is_partial=True))
        assert "Partial report" in report

    def test_complete_report_does_not_contain_warning_banner(self):
        report = generate_report(_report_data(is_partial=False))
        assert "Partial report" not in report


class TestWriteReport:
    """Tests for write_report()."""

    def test_filename_includes_timestamp(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = write_report("# Report", datetime(2024, 6, 15, 8, 30, 0))
        assert "reports/strava-visibility-report-20240615-083000" in path


class TestPrintSummary:
    """Tests for print_summary()."""

    def test_summary_includes_scanned_count_and_case_counts(self, capsys):
        data = _report_data(
            scanned_count=15,
            case_a=[
                _activity(id=1, visibility="followers_only", has_pr=True),
                _activity(id=2, visibility="only_me", has_pr=True),
            ],
            case_b=[_activity(id=3, visibility="everyone", has_pr=False)],
        )
        print_summary(data)
        output = capsys.readouterr().out
        assert "15" in output
        assert "2" in output
        assert "1" in output


class TestClassifyActivities:
    """Tests for classify_activities() in main.py."""

    def test_followers_only_with_pr_is_case_a(self):
        a = _activity(visibility="followers_only", has_pr=True)
        case_a, case_b = classify_activities([a])
        assert a in case_a
        assert a not in case_b

    def test_only_me_with_pr_is_case_a(self):
        a = _activity(visibility="only_me", has_pr=True)
        case_a, case_b = classify_activities([a])
        assert a in case_a
        assert a not in case_b

    def test_public_without_pr_is_case_b(self):
        a = _activity(visibility="everyone", has_pr=False)
        case_a, case_b = classify_activities([a])
        assert a not in case_a
        assert a in case_b

    def test_public_with_pr_is_not_reported(self):
        a = _activity(visibility="everyone", has_pr=True)
        case_a, case_b = classify_activities([a])
        assert a not in case_a
        assert a not in case_b

    def test_followers_only_without_pr_is_not_reported(self):
        a = _activity(visibility="followers_only", has_pr=False)
        case_a, case_b = classify_activities([a])
        assert a not in case_a
        assert a not in case_b

    def test_only_me_without_pr_is_not_reported(self):
        a = _activity(visibility="only_me", has_pr=False)
        case_a, case_b = classify_activities([a])
        assert a not in case_a
        assert a not in case_b
