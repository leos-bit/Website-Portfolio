from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = [
    ROOT / "output" / "pdf" / "Leo_Shaw_Portfolio.pdf",
    ROOT / "assets" / "Leo_Shaw_Portfolio.pdf",
]

SITE = "https://leos-bit.github.io/Website-Portfolio"
EMAIL = "leos@andrew.cmu.edu"
GITHUB = "https://github.com/leos-bit"
LINKEDIN = "https://linkedin.com/in/leoshaw"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="PortfolioTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#1c1c1c"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PortfolioSubhead",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#4f4f4f"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeader",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#0a7b6c"),
            spaceAfter=8,
            spaceBefore=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CardTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1c1c1c"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1c1c1c"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4f4f4f"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CenterNote",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4f4f4f"),
        )
    )
    return styles


def link(label: str, url: str) -> str:
    return f'<link href="{url}" color="#1c66d6"><u>{label}</u></link>'


def card_table(title, meta, summary, url, styles):
    rows = [
        [Paragraph(title, styles["CardTitle"])],
        [Paragraph(meta, styles["Meta"])],
        [Paragraph(summary, styles["BodySmall"])],
        [Paragraph(link("Open project page", url), styles["BodySmall"])],
    ]
    table = Table(rows, colWidths=[6.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#e7e2da")),
                ("INNERPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#e7e2da"))
    canvas.line(doc.leftMargin, 0.6 * inch, letter[0] - doc.rightMargin, 0.6 * inch)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#4f4f4f"))
    canvas.drawString(doc.leftMargin, 0.38 * inch, "Leo Shaw Portfolio")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_story():
    styles = build_styles()
    story = []

    story.append(Paragraph("Leo Shaw", styles["PortfolioTitle"]))
    story.append(
        Paragraph(
            "Artificial intelligence and mechanical engineering for real-world autonomy, manufacturing systems, and grounded technical reasoning.",
            styles["PortfolioSubhead"],
        )
    )
    story.append(
        Paragraph(
            "Downloadable portfolio companion to the live site. All section links below remain clickable in the PDF.",
            styles["BodySmall"],
        )
    )

    contact_rows = [
        [
            Paragraph("<b>Email</b>", styles["BodySmall"]),
            Paragraph(link(EMAIL, f"mailto:{EMAIL}"), styles["BodySmall"]),
            Paragraph("<b>Portfolio</b>", styles["BodySmall"]),
            Paragraph(link("Website", SITE), styles["BodySmall"]),
        ],
        [
            Paragraph("<b>GitHub</b>", styles["BodySmall"]),
            Paragraph(link("leos-bit", GITHUB), styles["BodySmall"]),
            Paragraph("<b>LinkedIn</b>", styles["BodySmall"]),
            Paragraph(link("linkedin.com/in/leoshaw", LINKEDIN), styles["BodySmall"]),
        ],
    ]
    contact_table = Table(contact_rows, colWidths=[1.0 * inch, 2.3 * inch, 1.0 * inch, 2.3 * inch])
    contact_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f5ef")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#e7e2da")),
                ("INNERPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.extend([Spacer(1, 0.08 * inch), contact_table, Spacer(1, 0.22 * inch)])

    story.append(Paragraph("Overview", styles["SectionHeader"]))
    story.append(
        Paragraph(
            "I build systems that sense, decide, and act in physical environments. My work spans semiconductor equipment, robotic sorting cells, reinforcement learning planners, document intelligence pipelines, and grounded RAG systems for manufacturing knowledge.",
            styles["BodySmall"],
        )
    )
    story.append(
        Paragraph(
            f"Live navigation: {link('Projects & Experience', SITE + '/projects.html')} | {link('Resume', SITE + '/resume.html')} | {link('About', SITE + '/index.html')}",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("Selected Research And Projects", styles["SectionHeader"]))
    project_cards = [
        (
            "NEXA: Small Language Models for Manufacturing Process Design",
            "Research | 2026 - Present",
            "A grounded manufacturing AI stack combining Nemotron OCR ingestion, handwritten log reconstruction, Q/A/context generation, diagnostic RAG, and OpenWebUI integration.",
            SITE + "/nexa-research.html",
        ),
        (
            "Autonomous Driving Local Planner with Reinforcement Learning",
            "January 2026 - May 2026",
            "A CARLA planning framework for merges, left turns, and cut-ins that compares classical planning against PPO-based local trajectory generation under a fixed PID control stack.",
            SITE + "/autonomous-driving-planner.html",
        ),
        (
            "Real-Time Conveyor-Belt Object Detection and Robotic Sorting",
            "January 2026 - May 2026",
            "A final integrated sorting system using computer vision, homography calibration, and a vacuum-equipped delta robot to remove aluminum cans from a moving conveyor.",
            SITE + "/conveyor-sorting.html",
        ),
        (
            "Autonomous Drone Pathing with Reinforcement Learning",
            "Spring 2026",
            "A MuJoCo quadrotor navigation project comparing PPO, SAC, and model-based RL, including goal-hover shaping and wind-robustness experiments.",
            SITE + "/drone-pathing-rl.html",
        ),
        (
            "Seeing Through Occlusion",
            "January 2026 - May 2026",
            "A video instance segmentation project on OVIS that models object motion through occlusion with multimodal LSTMs, temporal attention, and an occlusion-aware memory bank.",
            SITE + "/seeing-through-occlusion.html",
        ),
    ]
    for item in project_cards[:3]:
        story.append(card_table(*item, styles))
        story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("More Project Work", styles["SectionHeader"]))
    for item in project_cards[3:]:
        story.append(card_table(*item, styles))
        story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("Experience Highlights", styles["SectionHeader"]))
    exp_items = [
        "<b>Ulvac Technologies - Field Service Engineer I</b> | Santa Clara, CA | Oct 2024 - Aug 2025<br/>Rebuilt and upgraded semiconductor tools across six high-volume fabs, executed 30+ retrofit projects across vacuum, RF, PLC, HMI, and motion subsystems, and improved uptime, process stability, and fault-diagnosis speed.",
        "<b>Carnegie Mellon University - Graduate Research Assistant</b> | Pittsburgh, PA | 2026 - Present<br/>Developing manufacturing-focused small language model workflows, document pipelines, and grounded reasoning systems that convert process documentation into retrieval-ready technical knowledge.",
        "<b>Paltorc - Mechanical Engineering Intern</b> | Milpitas, CA | May 2022 - Aug 2022<br/>Integrated an e-bike control module with rider-facing software and improved telemetry, diagnostics, and overall system reliability.",
    ]
    exp_list = ListFlowable(
        [ListItem(Paragraph(item, styles["BodySmall"])) for item in exp_items],
        bulletType="bullet",
        start="circle",
        leftIndent=16,
    )
    story.append(exp_list)
    story.append(Spacer(1, 0.14 * inch))

    story.append(Paragraph("Quick Links", styles["SectionHeader"]))
    quick_links = [
        Paragraph(link("Full Projects & Experience index", SITE + "/projects.html"), styles["BodySmall"]),
        Paragraph(link("Current resume PDF", SITE + "/assets/Leo_Shaw_Resume.pdf"), styles["BodySmall"]),
        Paragraph(link("NEXA research page", SITE + "/nexa-research.html"), styles["BodySmall"]),
        Paragraph(link("GitHub profile", GITHUB), styles["BodySmall"]),
    ]
    for item in quick_links:
        story.append(item)

    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "This PDF is meant to travel easily in applications and outreach while preserving direct access to the live portfolio pages.",
            styles["CenterNote"],
        )
    )
    return story


def main():
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(path),
            pagesize=letter,
            leftMargin=0.72 * inch,
            rightMargin=0.72 * inch,
            topMargin=0.72 * inch,
            bottomMargin=0.82 * inch,
            title="Leo Shaw Portfolio",
            author="Leo Shaw",
        )
        doc.build(build_story(), onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
