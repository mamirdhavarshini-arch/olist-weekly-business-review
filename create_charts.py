
from pathlib import Path
import getpass

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "charts"
OUTPUT_DIR.mkdir(exist_ok=True)

password = getpass.getpass("Enter PostgreSQL password: ")

url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password=password,
    host="localhost",
    port=5432,
    database="olist_review",
)

engine = create_engine(url)

try:
    
    # Chart 1: Monthly revenue
    monthly = pd.read_sql("""
        SELECT DATE_TRUNC('month', purchase_timestamp)::date AS month,
               SUM(total_order_value) AS revenue
        FROM mart.mart_orders
        WHERE purchase_timestamp IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """, engine)

    monthly["month"] = pd.to_datetime(monthly["month"])

    plt.figure(figsize=(10, 5))
    plt.plot(monthly["month"], monthly["revenue"], marker="o")
    plt.title("Monthly Order Value (Product Price + Freight)")
    plt.xlabel("Month")
    plt.ylabel("Order Value")
    plt.figtext(
        0.5, 0.01,
        "Note: Sep 2018 (16 orders) and Oct 2018 (4 orders) "
        "are sparse final months in the supplied dataset.",
        ha="center", fontsize=8
    )
    plt.xticks(rotation=45)
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig(OUTPUT_DIR / "01_monthly_revenue.png", dpi=150)
    plt.close()


    # Chart 2: Top product categories by revenue
    categories = pd.read_sql("""
        SELECT COALESCE(
                   t.product_category_name_english,
                   p.product_category_name,
                   'Unknown'
               ) AS category_name,
               SUM(i.price) AS revenue
        FROM staging.order_items i
        JOIN staging.products p ON i.product_id = p.product_id
        LEFT JOIN raw.product_category_name_translation t
          ON p.product_category_name = t.product_category_name
        GROUP BY 1
        ORDER BY revenue DESC
        LIMIT 10
    """, engine)

    categories = categories.sort_values("revenue")
    plt.figure(figsize=(10, 6))
    plt.barh(categories["category_name"], categories["revenue"])
    plt.title("Top 10 Product Categories by Product Revenue")
    plt.xlabel("Product Revenue")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "02_top_categories.png", dpi=150)
    plt.close()

    # Chart 3: Seven-day rolling average of daily orders
    daily = pd.read_sql("""
        SELECT purchase_timestamp::date AS order_date,
               COUNT(*) AS order_count
        FROM mart.mart_orders
        WHERE purchase_timestamp IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """, engine)

    daily["order_date"] = pd.to_datetime(daily["order_date"])
    daily = daily.set_index("order_date").asfreq("D", fill_value=0)
    daily["rolling_average"] = daily["order_count"].rolling(
        window=7, min_periods=1
    ).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(daily.index, daily["rolling_average"])
    plt.title("Seven-Day Rolling Average of Daily Orders")
    plt.xlabel("Date")
    plt.ylabel("Average Daily Orders")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "03_rolling_orders.png", dpi=150)
    plt.close()

    # Chart 4: Delivery delay and review score
    delivery = pd.read_sql("""
        SELECT
            CASE WHEN delivered_on_time THEN 'On time'
                 ELSE 'Late'
            END AS delivery_category,
            AVG(avg_review_score) AS average_review_score
        FROM mart.mart_orders
        WHERE delivered_on_time IS NOT NULL
          AND avg_review_score IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """, engine)

    plt.figure(figsize=(7, 5))
    plt.bar(
        delivery["delivery_category"],
        delivery["average_review_score"]
    )
    plt.title("Average Review Score by Delivery Performance")
    plt.xlabel("Delivery Category")
    plt.ylabel("Average Review Score")
    plt.ylim(0, 5)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "04_delivery_review.png", dpi=150)
    plt.close()

    print("All four charts created in:", OUTPUT_DIR)

finally:
    engine.dispose()
