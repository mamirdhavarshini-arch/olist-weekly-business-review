
CREATE SCHEMA IF NOT EXISTS mart;

DROP TABLE IF EXISTS mart.mart_orders;

CREATE TABLE mart.mart_orders AS
WITH item_summary AS (
    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS product_revenue,
        SUM(freight_value) AS freight_revenue,
        SUM(price + freight_value) AS total_order_value
    FROM staging.order_items
    GROUP BY order_id
),
payment_summary AS (
    SELECT
        order_id,
        SUM(payment_value) AS payment_total
    FROM staging.payments
    GROUP BY order_id
),
review_summary AS (
    SELECT
        order_id,
        AVG(review_score) AS avg_review_score
    FROM staging.reviews
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.purchase_timestamp,
    o.delivered_timestamp,
    o.estimated_delivery_timestamp,
    COALESCE(i.item_count, 0) AS item_count,
    COALESCE(i.product_revenue, 0) AS product_revenue,
    COALESCE(i.freight_revenue, 0) AS freight_revenue,
    COALESCE(i.total_order_value, 0) AS total_order_value,
    p.payment_total,
    r.avg_review_score,
    CASE
        WHEN o.delivered_timestamp IS NOT NULL
         AND o.estimated_delivery_timestamp IS NOT NULL
         AND o.delivered_timestamp
             <= o.estimated_delivery_timestamp
        THEN TRUE
        WHEN o.delivered_timestamp IS NOT NULL
         AND o.estimated_delivery_timestamp IS NOT NULL
        THEN FALSE
        ELSE NULL
    END AS delivered_on_time,
    CASE
        WHEN o.delivered_timestamp IS NOT NULL
         AND o.estimated_delivery_timestamp IS NOT NULL
        THEN
            EXTRACT(
                EPOCH FROM (
                    o.delivered_timestamp
                    - o.estimated_delivery_timestamp
                )
            ) / 86400.0
        ELSE NULL
    END AS delivery_delay_days
FROM staging.orders o
LEFT JOIN staging.customers c
    ON o.customer_id = c.customer_id
LEFT JOIN item_summary i
    ON o.order_id = i.order_id
LEFT JOIN payment_summary p
    ON o.order_id = p.order_id
LEFT JOIN review_summary r
    ON o.order_id = r.order_id;
