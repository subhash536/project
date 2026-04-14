# AI-Based Smart Weather Intelligence Platform with Risk Scoring and Decision Support

A Smart Weather Intelligence Engine (SWIE) that combines **weather prediction**, **risk scoring**, and **AI-generated advice** for agriculture, disaster preparedness, and transport. It uses Open-Meteo APIs, machine learning (Decision Tree, SVM, Random Forest, XGBoost), and an interactive dashboard.

## Features

### Module 1 — Smart Weather Prediction Engine
- **ML-based classification:** Rainy, Sunny, Cloudy, Storm
- **Inputs:** Temperature, rainfall, wind, humidity, pressure
- **Output:** Predicted weather with probability (e.g. Rainy 82%)

### Module 2 — Intelligent Risk Score Engine
- **Flood Risk Score** (0–100): rainfall, humidity, wind
- **Transport Safety Score** (0–100): rain and wind risk
- **Crop Suitability Score** (0–100): temperature, rainfall, humidity

### Module 3 — AI Decision Generator
- **Agriculture advice** — Irrigation, fieldwork, crop suitability
- **Transport advice** — Travel safety based on wind and rain
- **Disaster preparedness advice** for:
  - **Floods** — Based on flood risk score and rainfall
  - **Drought** — Based on low rain, humidity, temperature
  - **Cyclones** — Based on wind and pressure
  - **Ice storms** — Based on temperature and precipitation type
  - **Earthquake** — Preparedness (secure furniture, emergency kit, safe spots)
  - **Tsunami** — Coastal evacuation and alert awareness

### Module 4 — Professional Dashboard
- **Live weather** — Temperature, wind, rainfall, humidity, pressure
- **AI predictions** — Predicted weather and probability bar
- **Risk meters** — Visual gauges for Flood, Transport Safety, Crop Suitability
- **Climate trends** — Temperature vs time, rainfall, 30-day forecast
- **Climate projections (1980–2050)** — IPCC CMIP6

### Module 5 — Model Comparison
- **Accuracy, Precision, Recall, F1-Score** for Decision Tree, SVM, Random Forest, XGBoost

### Module 6 — Explainable AI
- **Feature importance** — Why the model predicted (temp, rainfall, wind, humidity, pressure)
- Bar chart of feature weights

### Module 7 — Smart Report & Interactive Map
- **PDF report** — Weather summary, risk scores, agriculture/transport/disaster advice (requires `reportlab`)
- **Interactive map** — Folium map with risk zone overlay (requires `folium`)

## Tech Stack

- **Backend:** Python, Flask
- **ML:** scikit-learn (Decision Tree, SVM, Random Forest), XGBoost
- **APIs:** Open-Meteo (Forecast, Archive, Climate, Geocoding)
- **Frontend:** HTML, CSS, JavaScript, Plotly.js
- **Optional:** reportlab (PDF), folium (map)

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or: source venv/bin/activate   # macOS/Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project Structure

```
weather/
├── app.py                 # Flask app, API routes (current, swie, report, map)
├── data_processor.py      # Open-Meteo + trend analysis + SWIE integration
├── ml_engine.py           # Weather classification (RF, SVM, DT, XGBoost)
├── risk_engine.py         # Flood, Transport, Crop risk scores
├── advice_engine.py       # Agriculture, Transport, Disaster advice
├── report_generator.py    # PDF report (reportlab)
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard |
| `GET /api/current/<lat>/<lon>` | Current weather + 7-day forecast |
| `GET /api/swie/<lat>/<lon>` | Full SWIE: prediction, risk scores, advice, feature importance, model comparison |
| `GET /api/analysis/<lat>/<lon>?days=365` | Trend analysis + 30-day forecast |
| `GET /api/climate/<lat>/<lon>` | Climate projections (1980–2050) |
| `GET /api/report/<lat>/<lon>?name=...` | Download PDF report |
| `GET /api/map/<lat>/<lon>` | Interactive map HTML (iframe) |
| `GET /api/search?q=...` | Location search |

## Data Sources

- [Open-Meteo](https://open-meteo.com) — Forecast, historical archive, climate, geocoding (no API key required)
- IPCC CMIP6 — Long-term climate projections

## License

MIT
