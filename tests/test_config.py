"""
Unit tests for the config module.
"""

import logging
from datetime import date, timedelta

import pytest

from config import _parse_activity_types, load_config

_BASE_ENV = {
    "STRAVA_CLIENT_ID": "123",
    "STRAVA_CLIENT_SECRET": "secret",
    "STRAVA_REFRESH_TOKEN": "token",
}


class TestLoadConfig:
    """Tests for load_config()."""

    def _set_base_env(self, monkeypatch):
        for k, v in _BASE_ENV.items():
            monkeypatch.setenv(k, v)
        for key in ("MODE", "DATE_FROM", "DATE_TO", "ACTIVITY_TYPES"):
            monkeypatch.delenv(key, raising=False)

    def test_valid_full_mode(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "full")
        config = load_config()
        assert config.mode == "full"
        assert config.date_from is None
        assert config.date_to is None

    def test_valid_partial_mode_with_dates(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "partial")
        monkeypatch.setenv("DATE_FROM", "2024-01-01")
        monkeypatch.setenv("DATE_TO", "2024-03-31")
        config = load_config()
        assert config.mode == "partial"
        assert config.date_from == date(2024, 1, 1)
        assert config.date_to == date(2024, 3, 31)

    def test_partial_mode_without_date_from_defaults_to_last_30_days(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "partial")
        config = load_config()
        today = date.today()
        assert config.mode == "partial"
        assert config.date_from == today - timedelta(days=30)
        assert config.date_to == today

    def test_invalid_mode_exits(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "weekly")
        with pytest.raises(SystemExit):
            load_config()

    def test_date_from_after_date_to_exits(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "partial")
        monkeypatch.setenv("DATE_FROM", "2024-06-01")
        monkeypatch.setenv("DATE_TO", "2024-01-01")
        with pytest.raises(SystemExit):
            load_config()

    def test_partial_mode_without_date_to_defaults_to_today(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "partial")
        monkeypatch.setenv("DATE_FROM", "2024-01-01")
        config = load_config()
        assert config.date_to == date.today()

    def test_invalid_date_format_exits(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "partial")
        monkeypatch.setenv("DATE_FROM", "not-a-date")
        with pytest.raises(SystemExit):
            load_config()

    def test_invalid_date_to_format_exits(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("MODE", "partial")
        monkeypatch.setenv("DATE_FROM", "2024-01-01")
        monkeypatch.setenv("DATE_TO", "not-a-date")
        with pytest.raises(SystemExit):
            load_config()

    def test_default_mode_is_partial_last_30_days(self, monkeypatch):
        self._set_base_env(monkeypatch)
        config = load_config()
        today = date.today()
        assert config.mode == "partial"
        assert config.date_to == today
        assert config.date_from == today - timedelta(days=30)

    def test_date_from_without_mode_is_respected(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("DATE_FROM", "2024-01-01")
        config = load_config()
        assert config.mode == "partial"
        assert config.date_from == date(2024, 1, 1)

    def test_date_from_and_date_to_without_mode_are_respected(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("DATE_FROM", "2024-01-01")
        monkeypatch.setenv("DATE_TO", "2024-03-31")
        config = load_config()
        assert config.mode == "partial"
        assert config.date_from == date(2024, 1, 1)
        assert config.date_to == date(2024, 3, 31)


class TestParseActivityTypes:
    """Tests for _parse_activity_types()."""

    def test_single_type(self):
        assert _parse_activity_types("Run") == ["Run"]

    def test_multiple_types(self):
        assert _parse_activity_types("Run,TrailRun") == ["Run", "TrailRun"]

    def test_none_returns_empty_list(self):
        assert _parse_activity_types(None) == []

    def test_unknown_type_logs_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            result = _parse_activity_types("Run,UnknownType")
        assert "UnknownType" in caplog.text
        assert "Run" in result
