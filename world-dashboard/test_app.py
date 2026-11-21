"""Tests that run without internet: the World Bank API is replaced by fake answers."""

import pytest

import app as dashboard
import worldbank

FAKE_COUNTRIES = [
    {"id": "FRA", "name": "France", "region": {"value": "Europe & Central Asia"}},
    {"id": "FIN", "name": "Finland", "region": {"value": "Europe & Central Asia"}},
    {"id": "EUU", "name": "European Union", "region": {"value": "Aggregates"}},
]

FAKE_SERIES = [
    {"country": {"value": "France"}, "date": "2021", "value": 86.1},
    {"country": {"value": "France"}, "date": "2020", "value": 84.8},
    {"country": {"value": "France"}, "date": "2019", "value": None},
    {"country": {"value": "Finland"}, "date": "2021", "value": 92.8},
]


@pytest.fixture(autouse=True)
def fake_api(monkeypatch):
    def fake_get(path, params=None):
        return FAKE_COUNTRIES if path == "country" else FAKE_SERIES

    monkeypatch.setattr(worldbank, "_get", fake_get)
    worldbank.get_countries.cache_clear()
    worldbank.get_series.cache_clear()


def test_countries_skip_aggregates_and_are_sorted():
    names = [c["name"] for c in worldbank.get_countries()]
    assert names == ["Finland", "France"]


def test_series_sorted_by_year_without_missing_values():
    series = worldbank.get_series(("FRA", "FIN"), "IT.NET.USER.ZS")
    assert series["France"] == {"years": [2020, 2021], "values": [84.8, 86.1]}
    assert series["Finland"]["years"] == [2021]


def test_unknown_indicator_is_refused():
    with pytest.raises(ValueError):
        worldbank.get_series(("FRA",), "NOT.A.CODE")


def test_page_shows_chart_and_table():
    client = dashboard.app.test_client()
    page = client.get("/?countries=FRA&countries=FIN&indicator=IT.NET.USER.ZS").get_data(as_text=True)
    assert "Utilisateurs d&#39;Internet" in page
    assert 'id="chart"' in page
    assert "86.1" in page


def test_api_error_is_shown_to_user(monkeypatch):
    def broken(path, params=None):
        raise worldbank.WorldBankError("API World Bank injoignable : test")

    monkeypatch.setattr(worldbank, "_get", broken)
    page = dashboard.app.test_client().get("/").get_data(as_text=True)
    assert "injoignable" in page
