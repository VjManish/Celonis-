-- ============================================================
-- O2C PROCESS INTELLIGENCE - SQL ANALYSIS
-- ============================================================


-- ============================================================
-- 1. BASIC PROCESS KPI
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    ROUND(AVG(total_hours), 2) AS avg_cycle_time_hours,
    ROUND(MEDIAN(total_hours), 2) AS median_cycle_time_hours
FROM orders;


-- ============================================================
-- 2. DELAY RATE
-- ============================================================

SELECT
    COUNT(*) AS total_orders,

    SUM(
        CASE
            WHEN delayed = 1 THEN 1
            ELSE 0
        END
    ) AS delayed_orders,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN delayed = 1 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS delay_percentage

FROM orders;


-- ============================================================
-- 3. REWORK RATE
-- ============================================================

SELECT
    COUNT(*) AS total_orders,

    SUM(rework) AS rework_orders,

    ROUND(
        100.0 * SUM(rework) / COUNT(*),
        2
    ) AS rework_percentage

FROM orders;


-- ============================================================
-- 4. WAREHOUSE PERFORMANCE
-- ============================================================

SELECT
    warehouse,

    COUNT(*) AS orders,

    ROUND(
        AVG(total_hours),
        2
    ) AS avg_cycle_time_hours,

    SUM(delayed) AS delayed_orders,

    ROUND(
        100.0 * SUM(delayed) / COUNT(*),
        2
    ) AS delay_percentage,

    SUM(rework) AS rework_orders,

    ROUND(
        100.0 * SUM(rework) / COUNT(*),
        2
    ) AS rework_percentage

FROM orders

GROUP BY warehouse

ORDER BY delay_percentage DESC;


-- ============================================================
-- 5. SHIPPING METHOD PERFORMANCE
-- ============================================================

SELECT
    shipping_method,

    COUNT(*) AS orders,

    ROUND(
        AVG(total_hours),
        2
    ) AS avg_cycle_time_hours,

    SUM(delayed) AS delayed_orders,

    ROUND(
        100.0 * SUM(delayed) / COUNT(*),
        2
    ) AS delay_percentage

FROM orders

GROUP BY shipping_method

ORDER BY delay_percentage DESC;


-- ============================================================
-- 6. CUSTOMER SEGMENT PERFORMANCE
-- ============================================================

SELECT
    customer_type,

    COUNT(*) AS orders,

    ROUND(
        AVG(total_hours),
        2
    ) AS avg_cycle_time_hours,

    SUM(delayed) AS delayed_orders,

    ROUND(
        100.0 * SUM(delayed) / COUNT(*),
        2
    ) AS delay_percentage

FROM orders

GROUP BY customer_type

ORDER BY delay_percentage DESC;


-- ============================================================
-- 7. REWORK IMPACT
-- ============================================================

SELECT
    CASE
        WHEN rework = 1 THEN 'With Rework'
        ELSE 'Without Rework'
    END AS rework_status,

    COUNT(*) AS orders,

    ROUND(
        AVG(total_hours),
        2
    ) AS avg_cycle_time_hours,

    ROUND(
        AVG(delayed) * 100,
        2
    ) AS delay_percentage

FROM orders

GROUP BY rework

ORDER BY rework DESC;


-- ============================================================
-- 8. HIGH-RISK ORDERS
-- ============================================================

SELECT
    case_id,
    customer_type,
    warehouse,
    shipping_method,
    order_value,
    total_hours,
    delayed,
    rework

FROM orders

WHERE delayed = 1

ORDER BY total_hours DESC

LIMIT 20;