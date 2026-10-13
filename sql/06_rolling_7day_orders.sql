
WITH RECURSIVE daily_orders AS (
    SELECT
        purchase_timestamp::date AS order_date,
        COUNT(*) AS order_count
    FROM mart.mart_orders
    WHERE purchase_timestamp IS NOT NULL
    GROUP BY purchase_timestamp::date
),
calendar AS (
    SELECT
        MIN(order_date) AS order_date
    FROM daily_orders

    UNION ALL

    SELECT order_date + 1
    FROM calendar
    WHERE order_date < (
        SELECT MAX(order_date) FROM daily_orders
    )
),
complete_daily_orders AS (
    SELECT
        c.order_date,
        COALESCE(d.order_count, 0) AS order_count
    FROM calendar c
    LEFT JOIN daily_orders d USING (order_date)
),
rolling_average AS (
    SELECT
        order_date,
        order_count,
        AVG(order_count::numeric) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_7day_average
    FROM complete_daily_orders
)
SELECT
    order_date,
    order_count,
    ROUND(rolling_7day_average, 2) AS rolling_7day_average
FROM rolling_average
ORDER BY order_date;
