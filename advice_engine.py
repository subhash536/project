"""
AI Decision Generator (SWIE Module 3)
Agriculture, Disaster (earthquake, tsunami, drought, floods, cyclones, ice storms), Transport advice.
"""


def _flood_advice(flood_score: float, rainfall: float) -> str:
    if flood_score >= 70:
        return "High flood risk. Avoid low-lying areas. Monitor water levels and official flood alerts. Prepare evacuation kit."
    if flood_score >= 50:
        return "Moderate flood risk. Monitor rainfall levels. Clear drains and avoid unnecessary travel in affected areas."
    if flood_score >= 30:
        return "Elevated flood watch. Stay informed. Avoid crossing flooded roads."
    return "Flood risk low. Normal precautions."


def _drought_advice(rainfall: float, humidity: float, temp: float, crop_score: float) -> str:
    if (rainfall or 0) < 2 and humidity < 40 and temp > 28:
        return "Drought conditions likely. Conserve water. Avoid outdoor burning. Follow local water restrictions. Consider drought-resistant crops."
    if (rainfall or 0) < 5 and crop_score < 50:
        return "Dry spell. Increase irrigation where possible. Mulch to retain soil moisture."
    return "No drought alert. Maintain usual water management."


def _cyclone_advice(wind: float, pressure: float) -> str:
    if (wind or 0) >= 60 or (pressure and pressure < 995):
        return "Cyclone/severe storm risk. Secure outdoor objects. Stay indoors. Follow official cyclone warnings and evacuation orders."
    if (wind or 0) >= 40:
        return "Strong winds possible. Secure loose objects. Limit travel. Monitor cyclone bulletins."
    return "No cyclone threat indicated. Monitor weather updates."


def _ice_storm_advice(temp: float, precipitation: float, weather_code: int) -> str:
    # WMO codes: 71,73,75,77,85,86 = snow; 66,67 = freezing rain
    is_frozen = temp <= 2 and (precipitation or 0) > 0
    is_snow = weather_code in (71, 73, 75, 77, 85, 86, 66, 67) if weather_code else False
    if is_frozen or is_snow:
        if temp <= -2:
            return "Ice storm / freezing rain risk. Avoid travel. Watch for black ice. Protect pipes and outdoor equipment."
        return "Wintry mix or ice possible. Drive with caution. Allow extra time for travel."
    return "No ice storm risk. Normal winter precautions if applicable."


def _earthquake_advice(region_risk: str = "general") -> str:
    # No real-time earthquake prediction from weather; provide preparedness advice.
    return "Earthquake preparedness: Secure heavy furniture and fixtures. Know safe spots (under sturdy furniture, away from windows). Keep emergency kit with water, food, flashlight. Identify evacuation routes and meeting points. Stay informed via local seismic/emergency alerts."


def _tsunami_advice(coastal: bool = True) -> str:
    # Tsunami is triggered by seismic/volcanic events; weather API doesn't provide this.
    if coastal:
        return "Tsunami preparedness: Know evacuation routes to higher ground. If you feel a strong earthquake near the coast, move inland and uphill immediately. Stay tuned to tsunami warning systems (e.g., PTWC). Do not return until authorities declare all-clear."
    return "Tsunami risk is coastal. If you are near the coast, know your evacuation route to high ground and follow official tsunami alerts."


def agriculture_advice(
    temp: float,
    rainfall: float,
    humidity: float,
    crop_score: float,
    prediction: str,
) -> str:
    if "Rainy" in prediction or "Storm" in prediction:
        if (rainfall or 0) > 15:
            return "Heavy rainfall expected. Avoid irrigation today. Postpone spraying. Protect harvested produce from moisture."
        return "Rain likely. Delay irrigation. Plan fieldwork for dry windows."
    if (rainfall or 0) < 2 and humidity < 45:
        return "Dry conditions. Schedule irrigation. Consider mulching to conserve soil moisture."
    if crop_score >= 70:
        return "Conditions suitable for most crops. Proceed with planned operations. Rice and leafy vegetables favorable."
    if crop_score < 40:
        return "Marginal crop conditions. Prefer drought-tolerant or short-duration varieties. Monitor soil moisture."
    return "Moderate suitability. Follow local agronomic recommendations."


def disaster_advice(
    flood_score: float,
    rainfall: float,
    wind: float,
    pressure: float,
    temp: float,
    humidity: float,
    crop_score: float,
    precipitation: float,
    weather_code: int,
    is_coastal: bool = True,
) -> dict:
    """
    Returns advice for: flood, drought, cyclone, ice_storm, earthquake, tsunami.
    """
    return {
        "floods": _flood_advice(flood_score, rainfall or 0),
        "drought": _drought_advice(rainfall or 0, humidity or 0, temp or 20, crop_score or 50),
        "cyclones": _cyclone_advice(wind or 0, pressure),
        "ice_storms": _ice_storm_advice(temp or 0, precipitation or 0, weather_code or 0),
        "earthquake": _earthquake_advice("general"),
        "tsunami": _tsunami_advice(is_coastal),
    }


def transport_advice(wind: float, rainfall: float, transport_safety: float, prediction: str) -> str:
    if transport_safety < 30:
        return "Travel not recommended. Strong winds and/or heavy rain. Delay non-essential trips."
    if (wind or 0) >= 50:
        return "Strong winds detected. Avoid high-profile vehicles and exposed routes. Secure cargo."
    if (rainfall or 0) > 20:
        return "Heavy rain. Reduce speed. Avoid flooded roads. Use headlights."
    if (rainfall or 0) > 5:
        return "Rain expected. Drive with caution. Allow extra stopping distance."
    return "Favorable conditions for travel. Standard precautions."
