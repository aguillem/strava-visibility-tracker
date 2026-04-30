"""
Unit tests for the config module.
"""


class TestLoadConfig:
    """Tests for load_config()."""

    def test_valid_full_mode(self):
        ...

    def test_valid_partial_mode_with_dates(self):
        ...

    def test_partial_mode_missing_date_from_exits(self):
        ...

    def test_invalid_mode_exits(self):
        ...

    def test_date_from_after_date_to_exits(self):
        ...

    def test_default_mode_is_partial_last_30_days(self):
        ...


class TestParseActivityTypes:
    """Tests for _parse_activity_types()."""

    def test_single_type(self):
        ...

    def test_multiple_types(self):
        ...

    def test_none_returns_empty_list(self):
        ...

    def test_unknown_type_logs_warning(self):
        ...
