import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

LEVEL_LABELS = {1: "Emerging", 2: "Developing", 3: "Proficient", 4: "Advanced"}
LEVEL_COLORS = {
    1: colors.HexColor("#EF4444"),
    2: colors.HexColor("#F97316"),
    3: colors.HexColor("#3B82F6"),
    4: colors.HexColor("#22C55E"),
}
LEVEL_BAR = {1: "█░░░", 2: "██░░", 3: "███░", 4: "████"}

DOMAIN_LABELS = {
    "number": "Number",
    "algebra": "Algebra",
    "geometry_measurement": "Geometry & Measurement",
    "handling_data": "Handling Data",
    "diversity_matter": "Diversity of Matter",
    "cycles": "Cycles",
    "systems": "Systems",
    "forces_energy": "Forces and Energy",
    "humans_environment": "Humans and the Environment",
}


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=base["Heading1"], fontSize=14, spaceAfter=6)
    section = ParagraphStyle("Section", parent=base["Heading2"], fontSize=11, spaceAfter=4,
                              textColor=colors.HexColor("#1E3A5F"))
    normal = ParagraphStyle("Normal", parent=base["Normal"], fontSize=9, spaceAfter=3)
    small = ParagraphStyle("Small", parent=base["Normal"], fontSize=8, textColor=colors.grey)
    bold = ParagraphStyle("Bold", parent=base["Normal"], fontSize=9, fontName="Helvetica-Bold")
    return {"title": title, "section": section, "normal": normal, "small": small, "bold": bold}


def _domain_table(scores: dict, styles: dict) -> Table:
    header = ["Domain", "Score", "Level", ""]
    rows = [header]
    for domain, ds in scores.items():
        label = DOMAIN_LABELS.get(domain, domain)
        score_pct = f"{int(ds['score'] * 100)}%"
        level_label = LEVEL_LABELS[ds["level"]]
        bar = LEVEL_BAR[ds["level"]]
        rows.append([label, score_pct, level_label, bar])

    col_widths = [6 * cm, 1.8 * cm, 2.8 * cm, 1.8 * cm]
    table = Table(rows, colWidths=col_widths)
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
    for i, row in enumerate(rows[1:], 1):
        level = list(scores.values())[i - 1]["level"]
        bar_color = LEVEL_COLORS[level]
        style.add("TEXTCOLOR", (3, i), (3, i), bar_color)
        style.add("FONTNAME", (3, i), (3, i), "Helvetica-Bold")
    table.setStyle(style)
    return table


def generate_report(result: dict, math_recommendations: dict, science_recommendations: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = _styles()
    story = []

    group_label = result.get("group_label") or ""
    assessment_type = (result.get("assessment_type") or "baseline").title()
    group_map = {"기초": "Foundational", "중간": "Developing", "상위": "Advanced"}
    group_en = group_map.get(group_label, group_label)

    story.append(Paragraph("Learning Level Diagnostic Report", styles["title"]))
    story.append(Paragraph(
        f"<b>Student:</b> {result['student_name']}  &nbsp;&nbsp; "
        f"<b>Date:</b> {result['completed_at'][:10]}  &nbsp;&nbsp; "
        f"<b>Overall Level:</b> {LEVEL_LABELS[result['overall_level']]}",
        styles["normal"]
    ))
    meta_parts = [f"<b>Assessment:</b> {assessment_type}"]
    if group_en:
        meta_parts.append(f"<b>Group:</b> {group_label} ({group_en})")
    story.append(Paragraph("  &nbsp;&nbsp; ".join(meta_parts), styles["normal"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

    story.append(Paragraph("Mathematics", styles["section"]))
    story.append(_domain_table(result["math_scores"], styles))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Science", styles["section"]))
    story.append(_domain_table(result["science_scores"], styles))
    story.append(Spacer(1, 0.4 * cm))

    all_scores = {**result["math_scores"], **result["science_scores"]}
    gaps = [(d, s) for d, s in all_scores.items() if s["level"] <= 2]
    gaps_sorted = sorted(gaps, key=lambda x: x[1]["score"])

    if gaps_sorted:
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=6))
        story.append(Paragraph("Priority Learning Areas", styles["section"]))
        for domain, ds in gaps_sorted:
            label = DOMAIN_LABELS.get(domain, domain)
            story.append(Paragraph(
                f"&#x25CF; <b>{label}</b> — Level {ds['level']}: {LEVEL_LABELS[ds['level']]} "
                f"({int(ds['score'] * 100)}%)",
                styles["normal"]
            ))
        story.append(Spacer(1, 0.3 * cm))

    all_recs = {**math_recommendations, **science_recommendations}
    if all_recs:
        story.append(Paragraph("Recommended Next Activities", styles["section"]))
        for domain, text in all_recs.items():
            label = DOMAIN_LABELS.get(domain, domain)
            story.append(Paragraph(f"<b>{label}:</b>", styles["bold"]))
            story.append(Paragraph(text, styles["normal"]))
            story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        f"Generated by Learning Level Assessment &middot; {result['completed_at'][:10]}",
        styles["small"]
    ))

    doc.build(story)
    return buffer.getvalue()
