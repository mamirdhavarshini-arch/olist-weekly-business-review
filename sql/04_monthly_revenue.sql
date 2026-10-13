
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', purchase_timestamp)::date AS month,
        SUM(total_order_value) AS revenue
    FROM mart.mart_orders
    WHERE purchase_timestamp IS NOT NULL
    GROUP BY DATE_TRUNC('month', purchase_timestamp)
),
revenue_with_previous AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    month,
    ROUND(revenue::numeric, 2) AS revenue,
    ROUND(previous_month_revenue::numeric, 2) AS previous_month_revenue,
    ROUND(
        100.0 * (revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        2
    ) AS growth_percentage
FROM revenue_with_previous
ORDER BY month;
