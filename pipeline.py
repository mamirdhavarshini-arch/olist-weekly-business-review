
from pathlib import Path
import getpass
import logging
import re

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# --------------------------------------------------
# Project configuration
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"

DATABASE = "olist_review"

REQUIRED_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
]

# These checks must return zero for the pipeline to continue.
# Every quality check must pass before mart creation.
CRITICAL_CHECKS = {
    "1. Missing order IDs",
    "2. Duplicate order IDs",
    "3. Invalid delivery dates",
    "4. Invalid order items",
    "5. Missing customers",
    "6. Invalid review scores",
    "7. Payment mismatches",
    "8. Orders without items",
    "9. Orders without payments",
}

WARNING_CHECKS = set()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            BASE_DIR / "pipeline.log",
            encoding="utf-8",
        ),
    ],
)


def read_sql_file(filename):
    """Read a SQL script and fail if it is missing or empty."""
    path = SQL_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(f"SQL file not found: {path}")

    sql = path.read_text(encoding="utf-8").strip()

    if not sql:
        raise ValueError(f"SQL file is empty: {path}")

    return sql


def execute_sql_script(connection, filename):
    """
    Execute a SQL file containing separate statements.
    This project uses semicolon-separated SQL statements.
    """
    sql = read_sql_file(filename)

    # The current project SQL files do not require semicolons
    # inside string literals or procedural blocks.
    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    logging.info("Running %s", filename)

    for statement in statements:
        connection.exec_driver_sql(statement)

    logging.info("Completed %s", filename)


def validate_csv_files():
    """Check required CSV files and required columns."""
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f"Data folder not found: {DATA_DIR}")

    missing = [
        filename
        for filename in REQUIRED_FILES
        if not (DATA_DIR / filename).is_file()
    ]

    if missing:
        raise FileNotFoundError(
            "Required CSV files are missing:\n"
            + "\n".join(missing)
        )

    required_columns = {
        "olist_orders_dataset.csv": {
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        },
        "olist_order_items_dataset.csv": {
            "order_id",
            "product_id",
            "price",
            "freight_value",
        },
        "olist_order_payments_dataset.csv": {
            "order_id",
            "payment_value",
        },
        "olist_order_reviews_dataset.csv": {
            "review_score",
        },
        "olist_customers_dataset.csv": {
            "customer_id",
            "customer_unique_id",
            "customer_state",
        },
        "olist_products_dataset.csv": {
            "product_id",
            "product_category_name",
        },
    }

    for filename, expected in required_columns.items():
        header = pd.read_csv(
            DATA_DIR / filename,
            nrows=0,
        )

        actual = {
            str(column).strip().lower()
            for column in header.columns
        }

        missing_columns = expected - actual

        if missing_columns:
            raise ValueError(
                f"{filename} is missing required columns: "
                f"{sorted(missing_columns)}"
            )

    logging.info("Required files and columns validated.")


def load_raw_tables(engine):
    """Load all CSV files into the raw schema."""
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No CSV files found in the data folder.")

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE SCHEMA IF NOT EXISTS raw"
        )

    for csv_file in csv_files:
        table_name = re.sub(
            r"[^a-zA-Z0-9_]",
            "_",
            csv_file.stem.lower(),
        )

        logging.info("Loading %s", csv_file.name)

        df = pd.read_csv(csv_file)

        df.columns = [
            str(column).strip().lower()
            for column in df.columns
        ]

        if df.columns.duplicated().any():
            raise ValueError(
                f"Duplicate column names found in {csv_file.name}"
            )

        if df.empty:
            logging.warning(
                "%s contains no data rows",
                csv_file.name,
            )

        df.to_sql(
            name=table_name,
            con=engine,
            schema="raw",
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi",
        )

        logging.info(
            "Loaded %s rows into raw.%s",
            len(df),
            table_name,
        )



def run_quality_checks(connection):
    """Run all quality checks and stop for any failures."""
    sql = read_sql_file("02_data_quality_checks.sql")

    results = pd.read_sql_query(text(sql), connection)

    required_columns = {"check_name", "failed_rows"}
    if not required_columns.issubset(results.columns):
        raise ValueError(
            "Quality-check SQL must return check_name and failed_rows."
        )

    results["failed_rows"] = pd.to_numeric(
        results["failed_rows"], errors="raise"
    )

    # Save results even if a check fails.
    results.to_csv(
        BASE_DIR / "data_quality_results.csv",
        index=False,
    )

    expected_checks = CRITICAL_CHECKS
    actual_checks = set(results["check_name"])

    unknown_checks = actual_checks - expected_checks
    missing_checks = expected_checks - actual_checks

    if unknown_checks:
        raise ValueError(
            f"Unrecognized quality checks: {sorted(unknown_checks)}"
        )

    if missing_checks:
        raise ValueError(
            f"Expected quality checks are missing: {sorted(missing_checks)}"
        )

    logging.info("Data-quality results:")
    for _, row in results.iterrows():
        logging.info(
            "%s: %s failed rows",
            row["check_name"],
            int(row["failed_rows"]),
        )

    failures = results[results["failed_rows"] > 0]

    if not failures.empty:
        details = "\n".join(
            f"{row['check_name']}: {int(row['failed_rows'])} failed rows"
            for _, row in failures.iterrows()
        )

        logging.error("Data-quality checks failed:\n%s", details)
        raise RuntimeError(
            "Pipeline stopped: one or more data-quality checks failed."
        )

    logging.info("All nine data-quality checks passed.")



def main():
    engine = None

    try:
        validate_csv_files()

        password = getpass.getpass(
            "Enter PostgreSQL password: "
        )

        url = URL.create(
            drivername="postgresql+psycopg2",
            username="postgres",
            password=password,
            host="localhost",
            port=5432,
            database=DATABASE,
        )

        engine = create_engine(url)

        # Confirm that PostgreSQL is reachable.
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logging.info("PostgreSQL connection successful.")

        # Stage 1: Load the raw CSV files.
        load_raw_tables(engine)

        # Stage 2: Create staging tables.
        with engine.begin() as connection:
            execute_sql_script(
                connection,
                "01_create_staging.sql",
            )

        # Stage 3: Run quality checks before mart creation.
        with engine.connect() as connection:
            run_quality_checks(connection)

        # Stage 4: Create the mart only after critical checks pass.
        with engine.begin() as connection:
            execute_sql_script(
                connection,
                "03_create_mart.sql",
            )

        # Stage 5: Verify one row per order.
        with engine.connect() as connection:
            counts = connection.execute(
                text("""
                    SELECT
                        COUNT(*) AS total_rows,
                        COUNT(DISTINCT order_id) AS unique_orders
                    FROM mart.mart_orders
                """)
            ).mappings().one()

            total_rows = counts["total_rows"]
            unique_orders = counts["unique_orders"]

            logging.info(
                "Mart verification: rows=%s, unique orders=%s",
                total_rows,
                unique_orders,
            )

            if total_rows != unique_orders:
                raise RuntimeError(
                    "Mart validation failed: duplicate order IDs exist."
                )

        logging.info("PIPELINE COMPLETED SUCCESSFULLY.")

    except Exception:
        logging.exception("PIPELINE FAILED.")
        raise

    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    main()