# Weekly Business Review — Olist E-commerce Marketplace

**To:** Vice President  
**Subject:** Delivery Performance, Customer Experience, and Repeat Purchasing

## Executive Summary

The analysis covers **99,441 orders** in the Olist order mart. The North Star metric, on-time delivery rate, is **91.89%**, while **8.11%** of orders with known delivery outcomes were delivered late. The average customer review score is **4.09 out of 5**, indicating a generally positive average rating. The average order value, defined as product price plus freight, is **159.33** in the dataset's currency.

## Key Findings

- **Delivery reliability:** 91.89% of orders with known delivery outcomes arrived on or before their estimated delivery dates.
- **Customer experience:** The average review score is 4.09/5. Review scores should also be compared between late and on-time deliveries to identify potential service-quality differences.
- **Repeat purchasing:** The repeat purchase rate is **3.12% of unique customers** represented in the mart. The repeat-customer order share is **6.38%**; these metrics use different denominators.
- **Revenue and product mix:** Monthly order value and category-level revenue provide a basis for monitoring commercial performance and identifying high-performing categories.

## Recommended Actions

1. Investigate late deliveries by customer state, product category, seller, and delivery period.
2. Monitor on-time delivery rate and late-delivery rate weekly, alongside customer review scores.
3. Examine repeat-purchase patterns and identify customer segments that may benefit from retention initiatives.
4. Review data-quality exceptions before using financial or operational figures for decisions.

## Measurement Notes

On-time delivery includes orders delivered before or on the estimated date. Average order value is the mean of product price plus freight per order, not a separately verified accounting revenue measure. Repeat purchase rate is calculated using `customer_unique_id`. Data-quality exceptions should be reviewed before drawing conclusions from affected records.