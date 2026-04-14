"""
AI-Based Smart Weather Intelligence Platform - Flask Application
SWIE: prediction, risk scoring, decision support, report, map.
"""

import os
from flask import Flask, render_template, jsonify, request, Response
from data_processor import WeatherDataProcessor
from report_generator import generate_report_pdf, HAS_REPORTLAB

app = Flask(__name__)
processor = WeatherDataProcessor()


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")


@app.route("/api/current/<lat>/<lon>")
def current_weather(lat, lon):
    """Get current weather and 7-day forecast."""
    try:
        data = processor.get_current_forecast(float(lat), float(lon))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/historical/<lat>/<lon>")
def historical_weather(lat, lon):
    """Get historical weather data for trend analysis."""
    try:
        days = request.args.get("days", 365, type=int)
        days = min(max(days, 30), 365 * 5)  # 30 days to 5 years
        data = processor.get_historical_data(float(lat), float(lon), days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/climate/<lat>/<lon>")
def climate_data(lat, lon):
    """Get climate model projections (1950-2050)."""
    try:
        data = processor.get_climate_projections(float(lat), float(lon))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analysis/<lat>/<lon>")
def trend_analysis(lat, lon):
    """Get data science trend analysis and forecasts."""
    try:
        days = request.args.get("days", 365, type=int)
        days = min(max(days, 90), 365 * 5)
        data = processor.analyze_trends(float(lat), float(lon), days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search")
def search_location():
    """Search for location coordinates (simple geocoding via Open-Meteo)."""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"results": []})
    try:
        results = processor.search_location(query)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"results": [], "error": str(e)})


@app.route("/api/swie/<lat>/<lon>")
def swie_data(lat, lon):
    """Smart Weather Intelligence Engine: prediction, risk scores, advice, explainable AI, model comparison."""
    try:
        is_coastal = request.args.get("coastal", "true").lower() == "true"
        data = processor.get_swie_data(float(lat), float(lon), is_coastal=is_coastal)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/report/<lat>/<lon>")
def report_pdf(lat, lon):
    """Generate Weather Intelligence Report (PDF)."""
    try:
        name = request.args.get("name", f"{lat}, {lon}")
        swie = processor.get_swie_data(float(lat), float(lon))
        analysis = processor.analyze_trends(float(lat), float(lon), 365)
        trend_direction = analysis.get("trend_direction", "stable") if "error" not in analysis else "stable"

        pdf_bytes = generate_report_pdf(
            location_name=name,
            weather_prediction=swie["prediction"],
            probability=swie["probability"],
            flood_risk_score=swie["risk_scores"]["flood_risk_score"],
            transport_safety_score=swie["risk_scores"]["transport_safety_score"],
            crop_suitability_score=swie["risk_scores"]["crop_suitability_score"],
            crop_advice=swie["agriculture_advice"],
            transport_advice=swie["transport_advice"],
            disaster_advice=swie["disaster_advice"],
            trend_direction=trend_direction,
        )
        if not pdf_bytes:
            return jsonify({"error": "PDF generation not available. Install reportlab."}), 501
        return Response(pdf_bytes, mimetype="application/pdf", headers={"Content-Disposition": "attachment; filename=weather_intelligence_report.pdf"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _get_map_html(lat: float, lon: float):
    """Generate interactive map HTML (Folium) with weather/risk zones."""
    try:
        import folium
        from folium import Circle
    except ImportError:
        return "<p>Map unavailable. Install folium: pip install folium</p>"
    swie = processor.get_swie_data(lat, lon)
    flood = swie["risk_scores"]["flood_risk_score"]
    transport = swie["risk_scores"]["transport_safety_score"]
    crop = swie["risk_scores"]["crop_suitability_score"]
    m = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")
    folium.Marker([lat, lon], popup=f"Flood: {flood}/100 | Transport: {transport}/100 | Crop: {crop}/100", tooltip="Current location").add_to(m)
    # Risk zone overlay: red = high flood risk, green = safe
    color = "red" if flood >= 60 else "orange" if flood >= 40 else "green"
    Circle(location=[lat, lon], radius=5000, color=color, fill=True, fill_opacity=0.3, popup=f"Flood Risk: {flood}/100").add_to(m)
    return m._repr_html_()


@app.route("/api/map/<lat>/<lon>")
def map_view(lat, lon):
    """Interactive map (Folium) with weather/risk zones. Returns HTML snippet for iframe."""
    try:
        html = _get_map_html(float(lat), float(lon))
        return Response(html, mimetype="text/html")
    except Exception as e:
        return f"<p>Map error: {e}</p>", 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
