-- ============================================================================
-- analysis_queries.sql
-- E-commerce Sales Analytics — Business Question SQL Bank
-- Database: SQLite (sql/ecommerce.db). Standard ANSI SQL, portable to
-- Postgres/MySQL/Snowflake with minimal syntax changes (window functions,
-- CTEs used throughout, no vendor-specific functions except date formatting).
-- ============================================================================


-- ----------------------------------------------------------------------------
-- Q1. Monthly revenue and profit trend
-- Business question: Is the business growing month over month?
-- ----------------------------------------------------------------------------
SELECT
    order_month,
    ROUND(SUM(gross_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2)        AS profit,
    ROUND(SUM(profit) * 100.0 / SUM(gross_revenue), 2) AS profit_margin_pct,
    COUNT(DISTINCT order_id)     AS num_orders
FROM fact_sales
WHERE order_status != 'canceled'
GROUP BY order_month
ORDER BY order_month;


-- ----------------------------------------------------------------------------
-- Q2. Revenue and MoM growth rate using a window function
-- Business question: Which months grew/shrank, and by how much?
-- ----------------------------------------------------------------------------
WITH monthly AS (
    SELECT order_month, SUM(gross_revenue) AS revenue
    FROM fact_sales
    WHERE order_status != 'canceled'
    GROUP BY order_month
)
SELECT
    order_month,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue - LAG(revenue) OVER (ORDER BY order_month), 2) AS revenue_change,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY order_month)) * 100.0
        / LAG(revenue) OVER (ORDER BY order_month), 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY order_month;


-- ----------------------------------------------------------------------------
-- Q3. Top 10 product categories by revenue and margin
-- Business question: Where should marketing/inventory spend focus?
-- ----------------------------------------------------------------------------
SELECT
    category,
    ROUND(SUM(gross_revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2)        AS total_profit,
    ROUND(AVG(profit_margin_pct), 2) AS avg_margin_pct,
    COUNT(DISTINCT order_id)     AS num_orders
FROM fact_sales
WHERE order_status != 'canceled'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- Q4. Regional performance: revenue vs. delivery delay vs. cancellation rate
-- Business question: Which regions underperform, and why?
-- ----------------------------------------------------------------------------
WITH region_orders AS (
    SELECT
        region,
        order_id,
        order_status,
        delivery_days
    FROM orders
),
region_revenue AS (
    SELECT region, SUM(gross_revenue) AS revenue
    FROM fact_sales
    WHERE order_status != 'canceled'
    GROUP BY region
)
SELECT
    ro.region,
    COUNT(DISTINCT ro.order_id) AS total_orders,
    ROUND(AVG(ro.delivery_days), 1) AS avg_delivery_days,
    ROUND(
        SUM(CASE WHEN ro.order_status = 'canceled' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*), 2
    ) AS cancellation_rate_pct,
    ROUND(rr.revenue, 2) AS revenue
FROM region_orders ro
LEFT JOIN region_revenue rr ON ro.region = rr.region
GROUP BY ro.region, rr.revenue
ORDER BY revenue DESC;


-- ----------------------------------------------------------------------------
-- Q5. Customer segmentation via RFM (Recency, Frequency, Monetary)
-- Business question: Who are our best customers, and who is at risk of churn?
-- ----------------------------------------------------------------------------
WITH customer_orders AS (
    SELECT
        customer_id,
        MAX(order_date)              AS last_order_date,
        COUNT(DISTINCT order_id)     AS frequency,
        SUM(gross_revenue)           AS monetary
    FROM fact_sales
    WHERE order_status != 'canceled'
    GROUP BY customer_id
),
scored AS (
    SELECT
        customer_id,
        last_order_date,
        frequency,
        monetary,
        CAST(julianday('2024-12-31') - julianday(last_order_date) AS INTEGER) AS recency_days,
        NTILE(4) OVER (ORDER BY julianday('2024-12-31') - julianday(last_order_date) DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC)  AS m_score
    FROM customer_orders
)
SELECT
    customer_id,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN (r_score + f_score + m_score) >= 10 THEN 'Champions'
        WHEN (r_score + f_score + m_score) >= 7  THEN 'Loyal'
        WHEN (r_score + f_score + m_score) >= 5  THEN 'At Risk'
        ELSE 'Dormant / Churned'
    END AS segment
FROM scored
ORDER BY rfm_total DESC;


-- ----------------------------------------------------------------------------
-- Q6. Segment summary — how much revenue does each RFM segment represent?
-- Business question: Where is revenue concentrated? (80/20 check)
-- ----------------------------------------------------------------------------
WITH customer_orders AS (
    SELECT customer_id, MAX(order_date) AS last_order_date,
           COUNT(DISTINCT order_id) AS frequency, SUM(gross_revenue) AS monetary
    FROM fact_sales WHERE order_status != 'canceled'
    GROUP BY customer_id
),
scored AS (
    SELECT customer_id, monetary,
        NTILE(4) OVER (ORDER BY julianday('2024-12-31') - julianday(last_order_date) DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC)  AS m_score
    FROM customer_orders
),
segmented AS (
    SELECT customer_id, monetary,
        CASE
            WHEN (r_score + f_score + m_score) >= 10 THEN 'Champions'
            WHEN (r_score + f_score + m_score) >= 7  THEN 'Loyal'
            WHEN (r_score + f_score + m_score) >= 5  THEN 'At Risk'
            ELSE 'Dormant / Churned'
        END AS segment
    FROM scored
)
SELECT
    segment,
    COUNT(*) AS num_customers,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(SUM(monetary) * 100.0 / (SELECT SUM(monetary) FROM segmented), 2) AS pct_of_total_revenue
FROM segmented
GROUP BY segment
ORDER BY total_revenue DESC;


-- ----------------------------------------------------------------------------
-- Q7. Payment type vs. cancellation rate
-- Business question: Does payment method affect order reliability?
-- ----------------------------------------------------------------------------
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) * 100.0
          / COUNT(DISTINCT order_id), 2) AS cancellation_rate_pct
FROM fact_sales
GROUP BY payment_type
ORDER BY cancellation_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- Q8. Top 10 products by profit contribution (not just revenue)
-- Business question: Which SKUs should we push harder / restock first?
-- ----------------------------------------------------------------------------
SELECT
    product_id,
    category,
    ROUND(SUM(gross_revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(AVG(profit_margin_pct), 2) AS avg_margin_pct,
    SUM(quantity) AS units_sold
FROM fact_sales
WHERE order_status != 'canceled'
GROUP BY product_id, category
ORDER BY profit DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- Q9. Cohort retention — of customers who first ordered in a given month,
--     what % placed another order in a later month?
-- Business question: How sticky are new customers?
-- ----------------------------------------------------------------------------
WITH first_order AS (
    SELECT customer_id, MIN(order_month) AS cohort_month
    FROM fact_sales
    GROUP BY customer_id
),
orders_with_cohort AS (
    SELECT f.customer_id, f.order_month, fo.cohort_month
    FROM fact_sales f
    JOIN first_order fo ON f.customer_id = fo.customer_id
)
SELECT
    cohort_month,
    order_month,
    COUNT(DISTINCT customer_id) AS active_customers
FROM orders_with_cohort
GROUP BY cohort_month, order_month
ORDER BY cohort_month, order_month;


-- ----------------------------------------------------------------------------
-- Q10. Average order value (AOV) trend by quarter
-- Business question: Are customers spending more or less per order over time?
-- ----------------------------------------------------------------------------
SELECT
    order_quarter,
    ROUND(SUM(gross_revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
    COUNT(DISTINCT order_id) AS num_orders
FROM fact_sales
WHERE order_status != 'canceled'
GROUP BY order_quarter
ORDER BY order_quarter;
