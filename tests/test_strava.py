"""
Unit tests for the Strava API client module.
All HTTP calls are mocked — no real network requests are made.
"""


class TestGetAccessToken:
    """Tests for get_access_token()."""

    def test_returns_access_token_on_success(self):
        ...

    def test_exits_on_authentication_failure(self):
        ...


class TestFetchActivities:
    """Tests for fetch_activities()."""

    def test_returns_all_activities_in_full_mode(self):
        ...

    def test_filters_by_date_range_in_partial_mode(self):
        ...

    def test_filters_by_activity_type(self):
        ...

    def test_handles_pagination(self):
        ...

    def test_exits_on_rate_limit(self):
        ...


class TestHasPersonalRecord:
    """Tests for _has_personal_record()."""

    def test_returns_true_when_one_segment_has_pr_rank_1(self):
        ...

    def test_returns_true_when_multiple_segments_one_has_pr(self):
        ...

    def test_returns_false_when_no_segment_has_pr_rank_1(self):
        ...

    def test_returns_false_when_no_segment_efforts(self):
        ...

    def test_returns_false_when_pr_rank_is_not_1(self):
        ...
