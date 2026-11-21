"""World dashboard: compare countries with World Bank data.

Run:  python app.py   then open http://127.0.0.1:5000
"""

from flask import Flask, render_template, request

import worldbank

app = Flask(__name__)

DEFAULT_COUNTRIES = ["FRA", "DEU", "FIN", "CAN"]
DEFAULT_INDICATOR = "IT.NET.USER.ZS"
MAX_COUNTRIES = 6


@app.route("/")
def index():
    selected = request.args.getlist("countries") or DEFAULT_COUNTRIES
    selected = selected[:MAX_COUNTRIES]
    indicator = request.args.get("indicator", DEFAULT_INDICATOR)
    if indicator not in worldbank.INDICATORS:
        indicator = DEFAULT_INDICATOR

    error = None
    countries, series = [], {}
    try:
        countries = worldbank.get_countries()
        series = worldbank.get_series(tuple(selected), indicator)
    except worldbank.WorldBankError as err:
        error = str(err)

    return render_template(
        "index.html",
        countries=countries,
        selected=selected,
        indicators=worldbank.INDICATORS,
        indicator=indicator,
        series=series,
        max_countries=MAX_COUNTRIES,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
