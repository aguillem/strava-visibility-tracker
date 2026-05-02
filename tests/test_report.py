"""
Unit tests for the report generation module.
"""

from datetime import date, datetime

from main import find_hidden_prs
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
        "hidden_prs": [],
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
            hidden_prs=[
                _activity(id=1, visibility="followers_only", has_pr=True),
                _activity(id=2, visibility="followers_only", has_pr=True),
                _activity(id=3, visibility="only_me", has_pr=True),
            ],
        )
        report = generate_report(data)
        assert "Mode: partial" in report
        assert "2024-01-01" in report
        assert "2024-03-31" in report
        assert "Run" in report
        assert "Activities scanned: 10" in report
        assert "Hidden PRs found: 3" in report

    def test_hidden_prs_section_lists_correct_activities(self):
        activity = _activity(
            id=123456789,
            name="Morning Run",
            activity_type="Run",
            start_date=date(2024, 2, 14),
            visibility="followers_only",
            has_pr=True,
        )
        report = generate_report(_report_data(hidden_prs=[activity]))
        assert "Morning Run" in report
        assert "2024-02-14" in report
        assert "Run" in report
        assert "123456789" in report

    def test_no_hidden_prs_message_when_empty(self):
        report = generate_report(_report_data(hidden_prs=[]))
        assert "_No hidden PRs found._" in report

    def test_activity_link_format(self):
        activity = _activity(id=123456789, visibility="followers_only", has_pr=True)
        report = generate_report(_report_data(hidden_prs=[activity]))
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

    def test_pipe_in_activity_name_is_escaped(self):
        activity = _activity(id=1, name="Run | Race", visibility="followers_only", has_pr=True)
        report = generate_report(_report_data(hidden_prs=[activity]))
        assert r"Run \| Race" in report


class TestWriteReport:
    """Tests for write_report()."""

    def test_filename_includes_timestamp(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = write_report("# Report", datetime(2024, 6, 15, 8, 30, 0))
        assert "reports/strava-visibility-report-20240615-083000" in path


class TestPrintSummary:
    """Tests for print_summary()."""

    def test_summary_includes_scanned_count_and_hidden_prs(self, capsys):
        data = _report_data(
            scanned_count=15,
            hidden_prs=[
                _activity(id=1, visibility="followers_only", has_pr=True),
                _activity(id=2, visibility="only_me", has_pr=True),
            ],
        )
        print_summary(data)
        output = capsys.readouterr().out
        assert "15" in output
        assert "2" in output


class TestFindHiddenPrs:
    """Tests for find_hidden_prs() in main.py."""

    def test_followers_only_with_pr_is_hidden(self):
        a = _activity(visibility="followers_only", has_pr=True)
        assert a in find_hidden_prs([a])

    def test_only_me_with_pr_is_hidden(self):
        a = _activity(visibility="only_me", has_pr=True)
        assert a in find_hidden_prs([a])

    def test_public_with_pr_is_not_hidden(self):
        a = _activity(visibility="everyone", has_pr=True)
        assert a not in find_hidden_prs([a])

    def test_followers_only_without_pr_is_not_hidden(self):
        a = _activity(visibility="followers_only", has_pr=False)
        assert a not in find_hidden_prs([a])

    def test_only_me_without_pr_is_not_hidden(self):
        a = _activity(visibility="only_me", has_pr=False)
        assert a not in find_hidden_prs([a])

    def test_public_without_pr_is_not_hidden(self):
        a = _activity(visibility="everyone", has_pr=False)
        assert a not in find_hidden_prs([a])
