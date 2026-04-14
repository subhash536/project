"""
Data Science module for weather and climate analysis.
Uses Open-Meteo APIs and implements trend analysis, forecasting, and visualization.
Integrates SWIE: ML prediction, risk scoring, and AI decision/advice.
"""

import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import json

# SWIE modules
from ml_engine import get_ml_engine
from risk_engine import compute_all_risk_scores
from advice_engine import agriculture_advice, transport_advice, disaster_advice


class WeatherDataProcessor:
    """Process weather data and perform climate change analysis."""

    BASE_URL = "https://api.open-meteo.com/v1"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1"
    CLIMATE_URL = "https://climate-api.open-meteo.com/v1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "ClimateForecastApp/1.0"})

    def _fetch_json(self, url, params):
        """Fetch JSON from API with error handling."""
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_current_forecast(self, lat: float, lon: float):
        """Get current weather and 7-day forecast."""
        url = f"{self.BASE_URL}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,pressure_msl",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "timezone": "auto",
            "forecast_days": 7,
        }
        return self._fetch_json(url, params)

    def get_historical_data(self, lat: float, lon: float, days: int = 365):
        """Get historical weather data for trend analysis."""
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        url = f"{self.ARCHIVE_URL}/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum",
            "timezone": "auto",
        }
        return self._fetch_json(url, params)

    def get_climate_projections(self, lat: float, lon: float):
        """Get climate model projections from IPCC CMIP6 models.
        Fetches from one model and returns yearly averages for charting.
        """
        url = f"{self.CLIMATE_URL}/climate"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "1980-01-01",
            "end_date": "2050-12-31",
            "models": "EC_Earth3P_HR",
            "daily": "temperature_2m_max",
            "timezone": "auto",
        }
        raw = self._fetch_json(url, params)
        daily = raw.get("daily", {})
        if not daily or "time" not in daily:
            return raw

        times = daily["time"]
        temps = daily.get("temperature_2m_max", [])
        if not temps:
            return raw

        # Aggregate by year
        by_year = {}
        for i, t in enumerate(times):
            year = t[:4]
            if year not in by_year:
                by_year[year] = []
            if i < len(temps) and temps[i] is not None:
                by_year[year].append(temps[i])

        years = sorted(by_year.keys())
        yearly_avg = [
            round(sum(by_year[y]) / len(by_year[y]), 1) for y in years
        ]

        return {
            "daily": {
                "time": years,
                "EC_Earth3P_HR": yearly_avg,
            },
        }

    def search_location(self, query: str):
        """Search for location using Open-Meteo Geocoding API."""
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": query, "count": 10, "language": "en", "format": "json"}
        data = self._fetch_json(url, params)
        return data.get("results", [])

    def analyze_trends(self, lat: float, lon: float, days: int = 365):
        """
        Perform data science analysis: trend detection, forecasting, statistics.
        """
        hist = self.get_historical_data(lat, lon, days)
        daily = hist.get("daily", {})
        if not daily or "time" not in daily:
            return {"error": "No historical data available"}

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(daily["time"]),
                "temp_max": daily.get("temperature_2m_max", []),
                "temp_min": daily.get("temperature_2m_min", []),
                "temp_mean": daily.get("temperature_2m_mean", []),
                "precipitation": daily.get("precipitation_sum", []),
            }
        )
        df = df.dropna()

        if len(df) < 30:
            return {"error": "Insufficient data for analysis"}

        # Use mean temp for analysis
        df["temp"] = df["temp_mean"].fillna((df["temp_max"] + df["temp_min"]) / 2)
        df["day_num"] = (df["date"] - df["date"].min()).dt.days

        # Linear trend
        X = df[["day_num"]].values
        y_temp = df["temp"].values
        y_precip = df["precipitation"].values

        lr_temp = LinearRegression().fit(X, y_temp)
        lr_precip = LinearRegression().fit(X, y_precip)

        # Temperature trend (per decade)
        days_per_decade = 3652.5
        temp_trend_per_decade = lr_temp.coef_[0] * days_per_decade
        precip_trend_per_decade = lr_precip.coef_[0] * days_per_decade

        # Polynomial trend for visualization
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        lr_poly = LinearRegression().fit(X_poly, y_temp)
        df["trend"] = lr_poly.predict(X_poly)

        # Simple 30-day forecast (extrapolate)
        last_day = df["day_num"].max()
        future_days = np.arange(last_day + 1, last_day + 31).reshape(-1, 1)
        future_poly = poly.transform(future_days)
        forecast_temp = lr_poly.predict(future_poly)

        last_date = df["date"].max()
        forecast_dates = [
            (last_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(1, 31)
        ]

        # Statistics
        stats = {
            "mean_temp": float(df["temp"].mean()),
            "max_temp": float(df["temp_max"].max()),
            "min_temp": float(df["temp_min"].min()),
            "total_precipitation": float(df["precipitation"].sum()),
            "hot_days_30c": int((df["temp_max"] >= 30).sum()),
            "temp_trend_per_decade_c": round(temp_trend_per_decade, 2),
            "precip_trend_per_decade_mm": round(precip_trend_per_decade, 2),
        }

        return {
            "stats": stats,
            "trend_data": {
                "dates": [d.strftime("%Y-%m-%d") for d in df["date"]],
                "temp_mean": [round(x, 1) for x in df["temp"].tolist()],
                "trend": [round(x, 1) for x in df["trend"].tolist()],
                "precipitation": [round(x, 1) for x in df["precipitation"].tolist()],
            },
            "forecast": {
                "dates": forecast_dates,
                "temp": [round(x, 1) for x in forecast_temp.tolist()],
            },
            "trend_direction": "warming" if temp_trend_per_decade > 0.1 else "cooling" if temp_trend_per_decade < -0.1 else "stable",
        }

    def get_swie_data(self, lat: float, lon: float, is_coastal: bool = True):
        """
        Smart Weather Intelligence Engine: prediction, risk scores, advice, explainable AI, model comparison.
        """
        forecast = self.get_current_forecast(lat, lon)
        current = forecast.get("current", {})
        daily = forecast.get("daily", {})
        today_idx = 0
        daily_today = {}
        if daily and daily.get("time"):
            daily_today = {
                "temperature_2m_max": daily.get("temperature_2m_max", [0])[today_idx] if daily.get("temperature_2m_max") else None,
                "temperature_2m_min": daily.get("temperature_2m_min", [0])[today_idx] if daily.get("temperature_2m_min") else None,
                "precipitation_sum": daily.get("precipitation_sum", [0])[today_idx] if daily.get("precipitation_sum") else 0,
                "weather_code": daily.get("weather_code", [0])[today_idx] if daily.get("weather_code") else 0,
            }
        temp = current.get("temperature_2m", 20)
        rainfall = current.get("precipitation") or daily_today.get("precipitation_sum") or 0
        wind = current.get("wind_speed_10m", 0)
        humidity = current.get("relative_humidity_2m", 50)
        pressure = current.get("pressure_msl", 1013)
        precipitation = current.get("precipitation") or 0
        weather_code = current.get("weather_code") or daily_today.get("weather_code") or 0

        ml = get_ml_engine()
        prediction_result = ml.predict(temp, rainfall, wind, humidity, pressure)
        risk_scores = compute_all_risk_scores(temp, rainfall, wind, humidity)
        crop_score = risk_scores["crop_suitability_score"]
        transport_safety = risk_scores["transport_safety_score"]

        agri = agriculture_advice(temp, rainfall, humidity, crop_score, prediction_result["prediction"])
        trans = transport_advice(wind, rainfall, transport_safety, prediction_result["prediction"])
        disaster = disaster_advice(
            risk_scores["flood_risk_score"],
            rainfall,
            wind,
            pressure,
            temp,
            humidity,
            crop_score,
            precipitation,
            weather_code,
            is_coastal=is_coastal,
        )

        return {
            "current": current,
            "daily_today": daily_today,
            "prediction": prediction_result["prediction"],
            "probability": prediction_result["probability"],
            "probabilities": prediction_result["probabilities"],
            "risk_scores": risk_scores,
            "agriculture_advice": agri,
            "transport_advice": trans,
            "disaster_advice": disaster,
            "feature_importance": ml.get_feature_importance(),
            "model_comparison": ml.get_model_comparison(),
        }
