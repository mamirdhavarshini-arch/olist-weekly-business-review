
WITH category_revenue AS (
    SELECT
        c.customer_state,
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS category_name,
        SUM(i.price) AS revenue
    FROM staging.order_items i
    JOIN staging.orders o
        ON i.order_id = o.order_id
    JOIN staging.customers c
        ON o.customer_id = c.customer_id
    JOIN staging.products p
        ON i.product_id = p.product_id
    LEFT JOIN raw.product_category_name_translation t
        ON p.product_category_name = t.product_category_name
    GROUP BY
        c.customer_state,
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )
),
ranked_categories AS (
    SELECT
        customer_state,
        category_name,
        revenue,
        DENSE_RANK() OVER (
            PARTITION BY customer_state
            ORDER BY revenue DESC
        ) AS category_rank
    FROM category_revenue
)
SELECT
    customer_state,
    category_name,
    ROUND(revenue::numeric, 2) AS revenue,
    category_rank
FROM ranked_categories
WHERE category_rank <= 3
ORDER BY customer_state, category_rank, category_name;
