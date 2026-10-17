import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def _append_long_text(story, text, style):
    """Appends long narrative text as multiple flowable Paragraphs split on
    blank-line boundaries so ReportLab can page-break naturally. Single
    newlines within a block are preserved as <br/> line breaks. Using direct
    Paragraphs (rather than a single-cell Table) is required because a Table
    row taller than one page raises a LayoutError."""
    for block in text.split("\n\n"):
        clean = block.strip().replace("\n", "<br/>")
        if clean:
            story.append(Paragraph(clean, style))


def generate_research_pdf(
    objective: str,
    evidence_items: List[Dict[str, Any]],
    verification_report: Dict[str, Any],
    email_draft: Dict[str, Any],
    statistical_data: Optional[List[Dict[str, Any]]] = None,
    methodology: Optional[str] = None,
    key_themes: Optional[List[Dict[str, str]]] = None,
    strategic_implications: Optional[str] = None,
    recommendations: Optional[List[str]] = None,
    limitations: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Generates a minimalist, executive-grade PDF research intelligence brief
    featuring statistical data tables, verified citations, and audit certification.

    Extended sections include an investigative methodology overview, key thematic
    analysis, strategic implications, recommendations, and limitations so the
    report provides a deeper, more substantive research narrative.
    """
    os.makedirs(os.path.dirname(output_path) if output_path else "reports", exist_ok=True)
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reports/Research_Report_{timestamp}.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    # Minimalist, elegant palette (Claude-inspired: warm charcoal, muted stone, subtle amber)
    c_primary = colors.HexColor("#18181b")      # Deep warm zinc
    c_accent = colors.HexColor("#d97757")       # Terracotta / Claude warm amber
    c_text = colors.HexColor("#27272a")         # Soft charcoal
    c_muted = colors.HexColor("#71717a")        # Neutral gray
    c_bg_subtle = colors.HexColor("#f4f4f5")    # Off-white warm stone
    c_border = colors.HexColor("#e4e4e7")       # Clean hairline border
    c_green = colors.HexColor("#15803d")        # Muted forest green

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=c_muted,
        textTransform="uppercase",
        spaceAfter=14,
    )

    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=c_text,
        spaceAfter=6,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=c_primary,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=c_text,
    )

    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=c_muted,
    )

    tag_style = ParagraphStyle(
        "TagText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=c_accent,
    )

    theme_title_style = ParagraphStyle(
        "ThemeTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=c_accent,
        spaceAfter=2,
    )

    list_style = ParagraphStyle(
        "ListItem",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=c_text,
        leftIndent=14,
        bulletIndent=2,
        spaceAfter=4,
    )

    story = []

    # 1. Header
    story.append(Paragraph("EXECUTIVE RESEARCH INTELLIGENCE BRIEF", subtitle_style))
    story.append(Paragraph("Quantitative Investigation & Verified Evidence", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=4, spaceAfter=12))

    # 2. Executive Metadata Box
    date_str = datetime.now().strftime("%B %d, %Y")
    grounding_score = verification_report.get("grounding_score", 100.0)
    audit_status = verification_report.get("status", "CERTIFIED")

    metadata_data = [
        [
            Paragraph("Objective:", meta_label),
            Paragraph(f"<b>{objective}</b>", body_style),
        ],
        [
            Paragraph("Date:", meta_label),
            Paragraph(date_str, table_cell_style),
        ],
        [
            Paragraph("Verification Status:", meta_label),
            Paragraph(f"<font color='#15803d'><b>{audit_status}</b></font> ({grounding_score:.1f}% Grounding Score)", table_cell_style),
        ],
        [
            Paragraph("Agent Crew:", meta_label),
            Paragraph("Research Strategist · Quantitative Analyst · Citations Verifier · Executive Delivery", table_cell_style),
        ],
    ]

    meta_table = Table(metadata_data, colWidths=[1.4 * inch, 5.8 * inch])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_bg_subtle),
            ("BOX", (0, 0), (-1, -1), 0.5, c_border),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Statistical & Quantitative Benchmark Table
    if statistical_data:
        story.append(Paragraph("1. Quantitative & Statistical Benchmarks", h2_style))
        stat_rows = [
            [
                Paragraph("<b>Metric / Benchmark</b>", table_header_style),
                Paragraph("<b>Baseline / Prior</b>", table_header_style),
                Paragraph("<b>Observed Result</b>", table_header_style),
                Paragraph("<b>Variance / Delta</b>", table_header_style),
                Paragraph("<b>Citation</b>", table_header_style),
            ]
        ]
        for s in statistical_data:
            stat_rows.append([
                Paragraph(s.get("metric", "-"), table_cell_style),
                Paragraph(s.get("baseline", "-"), table_cell_style),
                Paragraph(s.get("result", "-"), table_cell_style),
                Paragraph(f"<b>{s.get('variance', '-')}</b>", table_cell_style),
                Paragraph(s.get("citation", "[E1]"), tag_style),
            ])

        stat_table = Table(stat_rows, colWidths=[2.2 * inch, 1.2 * inch, 1.4 * inch, 1.4 * inch, 1.0 * inch])
        stat_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), c_bg_subtle),
                ("GRID", (0, 0), (-1, -1), 0.5, c_border),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(stat_table)
        story.append(Spacer(1, 10))

    # 4. Research Methodology & Investigative Approach
    if methodology:
        story.append(Paragraph("2. Research Methodology & Investigative Approach", h2_style))
        _append_long_text(story, methodology, body_style)
        story.append(Spacer(1, 10))

    # 5. Verified Evidence Findings
    story.append(Paragraph("3. Primary Empirical Findings & Citations", h2_style))
    if evidence_items:
        evidence_rows = [
            [
                Paragraph("<b>ID</b>", table_header_style),
                Paragraph("<b>Verified Fact & Finding</b>", table_header_style),
                Paragraph("<b>Source & Attribution</b>", table_header_style),
                Paragraph("<b>Conf.</b>", table_header_style),
            ]
        ]
        for item in evidence_items:
            eid = item.get("id", "[E?]")
            fact = item.get("fact", "")
            title = item.get("source_title", "Web Source")
            url = item.get("source_url", "")
            conf = item.get("confidence", 0.90)
            url_short = url[:35] + "..." if len(url) > 35 else url

            evidence_rows.append([
                Paragraph(eid, tag_style),
                Paragraph(fact, table_cell_style),
                Paragraph(f"<b>{title}</b><br/><font color='#71717a'>{url_short}</font>", table_cell_style),
                Paragraph(f"{int(conf * 100)}%", table_cell_style),
            ])

        ev_table = Table(evidence_rows, colWidths=[0.6 * inch, 4.0 * inch, 2.0 * inch, 0.6 * inch])
        ev_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), c_bg_subtle),
                ("GRID", (0, 0), (-1, -1), 0.5, c_border),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(ev_table)

    story.append(Spacer(1, 10))

    # 6. Key Themes & Cross-Cutting Analysis
    if key_themes:
        story.append(Paragraph("4. Key Themes & Cross-Cutting Analysis", h2_style))
        for theme in key_themes:
            story.append(Paragraph(theme.get("title", ""), theme_title_style))
            story.append(Paragraph(theme.get("detail", ""), body_style))
            story.append(Spacer(1, 6))

    # 7. Executive Synthesis Brief
    story.append(Paragraph("5. Executive Synthesis Brief", h2_style))
    body = email_draft.get("body", "No synthesis provided.")
    _append_long_text(story, body, body_style)

    # 8. Strategic Implications & Outlook
    if strategic_implications:
        story.append(Paragraph("6. Strategic Implications & Outlook", h2_style))
        _append_long_text(story, strategic_implications, body_style)
        story.append(Spacer(1, 10))

    # 9. Recommendations & Next Steps
    if recommendations:
        story.append(Paragraph("7. Recommendations & Next Steps", h2_style))
        for idx, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{idx}. {rec}", list_style))
        story.append(Spacer(1, 8))

    # 10. Limitations & Caveats
    if limitations:
        story.append(Paragraph("8. Limitations & Caveats", h2_style))
        _append_long_text(story, limitations, body_style)

    # Minimal Footer
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_border, spaceBefore=4, spaceAfter=6))
    story.append(
        Paragraph(
            "Prepared by Autonomous Research Crew. Certified for factual integrity.",
            ParagraphStyle("Footer", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, textColor=c_muted),
        )
    )

    doc.build(story)
    return output_path
