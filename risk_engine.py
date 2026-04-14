"""
Intelligent Risk Score Engine (SWIE Module 2)
Flood Risk, Transport Safety, Crop Suitability scores (0–100).
"""

import math


def flood_risk_score(rainfall_mm: float, humidity_pct: float, wind_kmh: float) -> float:
    """
    Flood Risk Score = 0.5 × (rainfall norm) + 0.3 × (humidity norm) + 0.2 × (wind norm).
    Normalize to 0–100 scale.
    """
    r = min(100, (rainfall_mm / 50.0) * 100) if rainfall_mm else 0
    h = humidity_pct  # already 0–100
    w = min(100, (wind_kmh / 80.0) * 100) if wind_kmh else 0
    score = 0.5 * r + 0.3 * h + 0.2 * w
    return round(min(100, max(0, score)), 1)


def transport_safety_score(rainfall_mm: float, wind_kmh: float, visibility_km: float = 10.0) -> float:
    """
    Safety Score = 100 − (Rain risk + Wind risk).
    Higher rain/wind → lower safety.
    """
    rain_risk = min(50, (rainfall_mm / 20.0) * 50) if rainfall_mm else 0
    wind_risk = min(50, (wind_kmh / 60.0) * 50) if wind_kmh else 0
    vis_penalty = 0
    if visibility_km < 1:
        vis_penalty = 20
    elif visibility_km < 5:
        vis_penalty = 10
    score = 100 - rain_risk - wind_risk - vis_penalty
    return round(min(100, max(0, score)), 1)


def crop_suitability_score(temp_c: float, rainfall_mm: float, humidity_pct: float) -> float:
    """
    Crop Suitability = temperature suitability + rain suitability.
    Optimal band: temp 15–30°C, moderate rain, humidity 40–80%.
    """
    temp_opt = 22
    temp_spread = 12
    temp_score = 100 * max(0, 1 - abs(temp_c - temp_opt) / temp_spread)
    rain_opt = 15
    rain_score = 100 * max(0, 1 - abs((rainfall_mm or 0) - rain_opt) / 40)
    humidity_opt = 60
    humidity_score = 100 * max(0, 1 - abs(humidity_pct - humidity_opt) / 50)
    score = (0.4 * temp_score + 0.4 * rain_score + 0.2 * humidity_score)
    return round(min(100, max(0, score)), 1)


def compute_all_risk_scores(temp: float, rainfall: float, wind: float, humidity: float, visibility: float = 10.0):
    return {
        "flood_risk_score": flood_risk_score(rainfall, humidity, wind),
        "transport_safety_score": transport_safety_score(rainfall, wind, visibility),
        "crop_suitability_score": crop_suitability_score(temp, rainfall, humidity),
    }
