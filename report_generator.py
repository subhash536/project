"""
Smart Report Generator (SWIE Module 6)
Generates Weather Intelligence Report (PDF).
"""

import io
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_report_pdf(
    location_name: str,
    weather_prediction: str,
    probability: float,
    flood_risk_score: float,
    transport_safety_score: float,
    crop_suitability_score: float,
    crop_advice: str,
    transport_advice: str,
    disaster_advice: dict,
    trend_direction: str = "stable",
) -> bytes:
    """
    Returns PDF as bytes. If reportlab not installed, returns empty bytes.
    """
    if not HAS_REPORTLAB:
        return b""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name="Title", parent=styles["Heading1"], fontSize=18, spaceAfter=12)
    heading_style = ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=12, spaceAfter=6, spaceBefore=12)

    story = []
    story.append(Paragraph("Weather Intelligence Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>Location:</b> {location_name}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Weather Summary", heading_style))
    story.append(Paragraph(f"Weather: <b>{weather_prediction}</b> ({probability * 100:.0f}% probability)", styles["Normal"]))
    story.append(Paragraph(f"Trend: {trend_direction.capitalize()}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Risk Scores", heading_style))
    data = [
        ["Metric", "Score"],
        ["Flood Risk", f"{flood_risk_score}/100"],
        ["Transport Safety", f"{transport_safety_score}/100"],
        ["Crop Suitability", f"{crop_suitability_score}/100"],
    ]
    t = Table(data, colWidths=[3 * inch, 2 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#161b22")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#21262d")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Agriculture Advice", heading_style))
    story.append(Paragraph(crop_advice.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Transport Advice", heading_style))
    story.append(Paragraph(transport_advice.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Disaster Preparedness Advice", heading_style))
    for disaster_type, advice in (disaster_advice or {}).items():
        story.append(Paragraph(f"<b>{disaster_type.replace('_', ' ').title()}</b>", styles["Normal"]))
        story.append(Paragraph(advice.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
