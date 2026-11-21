# World Dashboard 🌍

Compare countries with live open data from the **World Bank**: GDP per capita, life expectancy, internet access, population, unemployment.

Pick an indicator and up to 6 countries: the app draws an interactive chart (2000 to today) and a table of the latest values.

![Screenshot](screenshot.png)

## Why this project

I studied international studies and I'm now a developer at École 42. This project brings both together: asking real questions about countries, and answering them with code and public data.

## Stack

- **Python** and **Flask** for the web server
- **requests** to call the [World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) (free, no key needed)
- **Plotly.js** for the interactive chart
- **pytest** for tests (the API is mocked, so tests run offline)

## Run it locally

```bash
git clone https://github.com/[pseudo]/world-dashboard.git
cd world-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

## Run the tests

```bash
pytest
```

## Project structure

```
app.py            Flask app: reads the form, calls the API, renders the page
worldbank.py      Small World Bank API client (with caching)
templates/        HTML page
static/           CSS
test_app.py       Tests with a fake API
```

## Ideas for later

- Add more indicators (education, CO₂ emissions…)
- Show a world map
- Export the data as CSV
