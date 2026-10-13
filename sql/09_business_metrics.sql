
SELECT
    COUNT(*) AS total_orders,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delivered_on_time = TRUE
        ) / NULLIF(
            COUNT(*) FILTER (
                WHERE delivered_on_time IS NOT NULL
            ), 0
        ),
        2
    ) AS on_time_delivery_rate_pct,

    ROUND(AVG(avg_review_score)::numeric, 2)
        AS average_review_score,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delivered_on_time = FALSE
        ) / NULLIF(
            COUNT(*) FILTER (
                WHERE delivered_on_time IS NOT NULL
            ), 0
        ),
        2
    ) AS late_delivery_rate_pct,

    ROUND(AVG(total_order_value)::numeric, 2)
        AS average_order_value,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE customer_unique_id IS NOT NULL
              AND customer_unique_id IN (
                  SELECT customer_unique_id
                  FROM mart.mart_orders
                  WHERE customer_unique_id IS NOT NULL
                  GROUP BY customer_unique_id
                  HAVING COUNT(DISTINCT order_id) > 1
              )
        ) / NULLIF(
            COUNT(*) FILTER (
                WHERE customer_unique_id IS NOT NULL
            ), 0
        ),
        2
    ) AS repeat_customer_order_share_pct

FROM mart.mart_orders;
