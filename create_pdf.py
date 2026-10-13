from pathlib import Path
import csv
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from pypdf import PdfReader

# This script is intended to be saved as create_pdf.py in the project root.
ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "report"
OUTPUT = REPORT / "final_report.pdf"
REPORT.mkdir(parents=True, exist_ok=True)

PAGE_WIDTH, PAGE_HEIGHT = A4

# Keep the current A4 width settings, while reclaiming a little vertical space.
LEFT_MARGIN = 42
RIGHT_MARGIN = 42
TOP_MARGIN = 34
BOTTOM_MARGIN = 34
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=RIGHT_MARGIN,
    leftMargin=LEFT_MARGIN,
    topMargin=TOP_MARGIN,
    bottomMargin=BOTTOM_MARGIN,
    title="Weekly Business Review - Olist E-commerce Marketplace",
    author="Amirdhavarshini M",
    subject="Olist marketplace data quality, metrics, and recommendations",
)

NAVY = colors.HexColor("#183153")
BLUE = colors.HexColor("#2F6690")
PALE_BLUE = colors.HexColor("#EAF1F8")
LIGHT_GREY = colors.HexColor("#F3F5F7")
MID_GREY = colors.HexColor("#667085")
DARK = colors.HexColor("#202938")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="ReportTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=21,
    leading=25,
    alignment=TA_CENTER,
    textColor=NAVY,
    spaceBefore=2,
    spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="ReportSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    alignment=TA_CENTER,
    textColor=MID_GREY,
    spaceAfter=14,
))
styles.add(ParagraphStyle(
    name="Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=17,
    textColor=NAVY,
    spaceBefore=9,
    spaceAfter=8,
    keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="Subsection",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=BLUE,
    spaceBefore=7,
    spaceAfter=5,
    keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="BodyLarge",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13.2,
    textColor=DARK,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="BodyCompact",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=DARK,
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="TableText",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8.4,
    leading=10.5,
    textColor=DARK,
    spaceAfter=0,
))
styles.add(ParagraphStyle(
    name="TableHeader",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=8.4,
    leading=10.5,
    textColor=WHITE,
    spaceAfter=0,
))
styles.add(ParagraphStyle(
    name="ChartCaption",
    parent=styles["BodyText"],
    fontName="Helvetica-Oblique",
    fontSize=8.8,
    leading=11,
    alignment=TA_CENTER,
    textColor=MID_GREY,
    spaceBefore=3,
    spaceAfter=9,
))
styles.add(ParagraphStyle(
    name="Callout",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=14,
    textColor=NAVY,
    backColor=PALE_BLUE,
    borderColor=BLUE,
    borderWidth=0.6,
    borderPadding=8,
    spaceBefore=5,
    spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="MemoBody",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13.3,
    textColor=DARK,
    spaceAfter=8,
))

story = []

def read_csv_rows(filename):
    """Read a CSV result file from the project root."""
    path = ROOT / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing SQL result CSV: {path}"
        )
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def heading(text):
    story.append(Paragraph(text, styles["Section"]))


def subheading(text):
    story.append(Paragraph(text, styles["Subsection"]))


def para(text, compact=False):
    story.append(Paragraph(text, styles["BodyCompact" if compact else "BodyLarge"]))


def make_table(rows, widths, font_size=8.4, padding=7):
    """Create a readable full-width table with wrapped paragraph cells."""
    converted = []
    for row_index, row in enumerate(rows):
        style = styles["TableHeader"] if row_index == 0 else styles["TableText"]
        converted.append([Paragraph(str(cell), style) for cell in row])

    table = Table(
        converted,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#C7D0DB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
    ]))
    return table


def chart(filename, caption, height):
    path = REPORT / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing chart: {path}\nRun create_charts.py before create_pdf.py."
        )

    img = Image(str(path), width=CONTENT_WIDTH, height=height * inch)
    img.hAlign = "CENTER"
    img._restrictSize(CONTENT_WIDTH, height * inch)
    story.append(img)
    story.append(Paragraph(caption, styles["ChartCaption"]))


# ---------------------------------------------------------------------------
# PAGE 1 — Executive summary and methodology
# ---------------------------------------------------------------------------
story.append(Paragraph(
    "Weekly Business Review",
    styles["ReportTitle"],
))
story.append(Paragraph(
    "Olist E-commerce Marketplace | Data Quality, Commercial Performance & Delivery",
    styles["ReportSubtitle"],
))

story.append(Paragraph(
    "99,441 orders&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;"
    "91.89% on-time delivery&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;"
    "4.09 / 5 average review",
    styles["Callout"],
))

heading("1. Executive Summary")
para(
    "The analysis mart contains <b>99,441 rows and 99,441 distinct order IDs</b>. "
    "The on-time delivery rate is <b>91.89%</b>, the late-delivery rate is "
    "<b>8.11%</b>, the average review score is <b>4.09/5</b>, and average "
    "order value is <b>159.33</b> in the dataset's currency, including product "
    "price and freight."
)
para(
    "The North Star metric is <b>on-time delivery rate</b> because it measures "
    "whether delivered orders arrive by the estimated date. Review scores add "
    "a customer-experience measure, while late-delivery rate acts as a direct "
    "operational guardrail."
)

heading("2. Pipeline and Methodology")
para(
    "<b>Raw ingestion:</b> CSV files are loaded into PostgreSQL raw tables. "
    "<b>Staging:</b> relevant fields and data types are prepared. "
    "<b>Analysis mart:</b> item, payment, and review data are aggregated before "
    "joining to orders to reduce the risk of multiplying order-level records. "
    "<b>Analysis:</b> SQL calculates monthly order value, state-level category "
    "rankings, rolling order counts, repeat purchasing, and delivery/review measures."
)
para(
    "The pipeline log records successful execution. The mart contains 99,441 rows "
    "and 99,441 unique orders, so the row count agrees with the distinct order count. "
    "The results describe the supplied Olist dataset and should not be interpreted "
    "as current marketplace performance."
)

subheading("Business question")
para(
    "Where should leadership focus to improve customer satisfaction without losing "
    "sight of order value, repeat purchasing, and data reliability?"
)

story.append(PageBreak())

# ---------------------------------------------------------------------------
# PAGE 2 — Data quality and metric definitions
# ---------------------------------------------------------------------------
heading("3. Data Quality Results")
para(
    "Nine automated checks were executed. Six critical checks returned zero "
    "failures. Three additional checks identified exceptions that were flagged "
    "for investigation rather than silently discarded. In the current pipeline, "
    "these three checks are warnings and do not stop mart creation."
)

dq_data = [
    ["Check", "Failed rows", "Handling / interpretation"],
    ["Missing order IDs", "0", "Passed"],
    ["Duplicate order IDs", "0", "Passed"],
    ["Invalid delivery dates", "0", "Passed"],
    ["Invalid item values", "0", "Passed"],
    ["Missing customer records", "0", "Passed"],
    ["Invalid review scores", "0", "Passed"],
    ["Payment mismatches", "267", "Flag for investigation"],
    ["Orders without items", "775", "Review order status; do not silently delete"],
    ["Orders without payments", "1", "Flag the unmatched delivered order"],
]
story.append(make_table(dq_data, [1.55*inch, 0.82*inch, CONTENT_WIDTH - 2.37*inch], padding=7))
story.append(Spacer(1, 8))

subheading("What the exceptions mean")
para(
    "The 267 payment mismatches are cases where aggregated item-plus-freight "
    "totals differ from payment totals by more than 0.02. The 775 orders without "
    "items are largely associated with unavailable or canceled statuses. One "
    "delivered order has no matching payment record. These exceptions are not, "
    "by themselves, evidence of fraud; investigate source records before changing them."
)
story.append(Paragraph(
    "Control note: the pipeline currently logs these three checks as warnings and "
    "continues. The assignment asks for an error/alarm when a check fails, so strict "
    "fail-fast behavior for these checks remains a follow-up improvement.",
    styles["Callout"],
))

heading("4. Supporting Business Metrics")
metrics = [
    ["Metric", "Result", "Formula / definition"],
    ["North Star: on-time delivery", "91.89%", "Delivered orders on/before estimate ÷ delivered orders with known outcome"],
    ["Late-delivery rate", "8.11%", "Delivered orders after estimate ÷ delivered orders with known outcome"],
    ["Average review score", "4.09 / 5", "Mean available review score"],
    ["Average order value", "159.33", "Mean (item price + freight) per order"],
    ["Repeat purchase rate", "3.12%", "Unique customers with >1 order ÷ all unique customers"],
    ["Repeat-customer order share", "6.38%", "Orders placed by repeat customers ÷ all orders"],
]
story.append(make_table(
    metrics,
    [1.55*inch, 0.92*inch, CONTENT_WIDTH - 2.47*inch],
    padding=7,
))
para(
    "<b>Interpretation:</b> repeat purchase rate is customer-based, whereas "
    "repeat-customer order share is order-based; they use different denominators.",
    compact=True,
)

story.append(PageBreak())

# ---------------------------------------------------------------------------
# PAGE 3 — Commercial charts
# ---------------------------------------------------------------------------
heading("5. Commercial Performance")
para(
    "The charts below summarize revenue/order-value movement and product-category "
    "concentration. Interpret changes alongside order counts, especially at the "
    "end of the dataset period."
)
chart(
    "01_monthly_revenue.png",
    "Figure 1. Monthly order value and month-over-month growth. Sep 2018 (16 orders) "
    "and Oct 2018 (4 orders) are sparse final months in the supplied dataset.",
    2.65,
)
chart(
    "02_top_categories.png",
    "Figure 2. Top product categories by customer state, ranked by revenue.",
    2.65,
)
subheading("How to use these results")
para(
    "Use monthly movement to identify periods that merit follow-up, but avoid "
    "over-interpreting the final sparse months. State-level category rankings can "
    "help identify where demand is concentrated and where assortment, availability, "
    "or seller coverage may deserve closer review."
)

story.append(PageBreak())

# ---------------------------------------------------------------------------
# PAGE 4 — Orders and customer experience
# ---------------------------------------------------------------------------
heading("6. Orders and Customer Experience")
para(
    "Order volume and delivery experience should be monitored together: volume "
    "shows demand patterns, while delivery outcomes and review scores help reveal "
    "potential friction in the customer journey."
)
chart(
    "03_rolling_orders.png",
    "Figure 3. Seven-day rolling average of daily orders, including calendar days "
    "with zero orders.",
    2.65,
)
chart(
    "04_delivery_review.png",
    "Figure 4. Average review score by delivery performance.",
    2.65,
)
story.append(Paragraph(
    "Late deliveries average 2.57/5 in review score, compared with 4.29/5 for "
    "early deliveries. This is an association in the observed data, not proof that "
    "delivery timing alone caused the review difference.",
    styles["Callout"],
))
para(
    "Operational follow-up should compare late-delivery patterns by customer state, "
    "seller, category, and time period. Track whether targeted changes are followed "
    "by improvements in both on-time delivery and review scores."
)

story.append(PageBreak())

# ---------------------------------------------------------------------------
# PAGE 5 — VP memo, actions, definitions
# ---------------------------------------------------------------------------
heading("7. VP Memo: Improving Customer Experience")
para("<b>To:</b> Vice President, Marketplace Operations&nbsp;&nbsp;&nbsp; "
     "<b>Subject:</b> Delivery reliability as a customer-experience priority")

story.append(Paragraph(
    "Key finding",
    styles["Subsection"],
))
para(
    "The dataset shows an overall on-time delivery rate of 91.89%, with 8.11% "
    "of delivered orders arriving late. Late deliveries are associated with a "
    "lower average review score: 2.57/5 for late deliveries versus 4.29/5 for "
    "early deliveries. This gap makes delivery reliability a practical priority "
    "for investigation, while not proving causation."
)

story.append(Paragraph(
    "Recommended action",
    styles["Subsection"],
))
para(
    "Run a focused late-delivery review by customer state, seller, product category, "
    "and purchase period. Identify the segments contributing the largest number "
    "of late orders, validate likely causes with operational teams, and pilot a "
    "targeted corrective action. Compare on-time delivery and review scores before "
    "and after the pilot."
)

story.append(Paragraph(
    "Weekly scorecard",
    styles["Subsection"],
))
scorecard = [
    ["Measure", "Why leadership should monitor it"],
    ["On-time delivery rate (North Star)", "Primary indicator of delivery reliability"],
    ["Late-delivery rate", "Guardrail that highlights failed delivery commitments"],
    ["Average review score", "Customer-experience signal to read alongside delivery"],
    ["Average order value", "Tracks order economics; includes item price and freight"],
    ["Repeat purchase rate", "Tracks the share of customers who return to order"],
]
story.append(make_table(
    scorecard,
    [2.1*inch, CONTENT_WIDTH - 2.1*inch],
    padding=6,
))
heading("Data and decision caveats")
para(
    "Payment mismatches (267), orders without items (775), and orders without "
    "payments (1) remain flagged for investigation. Resolve or document these "
    "exceptions and strengthen the pipeline's warning/failure policy before using "
    "affected records for operational or financial decisions. The Olist data spans "
    "2016–2018; findings are historical and may not reflect current performance."
)
para(
    "<b>Data source:</b> Olist Brazilian E-Commerce Public Dataset. "
    "<b>Tools:</b> Python, PostgreSQL, SQL, pandas, and matplotlib.",
    compact=True,
)


def footer(canvas, doc):
    canvas.saveState()
    # Thin rule and page number use the same horizontal margins as the content.
    canvas.setStrokeColor(colors.HexColor("#D7DEE7"))
    canvas.setLineWidth(0.5)
    canvas.line(LEFT_MARGIN, 27, PAGE_WIDTH - RIGHT_MARGIN, 27)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawString(LEFT_MARGIN, 15, "Weekly Business Review | Olist E-commerce")
    canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, 15, f"Page {doc.page} of 5")
    canvas.restoreState()


doc.build(story, onFirstPage=footer, onLaterPages=footer)

# Guard against accidental overflow or unexpected page breaks.
page_count = len(PdfReader(str(OUTPUT)).pages)
if page_count != 5:
    raise RuntimeError(
        f"PDF generated with {page_count} pages, expected exactly 5. "
        "Adjust chart heights or spacing and rerun."
    )

print(f"PDF created: {OUTPUT}")
print(f"Page count verified: {page_count}")