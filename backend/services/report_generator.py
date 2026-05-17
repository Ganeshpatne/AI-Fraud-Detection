"""
PDF fraud investigation report generator using ReportLab.
"""
import logging
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from backend.config import REPORTS_DIR

logger = logging.getLogger("fraud_detection.reports")


class FraudReportGenerator:
    """Generate professional PDF fraud investigation reports."""

    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        transaction_id: str,
        user_id: str,
        amount: float,
        risk_score: float,
        confidence: float,
        fraud_type: str,
        reason: str,
        explanation: str,
        risk_factors: dict,
        timestamp: datetime,
    ) -> str:
        """Generate a PDF report and return the file path."""
        filename = f"fraud_report_{transaction_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.reports_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=25 * mm,
            leftMargin=25 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=24,
            textColor=colors.HexColor("#0077b6"),
            spaceAfter=6,
            alignment=TA_CENTER,
        )

        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#666666"),
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#00b4d8"),
            spaceBefore=16,
            spaceAfter=8,
            borderWidth=0,
        )

        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#333333"),
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14,
        )

        label_style = ParagraphStyle(
            "LabelStyle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#555555"),
            fontName="Helvetica-Bold",
        )

        value_style = ParagraphStyle(
            "ValueStyle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#222222"),
        )

        elements = []

        # ── Header ──────────────────
        elements.append(Paragraph("🛡️ FRAUD INVESTIGATION REPORT", title_style))
        elements.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                subtitle_style,
            )
        )
        elements.append(
            HRFlowable(
                width="100%", thickness=2, color=colors.HexColor("#00b4d8"),
                spaceBefore=4, spaceAfter=16
            )
        )

        # ── Classification Badge ────
        severity_color = colors.HexColor("#dc3545") if risk_score >= 70 else (
            colors.HexColor("#fd7e14") if risk_score >= 40 else colors.HexColor("#28a745")
        )
        severity_label = "HIGH RISK" if risk_score >= 70 else (
            "MEDIUM RISK" if risk_score >= 40 else "LOW RISK"
        )

        badge_data = [[Paragraph(f"<b>{severity_label}</b>", ParagraphStyle(
            "Badge", parent=styles["Normal"], fontSize=12,
            textColor=colors.white, alignment=TA_CENTER
        ))]]
        badge_table = Table(badge_data, colWidths=[120])
        badge_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), severity_color),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        elements.append(badge_table)
        elements.append(Spacer(1, 16))

        # ── Transaction Details ─────
        elements.append(Paragraph("Transaction Details", section_style))

        details_data = [
            [Paragraph("<b>Field</b>", label_style), Paragraph("<b>Value</b>", label_style)],
            [Paragraph("Transaction ID", body_style), Paragraph(str(transaction_id), value_style)],
            [Paragraph("User ID", body_style), Paragraph(str(user_id), value_style)],
            [Paragraph("Amount", body_style), Paragraph(f"${amount:,.2f}", value_style)],
            [Paragraph("Timestamp", body_style), Paragraph(timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), value_style)],
            [Paragraph("Risk Score", body_style), Paragraph(f"{risk_score}/100", value_style)],
            [Paragraph("Confidence Score", body_style), Paragraph(f"{confidence:.2%}", value_style)],
            [Paragraph("Fraud Classification", body_style), Paragraph(str(fraud_type or "N/A"), value_style)],
        ]

        details_table = Table(details_data, colWidths=[160, 340])
        details_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f8ff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0077b6")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 16))

        # ── Risk Factor Breakdown ───
        elements.append(Paragraph("Risk Factor Breakdown", section_style))

        factor_data = [
            [
                Paragraph("<b>Factor</b>", label_style),
                Paragraph("<b>Score</b>", label_style),
                Paragraph("<b>Max</b>", label_style),
            ],
            [Paragraph("Amount Risk", body_style), Paragraph(str(risk_factors.get("amount_factor", 0)), value_style), Paragraph("35", value_style)],
            [Paragraph("Location Mismatch", body_style), Paragraph(str(risk_factors.get("location_factor", 0)), value_style), Paragraph("25", value_style)],
            [Paragraph("Device Mismatch", body_style), Paragraph(str(risk_factors.get("device_factor", 0)), value_style), Paragraph("20", value_style)],
            [Paragraph("Frequency Spike", body_style), Paragraph(str(risk_factors.get("frequency_factor", 0)), value_style), Paragraph("20", value_style)],
        ]

        factor_table = Table(factor_data, colWidths=[200, 150, 150])
        factor_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f4fd")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0077b6")),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(factor_table)
        elements.append(Spacer(1, 16))

        # ── Detection Reason ────────
        elements.append(Paragraph("Detection Reason", section_style))
        elements.append(Paragraph(reason, body_style))
        elements.append(Spacer(1, 12))

        # ── AI Explanation ──────────
        elements.append(Paragraph("AI-Powered Fraud Explanation", section_style))
        # Split explanation into paragraphs for better formatting
        for para in explanation.split("\n"):
            if para.strip():
                elements.append(Paragraph(para.strip(), body_style))
        elements.append(Spacer(1, 16))

        # ── Footer ──────────────────
        elements.append(
            HRFlowable(
                width="100%", thickness=1, color=colors.HexColor("#cccccc"),
                spaceBefore=20, spaceAfter=8
            )
        )
        footer_style = ParagraphStyle(
            "Footer", parent=styles["Normal"], fontSize=8,
            textColor=colors.HexColor("#999999"), alignment=TA_CENTER
        )
        elements.append(
            Paragraph(
                "This report was automatically generated by the AI Fraud Detection System. "
                "Confidential – For authorized personnel only.",
                footer_style,
            )
        )
        elements.append(
            Paragraph(
                f"Report ID: {transaction_id[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')} | "
                "Powered by NVIDIA AI",
                footer_style,
            )
        )

        # Build PDF
        doc.build(elements)
        logger.info("Fraud report generated: %s", filepath)
        return str(filepath)


# Singleton
report_generator = FraudReportGenerator()
