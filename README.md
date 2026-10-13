# Olist Weekly Business Review

## Project Overview

This project analyzes the Brazilian E-Commerce Public Dataset by Olist to evaluate order value, delivery performance, customer reviews, product categories, and repeat purchasing.

The workflow includes CSV ingestion, raw PostgreSQL tables, cleaned staging tables, an analysis-ready order mart, SQL data-quality checks, business analysis queries, and Python-generated charts.

## Technology Stack

- Python
- PostgreSQL
- pgAdmin 4
- SQLAlchemy
- pandas
- Matplotlib
- SQL (CTEs, window functions, aggregations)

## Project Structure

```text
olist-weekly-review/
├── data/
│   └── Olist CSV files
├── sql/
│   ├── 01_create_staging.sql
│   ├── 02_data_quality_checks.sql
│   ├── 03_create_mart.sql
│   ├── 04_monthly_revenue.sql
│   ├── 05_top_categories_by_state.sql
│   ├── 06_rolling_7day_orders.sql
│   ├── 07_repeat_purchase_rate.sql
│   ├── 08_delivery_delay_vs_review.sql
│   └── 09_business_metrics.sql
├── charts/
│   ├── 01_monthly_revenue.png
│   ├── 02_top_categories.png
│   ├── 03_rolling_orders.png
│   └── 04_delivery_review.png
├── report/
│   └── vp_memo.md
├── pipeline.py
├── test_connection.py
├── create_charts.py
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10 or later
- PostgreSQL
- pgAdmin 4
- Olist CSV dataset downloaded from Kaggle

## Installation

Install the required Python libraries:

```bash
python -m pip install pandas SQLAlchemy psycopg2-binary matplotlib seaborn
```

Create a PostgreSQL database named `olist_review`.

Place the extracted Olist CSV files in the `data/` folder.

## Database Connection

The scripts connect to a local PostgreSQL database using:

- Host: `localhost`
- Port: `5432`
- Database: `olist_review`
- User: `postgres`

The PostgreSQL password is entered when prompted. Do not commit passwords or other credentials to GitHub.

## Running the Project

Run the connection test:

```bash
python test_connection.py
```

Load CSV files into raw tables:

```bash
python pipeline.py
```

Run the SQL files in the `sql/` directory in the intended order using pgAdmin's Query Tool.

Generate the four charts:

```bash
python create_charts.py
```

The charts are saved in the `charts/` directory.

## Business Metrics

The analysis includes:

- On-time delivery rate
- Late delivery rate
- Average customer review score
- Average order value
- Repeat purchase rate
- Repeat-customer order share
- Monthly order value and growth
- Top product categories by customer state
- Seven-day rolling average of daily orders
- Delivery performance compared with review scores

## Current Verified Results

- Orders in the mart: 99,441
- Unique order IDs in the mart: 99,441
- On-time delivery rate: 91.89%
- Late delivery rate: 8.11%
- Average review score: 4.09/5
- Average order value: 159.33
- Repeat purchase rate: 3.12%
- Repeat-customer order share: 6.38%

These figures describe the current execution and should be regenerated if the source data or transformation logic changes.

## Data Quality and Limitations

Nine data-quality checks were evaluated. Six critical checks passed with zero failures. Three warning checks identified payment-total mismatches (267 rows), orders without items (775 rows), and orders without payments (1 row).

The current pipeline logs these three checks as warnings and continues to create the mart. The affected records are flagged for investigation rather than silently deleted or corrected. These warning results remain unresolved and should be reviewed before operational use.

The final mart contains 99,441 rows and 99,441 distinct order IDs. The workflow uses Python for ingestion and chart generation and SQL for staging, data-quality checks, mart creation, and business analysis. Review the logs and query results when rerunning the project.

## Outputs

The project produces raw and staging tables, the `mart.mart_orders` analysis table, SQL query results, four charts, and a VP business-review memo.

## Dataset

Source: [Brazilian E-Commerce Public Dataset by Olist — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)