
-- 02_data_quality_checks.sql
-- Run these checks after creating the staging tables.

-- Check 1: Missing order IDs
SELECT
    '1. Missing order IDs' AS check_name,
    COUNT(*) AS failed_rows
FROM raw.olist_orders_dataset
WHERE order_id IS NULL

UNION ALL

-- Check 2: Duplicate order IDs
SELECT
    '2. Duplicate order IDs',
    COUNT(*)
FROM (
    SELECT order_id
    FROM raw.olist_orders_dataset
    WHERE order_id IS NOT NULL
    GROUP BY order_id
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

-- Check 3: Delivery before purchase
SELECT
    '3. Invalid delivery dates',
    COUNT(*)
FROM staging.orders
WHERE delivered_timestamp < purchase_timestamp

UNION ALL

-- Check 4: Missing or negative item values
SELECT
    '4. Invalid order items',
    COUNT(*)
FROM raw.olist_order_items_dataset
WHERE price IS NULL
   OR freight_value IS NULL
   OR price < 0
   OR freight_value < 0

UNION ALL

-- Check 5: Orders without a matching customer
SELECT
    '5. Missing customers',
    COUNT(*)
FROM staging.orders o
LEFT JOIN staging.customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

-- Check 6: Missing or invalid review scores
SELECT
    '6. Invalid review scores',
    COUNT(*)
FROM raw.olist_order_reviews_dataset
WHERE review_score IS NULL
   OR review_score NOT BETWEEN 1 AND 5

UNION ALL

-- Check 7: Item totals do not match payment totals

-- Check 7: Compare independently aggregated item and payment totals
SELECT
    '7. Payment mismatches' AS check_name,
    COUNT(*) AS failed_rows
FROM (
    SELECT
        i.order_id
    FROM (
        SELECT
            order_id,
            SUM(price + freight_value) AS item_total
        FROM staging.order_items
        GROUP BY order_id
    ) i
    JOIN (
        SELECT
            order_id,
            SUM(payment_value) AS payment_total
        FROM staging.payments
        GROUP BY order_id
    ) p ON i.order_id = p.order_id
    WHERE ABS(i.item_total - p.payment_total) > 0.02
) AS mismatches


UNION ALL

-- Check 8: Orders without any item records
SELECT
    '8. Orders without items',
    COUNT(*)
FROM staging.orders o
LEFT JOIN staging.order_items i
    ON o.order_id = i.order_id
WHERE i.order_id IS NULL

UNION ALL

-- Check 9: Orders without any payment records
SELECT
    '9. Orders without payments',
    COUNT(*)
FROM staging.orders o
LEFT JOIN staging.payments p
    ON o.order_id = p.order_id
WHERE p.order_id IS NULL

ORDER BY check_name;