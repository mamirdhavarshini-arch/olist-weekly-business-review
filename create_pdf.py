
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak
)

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "report"
OUTPUT = REPORT / "final_report.pdf"

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=42,
    leftMargin=42,
    topMargin=38,
    bottomMargin=38
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="ReportTitle", parent=styles["Title"],
    fontSize=19, leading=23, alignment=TA_CENTER,
    textColor=colors.HexColor("#183153"), spaceAfter=12
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading2"],
    fontSize=13, leading=16, textColor=colors.HexColor("#183153"),
    spaceBefore=6, spaceAfter=6
))
styles.add(ParagraphStyle(
    name="SmallText", parent=styles["BodyText"],
    fontSize=8.5, leading=11, spaceAfter=5
))
styles.add(ParagraphStyle(
    name="ChartCaption", parent=styles["BodyText"],
    fontSize=8, leading=10, alignment=TA_CENTER, spaceAfter=5
))

story = []

def heading(text):
    story.append(Paragraph(text, styles["Section"]))

def para(text):
    story.append(Paragraph(text, styles["SmallText"]))

def chart(filename, caption, height=2.35):
    path = REPORT / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing chart: {path}")
    img = Image(str(path))
    img.drawHeight = height * inch
    img.drawWidth = 6.7 * inch
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Paragraph(caption, styles["ChartCaption"]))

# PAGE 1: Executive summary and methodology
story.append(Paragraph(
    "Weekly Business Review<br/>Olist E-commerce Marketplace",
    styles["ReportTitle"]
))
para("<b>Objective:</b> Evaluate delivery reliability, customer experience, "
     "order value, product-category performance, and repeat purchasing using "
     "the Olist Brazilian E-Commerce dataset.")
heading("1. Executive Summary")
para("The analysis mart contains 99,441 rows and 99,441 distinct order IDs. "
     "The on-time delivery rate is 91.89%, the late-delivery rate is 8.11%, "
     "the average review score is 4.09/5, and average order value is 159.33 "
     "in the dataset's currency, including product price and freight.")
para("The North Star metric is on-time delivery rate because it directly "
     "measures whether delivered orders meet the estimated delivery date. "
     "Review scores provide a customer-experience measure alongside it.")
heading("2. Pipeline and Methodology")
para("<b>Raw ingestion:</b> CSV files are loaded into PostgreSQL's raw schema. "
     "<b>Staging:</b> Relevant fields and data types are prepared. "
     "<b>Analysis mart:</b> Item, payment, and review data are aggregated "
     "before joining to orders to avoid multiplying order-level records. "
     "<b>Analysis:</b> SQL calculates monthly value, state-level categories, "
     "rolling order counts, repeat purchasing, and delivery/review measures.")
para("The pipeline log confirms successful execution and verifies that the "
     "mart has 99,441 rows and 99,441 unique orders.")

story.append(PageBreak())

# PAGE 2: Data quality and metrics
heading("3. Data Quality Results")
para("The automated pipeline ran nine checks. Six critical checks returned "
     "zero failures. Three additional checks identified exceptions that were "
     "flagged for investigation rather than silently discarded.")
dq_data = [
    ["Check", "Failed rows", "Handling"],
    ["Missing order IDs", "0", "Passed"],
    ["Duplicate order IDs", "0", "Passed"],
    ["Invalid delivery dates", "0", "Passed"],
    ["Invalid item values", "0", "Passed"],
    ["Missing customer records", "0", "Passed"],
    ["Invalid review scores", "0", "Passed"],
    ["Payment mismatches", "267", "Flag for investigation"],
    ["Orders without items", "775", "Flag; review status"],
    ["Orders without payments", "1", "Flag for investigation"],
]
t = Table(dq_data, colWidths=[2.1*inch, 0.85*inch, 3.05*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183153")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.white, colors.HexColor("#F1F4F8")]),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 7))
para("The 267 payment mismatches indicate differences greater than 0.02 "
     "between aggregated item-plus-freight totals and payment totals. "
     "The 775 orders without items are largely associated with unavailable "
     "or canceled statuses, but all exceptions should be reviewed. One "
     "delivered order has no matching payment record. No exception should "
     "be assumed fraudulent or deleted without investigation.")
heading("4. Supporting Business Metrics")
metrics = [
    ["Metric", "Result", "Definition"],
    ["On-time delivery", "91.89%", "Delivered on/before estimate"],
    ["Late delivery", "8.11%", "Delivered after estimate"],
    ["Average review", "4.09/5", "Mean review score"],
    ["Average order value", "159.33", "Mean item price + freight per order"],
    ["Repeat purchase rate", "3.12%", "Unique customers with >1 order / unique customers"],
    ["Repeat-customer order share", "6.38%", "Orders from repeat customers / all orders"],
]
t2 = Table(metrics, colWidths=[1.55*inch, 1.0*inch, 3.45*inch], repeatRows=1)
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183153")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(t2)

story.append(PageBreak())

# PAGE 3: Commercial charts
heading("5. Commercial Performance")
chart("01_monthly_revenue.png",
      "Figure 1. Monthly order value and month-over-month growth.", 2.55)
chart("02_top_categories.png",
      "Figure 2. Top product categories by state.", 2.55)
para("Interpret monthly movements together with data coverage and order "
     "counts. Category rankings identify where product demand is concentrated "
     "and may help guide state-specific assortment decisions.")

story.append(PageBreak())

# PAGE 4: Operational charts
heading("6. Orders and Customer Experience")
chart("03_rolling_orders.png",
      "Figure 3. Seven-day rolling average of daily orders.", 2.55)
chart("04_delivery_review.png",
      "Figure 4. Review scores grouped by delivery performance.", 2.55)
para("Late delivery is associated with a lower average review score in this "
     "dataset, but this relationship alone does not establish causation. "
     "Delivery and review metrics should be monitored together.")

story.append(PageBreak())

# PAGE 5: Recommendations and definitions
heading("7. Recommendations for the VP")
para("<b>1. Reduce late deliveries.</b> Investigate late-delivery rates by "
     "customer state, seller, product category, and delivery period. Prioritize "
     "the segments contributing most to late orders.")
para("<b>2. Monitor customer experience.</b> Review on-time delivery and "
     "average review scores weekly. Compare changes over time before "
     "concluding that one measure caused the other.")
para("<b>3. Improve retention.</b> Segment customers by order history and "
     "examine repeat purchasing before testing targeted retention initiatives.")
para("<b>4. Resolve data exceptions.</b> Investigate payment mismatches, "
     "orders without items, and the delivered order without a payment record. "
     "Document any corrections and rerun the quality checks.")
heading("Metric Definitions")
para("<b>On-time delivery rate:</b> delivered orders with actual delivery "
     "date on or before estimated delivery date divided by orders with known "
     "delivery outcomes. <b>Late-delivery rate:</b> delivered orders after "
     "the estimate divided by orders with known delivery outcomes.")
para("<b>Average order value:</b> mean of product price plus freight per "
     "order. It is not necessarily accounting revenue. <b>Repeat purchase "
     "rate:</b> unique customers with more than one order divided by all "
     "unique customers. <b>Repeat-customer order share:</b> orders placed by "
     "repeat customers divided by all orders.")
heading("Conclusion")
para("The current results establish a baseline for weekly business reviews. "
     "The pipeline ran successfully and the mart passed its row-uniqueness "
     "verification. Data-quality exceptions and unusual monthly movements "
     "should be investigated before the results are used for operational "
     "or financial decisions.")
para("Dataset: Olist Brazilian E-Commerce dataset. Analysis tools: Python, "
     "PostgreSQL, SQL, pandas, and matplotlib.")

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(42, 20, "Weekly Business Review — Olist E-commerce")
    canvas.drawRightString(A4[0] - 42, 20, f"Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"PDF created: {OUTPUT}")
