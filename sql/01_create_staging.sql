
CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.orders;
CREATE TABLE staging.orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::timestamp AS purchase_timestamp,
    order_approved_at::timestamp AS approved_timestamp,
    order_delivered_carrier_date::timestamp AS carrier_timestamp,
    order_delivered_customer_date::timestamp AS delivered_timestamp,
    order_estimated_delivery_date::timestamp AS estimated_delivery_timestamp
FROM raw.olist_orders_dataset
WHERE order_id IS NOT NULL
  AND customer_id IS NOT NULL;

DROP TABLE IF EXISTS staging.order_items;
CREATE TABLE staging.order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price::numeric AS price,
    freight_value::numeric AS freight_value
FROM raw.olist_order_items_dataset
WHERE order_id IS NOT NULL
  AND product_id IS NOT NULL
  AND price IS NOT NULL
  AND freight_value IS NOT NULL;

DROP TABLE IF EXISTS staging.payments;
CREATE TABLE staging.payments AS
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value::numeric AS payment_value
FROM raw.olist_order_payments_dataset
WHERE order_id IS NOT NULL
  AND payment_value IS NOT NULL;

DROP TABLE IF EXISTS staging.reviews;
CREATE TABLE staging.reviews AS
SELECT
    review_id,
    order_id,
    review_score::integer AS review_score
FROM raw.olist_order_reviews_dataset
WHERE order_id IS NOT NULL
  AND review_score IS NOT NULL
  AND review_score BETWEEN 1 AND 5;

DROP TABLE IF EXISTS staging.customers;
CREATE TABLE staging.customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_state
FROM raw.olist_customers_dataset
WHERE customer_id IS NOT NULL;

DROP TABLE IF EXISTS staging.products;
CREATE TABLE staging.products AS
SELECT
    product_id,
    product_category_name
FROM raw.olist_products_dataset
WHERE product_id IS NOT NULL;
