"""
Unit tests for the Strava API client module.
All HTTP calls are mocked — no real network requests are made.
"""

from datetime import date

import pytest
import requests
import responses

from strava import (
    RateLimitError,
    StravaAPIError,
    _fetch_activity_detail,
    _has_personal_record,
    fetch_activities,
    get_access_token,
)


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Authorization": "Bearer test_token"})
    return session


TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def _activity_stub(
    id=1,
    name="Morning Run",
    sport_type="Run",
    start_date="2024-03-15T08:00:00Z",
    visibility="everyone",
    workout_type=0,
):
    return {
        "id": id,
        "name": name,
        "sport_type": sport_type,
        "start_date_local": start_date,
        "visibility": visibility,
        "workout_type": workout_type,
    }


def _detail_stub(id=1, segment_efforts=None):
    return {"id": id, "segment_efforts": segment_efforts or []}


def _segment(pr_rank=None):
    return {"pr_rank": pr_rank}


class TestGetAccessToken:
    """Tests for get_access_token()."""

    @responses.activate
    def test_returns_access_token_on_success(self):
        responses.add(responses.POST, TOKEN_URL, json={"access_token": "my_token"}, status=200)
        assert get_access_token("id", "secret", "token") == "my_token"

    @responses.activate
    def test_raises_on_authentication_failure(self):
        responses.add(responses.POST, TOKEN_URL, json={"message": "Unauthorized"}, status=401)
        with pytest.raises(StravaAPIError):
            get_access_token("id", "bad_secret", "bad_token")

    @responses.activate
    def test_raises_when_access_token_missing_from_response(self):
        responses.add(responses.POST, TOKEN_URL, json={"athlete": {}}, status=200)
        with pytest.raises(StravaAPIError, match="access_token"):
            get_access_token("id", "secret", "token")


class TestFetchActivities:
    """Tests for fetch_activities()."""

    @responses.activate
    def test_returns_all_activities_in_full_mode(self):
        responses.add(
            responses.GET, ACTIVITIES_URL, json=[_activity_stub(1), _activity_stub(2)], status=200
        )
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        for i in [1, 2]:
            responses.add(
                responses.GET,
                f"https://www.strava.com/api/v3/activities/{i}",
                json=_detail_stub(i),
                status=200,
            )
        result = fetch_activities("token", "full", None, None, [])
        assert len(result) == 2

    @responses.activate
    def test_workout_type_is_read_from_api_response(self):
        responses.add(
            responses.GET,
            ACTIVITIES_URL,
            json=[_activity_stub(1, workout_type=1)],
            status=200,
        )
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/1",
            json=_detail_stub(1),
            status=200,
        )
        result = fetch_activities("token", "full", None, None, [])
        assert len(result) == 1
        assert result[0].workout_type == 1

    @responses.activate
    def test_filters_by_date_range_in_partial_mode(self):
        responses.add(
            responses.GET,
            ACTIVITIES_URL,
            json=[_activity_stub(1, start_date="2024-02-15T08:00:00Z")],
            status=200,
        )
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/1",
            json=_detail_stub(1),
            status=200,
        )
        result = fetch_activities("token", "partial", date(2024, 1, 1), date(2024, 3, 31), [])
        assert len(result) == 1
        assert result[0].start_date == date(2024, 2, 15)

    @responses.activate
    def test_filters_by_activity_type(self):
        responses.add(
            responses.GET,
            ACTIVITIES_URL,
            json=[_activity_stub(1, sport_type="Run"), _activity_stub(2, sport_type="Ride")],
            status=200,
        )
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        # Only the Run activity detail should be fetched
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/1",
            json=_detail_stub(1),
            status=200,
        )
        result = fetch_activities("token", "full", None, None, ["Run"])
        assert len(result) == 1
        assert result[0].activity_type == "Run"

    @responses.activate
    def test_handles_pagination(self):
        page1 = [_activity_stub(i) for i in range(1, 4)]
        page2 = [_activity_stub(i) for i in range(4, 6)]
        responses.add(responses.GET, ACTIVITIES_URL, json=page1, status=200)
        responses.add(responses.GET, ACTIVITIES_URL, json=page2, status=200)
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        for i in range(1, 6):
            responses.add(
                responses.GET,
                f"https://www.strava.com/api/v3/activities/{i}",
                json=_detail_stub(i),
                status=200,
            )
        result = fetch_activities("token", "full", None, None, [])
        assert len(result) == 5

    @responses.activate
    def test_raises_rate_limit_error_with_no_activities_fetched_yet(self):
        responses.add(responses.GET, ACTIVITIES_URL, status=429)
        with pytest.raises(RateLimitError) as exc_info:
            fetch_activities("token", "full", None, None, [])
        assert exc_info.value.partial_activities == []

    @responses.activate
    def test_raises_rate_limit_error_with_partial_activities_on_detail_429(self):
        responses.add(
            responses.GET, ACTIVITIES_URL, json=[_activity_stub(1), _activity_stub(2)], status=200
        )
        responses.add(responses.GET, ACTIVITIES_URL, json=[], status=200)
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/1",
            json=_detail_stub(1),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.strava.com/api/v3/activities/2",
            status=429,
        )
        with pytest.raises(RateLimitError) as exc_info:
            fetch_activities("token", "full", None, None, [])
        assert len(exc_info.value.partial_activities) == 1
        assert exc_info.value.partial_activities[0].id == 1

    @responses.activate
    def test_raises_on_generic_http_error(self):
        responses.add(responses.GET, ACTIVITIES_URL, status=403)
        with pytest.raises(StravaAPIError):
            fetch_activities("token", "full", None, None, [])


class TestFetchActivityDetail:
    """Tests for _fetch_activity_detail()."""

    @responses.activate
    def test_retries_once_on_5xx_and_succeeds(self):
        detail_url = "https://www.strava.com/api/v3/activities/1"
        responses.add(responses.GET, detail_url, status=500)
        responses.add(responses.GET, detail_url, json=_detail_stub(1), status=200)
        result = _fetch_activity_detail(_make_session(), 1)
        assert result["id"] == 1
        assert len(responses.calls) == 2

    @responses.activate
    def test_raises_after_two_consecutive_5xx_failures(self):
        detail_url = "https://www.strava.com/api/v3/activities/1"
        responses.add(responses.GET, detail_url, status=500)
        responses.add(responses.GET, detail_url, status=500)
        with pytest.raises(StravaAPIError):
            _fetch_activity_detail(_make_session(), 1)

    @responses.activate
    def test_raises_rate_limit_error_on_429(self):
        responses.add(responses.GET, "https://www.strava.com/api/v3/activities/1", status=429)
        with pytest.raises(RateLimitError):
            _fetch_activity_detail(_make_session(), 1)

    @responses.activate
    def test_raises_on_generic_http_error(self):
        responses.add(responses.GET, "https://www.strava.com/api/v3/activities/1", status=404)
        with pytest.raises(StravaAPIError):
            _fetch_activity_detail(_make_session(), 1)


class TestHasPersonalRecord:
    """Tests for _has_personal_record()."""

    def test_returns_true_when_one_segment_has_pr_rank_1(self):
        assert _has_personal_record(_detail_stub(segment_efforts=[_segment(pr_rank=1)])) is True

    def test_returns_true_when_multiple_segments_one_has_pr(self):
        efforts = [_segment(pr_rank=None), _segment(pr_rank=1), _segment(pr_rank=3)]
        assert _has_personal_record(_detail_stub(segment_efforts=efforts)) is True

    def test_returns_false_when_no_segment_has_pr_rank_1(self):
        efforts = [_segment(pr_rank=2), _segment(pr_rank=3)]
        assert _has_personal_record(_detail_stub(segment_efforts=efforts)) is False

    def test_returns_false_when_no_segment_efforts(self):
        assert _has_personal_record(_detail_stub(segment_efforts=[])) is False

    def test_returns_false_when_pr_rank_is_not_1(self):
        assert _has_personal_record(_detail_stub(segment_efforts=[_segment(pr_rank=2)])) is False

    def test_returns_true_when_segment_has_leaderboard_achievement(self):
        effort = {"pr_rank": None, "achievements": [{"type_id": 2, "type": "overall", "rank": 5}]}
        assert _has_personal_record({"segment_efforts": [effort]}) is True

    def test_returns_false_when_segment_has_only_pr_achievement_not_rank_1(self):
        effort = {"pr_rank": 2, "achievements": [{"type_id": 3, "type": "pr", "rank": 2}]}
        assert _has_personal_record({"segment_efforts": [effort]}) is False

    def test_returns_false_when_achievements_empty_and_no_pr(self):
        effort = {"pr_rank": None, "achievements": []}
        assert _has_personal_record({"segment_efforts": [effort]}) is False
