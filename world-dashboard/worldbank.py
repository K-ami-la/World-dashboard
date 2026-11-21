"""Small client for the World Bank open data API (no key needed).

Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""

from functools import lru_cache

import requests

API_URL = "https://api.worldbank.org/v2"
TIMEOUT = 15  # seconds

# Indicators shown in the dashboard: World Bank code -> readable label
INDICATORS = {
    "NY.GDP.PCAP.CD": "PIB par habitant (US$ courants)",
    "SP.DYN.LE00.IN": "Espérance de vie à la naissance (années)",
    "IT.NET.USER.ZS": "Utilisateurs d'Internet (% de la population)",
    "SP.POP.TOTL": "Population totale",
    "SL.UEM.TOTL.ZS": "Chômage (% de la population active)",
}


class WorldBankError(Exception):
    """Raised when the API cannot be reached or answers with an error."""


def _get(path, params=None):
    """Call the API and return the data part of the JSON answer."""
    query = {"format": "json", "per_page": 1000}
    query.update(params or {})
    try:
        response = requests.get(f"{API_URL}/{path}", params=query, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as err:
        raise WorldBankError(f"API World Bank injoignable : {err}") from err

    # A normal answer is [metadata, data]; an error is [{"message": [...]}]
    if not isinstance(payload, list) or len(payload) < 2:
        raise WorldBankError(f"Réponse inattendue de l'API : {payload}")
    return payload[1] or []


@lru_cache(maxsize=1)
def get_countries():
    """Return real countries (no regional aggregates), sorted by name.

    Each item is a dict: {"code": "FRA", "name": "France"}.
    """
    countries = [
        {"code": c["id"], "name": c["name"]}
        for c in _get("country", {"per_page": 400})
        if c["region"]["value"] != "Aggregates"
    ]
    return tuple(sorted(countries, key=lambda c: c["name"]))


@lru_cache(maxsize=128)
def get_series(country_codes, indicator, start=2000, end=2024):
    """Return one time series per country for an indicator.

    country_codes: tuple of ISO3 codes, e.g. ("FRA", "FIN").
    Result: {"France": {"years": [...], "values": [...]}, ...}
    Years with no value are skipped.
    """
    if indicator not in INDICATORS:
        raise ValueError(f"Indicateur inconnu : {indicator}")
    if not country_codes:
        return {}

    rows = _get(
        f"country/{';'.join(country_codes)}/indicator/{indicator}",
        {"date": f"{start}:{end}"},
    )

    series = {}
    for row in rows:
        if row["value"] is None:
            continue
        name = row["country"]["value"]
        series.setdefault(name, []).append((int(row["date"]), row["value"]))

    # The API sends the newest year first: sort each series by year
    return {
        name: {
            "years": [year for year, _ in sorted(points)],
            "values": [value for _, value in sorted(points)],
        }
        for name, points in series.items()
    }
