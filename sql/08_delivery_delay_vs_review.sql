
SELECT
    CASE
        WHEN delivery_delay_days < 0 THEN 'Early delivery'
        WHEN delivery_delay_days = 0 THEN 'On-time delivery'
        WHEN delivery_delay_days > 0 THEN 'Late delivery'
    END AS delivery_category,
    COUNT(*) AS order_count,
    ROUND(AVG(delivery_delay_days)::numeric, 2)
        AS average_delay_days,
    ROUND(AVG(avg_review_score)::numeric, 2)
        AS average_review_score
FROM mart.mart_orders
WHERE delivery_delay_days IS NOT NULL
  AND avg_review_score IS NOT NULL
GROUP BY
    CASE
        WHEN delivery_delay_days < 0 THEN 'Early delivery'
        WHEN delivery_delay_days = 0 THEN 'On-time delivery'
        WHEN delivery_delay_days > 0 THEN 'Late delivery'
    END
ORDER BY
    CASE
        WHEN
            CASE
                WHEN delivery_delay_days < 0 THEN 'Early delivery'
                WHEN delivery_delay_days = 0 THEN 'On-time delivery'
                WHEN delivery_delay_days > 0 THEN 'Late delivery'
            END = 'Early delivery' THEN 1
        WHEN
            CASE
                WHEN delivery_delay_days < 0 THEN 'Early delivery'
                WHEN delivery_delay_days = 0 THEN 'On-time delivery'
                WHEN delivery_delay_days > 0 THEN 'Late delivery'
            END = 'On-time delivery' THEN 2
        ELSE 3
    END;
