-- ============================================================
-- ORDER-TO-CASH CELONIS DATA MODEL PREPARATION
-- ============================================================

-- ============================================================
-- 1. SALES ORDERS
-- ============================================================

CREATE OR REPLACE TABLE sales_orders AS
SELECT
    case_id,
    customer_id,
    customer_type,
    warehouse,
    shipping_method,
    product_category,
    order_value,
    manual_approval,
    rework,
    delayed,
    start_time,
    end_time,
    total_hours
FROM read_csv_auto(
    'data/raw/o2c_orders.csv',
    HEADER = TRUE
);


-- ============================================================
-- 2. PROCESS EVENTS
-- ============================================================

CREATE OR REPLACE TABLE process_events AS
SELECT
    case_id,
    activity,
    CAST(timestamp AS TIMESTAMP) AS event_timestamp
FROM read_csv_auto(
    'data/raw/o2c_events.csv',
    HEADER = TRUE
);


-- ============================================================
-- 3. CUSTOMERS
-- ============================================================

CREATE OR REPLACE TABLE customers AS
SELECT DISTINCT
    customer_id,
    customer_type
FROM sales_orders;


-- ============================================================
-- 4. DATA QUALITY CHECKS
-- ============================================================

-- Orders
SELECT COUNT(*) AS total_orders
FROM sales_orders;


-- Events
SELECT COUNT(*) AS total_events
FROM process_events;


-- Orders without events
SELECT COUNT(*) AS orders_without_events
FROM sales_orders o
LEFT JOIN process_events e
    ON o.case_id = e.case_id
WHERE e.case_id IS NULL;


-- Events without orders
SELECT COUNT(*) AS events_without_orders
FROM process_events e
LEFT JOIN sales_orders o
    ON e.case_id = o.case_id
WHERE o.case_id IS NULL;


-- ============================================================
-- 5. EVENT LOG STRUCTURE
-- ============================================================

SELECT
    case_id,
    activity,
    event_timestamp
FROM process_events
ORDER BY
    case_id,
    event_timestamp;


-- ============================================================
-- CELONIS MAPPING
-- ============================================================

-- Case ID:
--     case_id
--
-- Activity:
--     activity
--
-- Timestamp:
--     event_timestamp
--
-- Main relationship:
--
-- sales_orders.case_id
--          |
--          |
--          v
-- process_events.case_id
--
-- Customer:
-- sales_orders.customer_id
--          |
--          v
-- customers.customer_id