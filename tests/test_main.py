"""
Integration test for the main orchestration function.
"""

from unittest.mock import patch

import responses

from main import main

TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def _activity_stub(
    id, visibility="public", sport_type="Run", start_date="2024-03-15T08:00:00Z", name="Morning Run"
):
    return {
        "id": id,
        "name": name,
        "sport_type": sport_type,
        "start_date_local": start_date,
        "visibility": visibility,
    }


def _detail_stub(id, pr=False):
    efforts = [{"pr_rank": 1}] if pr else []
    return {"id": id, "segment_efforts": efforts}


def _set_env(monkeypatch):
    for key in ("DATE_FROM", "DATE_TO", "ACTIVITY_TYPES"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("MODE", "full")
    monkeypatch.setenv("STRAVA_CLIENT_ID", "123")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret")
    monkeypatch.setenv("STRAVA_REFRESH_TOKEN", "refresh")


class TestMain:
    @responses.activate
    def test_full_run_writes_report_and_prints_summary(self, monkeypatch, tmp_path, capsys):
        _set_env(monkeypatch)
        monkeypatch.chdir(tmp_path)

        responses.add(responses.POST, TOKEN_URL, json={"access_token": "token"}, status=200)
        responses.add(
            responses.GET,
            ACTIVITIES_URL,
            json=[
                _activity_stub(1, visibility="followers_only", name="Case A Run"),
                _activity_stub(2, visibility="public", name="Case B Ride"),
            ],
            status=200,
        )
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/1",
            json=_detail_stub(1, pr=True),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/2",
            json=_detail_stub(2, pr=False),
            status=200,
        )

        with patch("main.load_dotenv"):
            main()

        reports = list(tmp_path.glob("reports/strava-visibility-report-*.md"))
        assert len(reports) == 1
        content = reports[0].read_text(encoding="utf-8")
        assert "Case A Run" in content
        assert "Case B Ride" in content
        assert "https://www.strava.com/activities/1" in content

        out = capsys.readouterr().out
        assert "Activities scanned: 2" in out
        assert "Case A (should be public): 1" in out
        assert "Case B (should be followers only): 1" in out
        assert "Report written to:" in out

    @responses.activate
    def test_rate_limit_generates_partial_report(self, monkeypatch, tmp_path, capsys):
        _set_env(monkeypatch)
        monkeypatch.chdir(tmp_path)

        responses.add(responses.POST, TOKEN_URL, json={"access_token": "token"}, status=200)
        responses.add(
            responses.GET,
            ACTIVITIES_URL,
            json=[
                _activity_stub(1, visibility="followers_only", name="Completed Run"),
                _activity_stub(2, visibility="public", name="Rate Limited Run"),
            ],
            status=200,
        )
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/1",
            json=_detail_stub(1, pr=True),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/2",
            status=429,
        )

        with patch("main.load_dotenv"):
            main()

        reports = list(tmp_path.glob("reports/strava-visibility-report-*.md"))
        assert len(reports) == 1
        content = reports[0].read_text(encoding="utf-8")
        assert "Partial report" in content
        assert "Completed Run" in content

        out = capsys.readouterr().out
        assert "Activities scanned: 1" in out
        assert "Report written to:" in out
