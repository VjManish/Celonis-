import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

NUM_ORDERS = 5000
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

fake = Faker()
Faker.seed(SEED)

RAW_DIR = "data/raw"

os.makedirs(RAW_DIR, exist_ok=True)


# ============================================================
# MASTER DATA
# ============================================================

warehouses = [
    "WH_NORTH",
    "WH_SOUTH",
    "WH_EAST",
    "WH_WEST"
]

customer_types = [
    "Enterprise",
    "SMB",
    "Retail"
]

shipping_methods = [
    "Standard",
    "Express",
    "Priority"
]

product_categories = [
    "Electronics",
    "Furniture",
    "Clothing",
    "Industrial",
    "Office Supplies"
]


# ============================================================
# EVENT GENERATION
# ============================================================

events = []
orders = []

start_date = datetime(2026, 1, 1)


def add_event(
    case_id,
    activity,
    timestamp,
    customer_id,
    warehouse,
    order_value
):
    events.append({
        "case_id": case_id,
        "activity": activity,
        "timestamp": timestamp,
        "customer_id": customer_id,
        "warehouse": warehouse,
        "order_value": round(order_value, 2)
    })


for i in range(1, NUM_ORDERS + 1):

    case_id = f"ORD{i:05d}"

    customer_id = f"CUST{random.randint(1, 1000):04d}"

    warehouse = random.choice(warehouses)

    customer_type = random.choice(customer_types)

    shipping_method = random.choice(shipping_methods)

    product_category = random.choice(product_categories)

    order_value = round(
        np.random.lognormal(mean=7.5, sigma=0.8),
        2
    )

    # Start time
    current_time = start_date + timedelta(
        days=random.randint(0, 180),
        hours=random.randint(8, 17),
        minutes=random.randint(0, 59)
    )

    order_start = current_time

    add_event(
        case_id,
        "Order Created",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # CREDIT CHECK
    # --------------------------------------------------------

    credit_delay = random.randint(15, 120)

    # Enterprise orders can occasionally experience
    # longer credit checks.
    if customer_type == "Enterprise" and random.random() < 0.15:
        credit_delay += random.randint(300, 900)

    current_time += timedelta(minutes=credit_delay)

    add_event(
        case_id,
        "Credit Check",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # APPROVAL
    # --------------------------------------------------------

    approval_delay = random.randint(20, 180)

    # Some orders require manual approval.
    manual_approval = random.random() < 0.12

    if manual_approval:
        approval_delay += random.randint(240, 900)

    current_time += timedelta(minutes=approval_delay)

    add_event(
        case_id,
        "Order Approved",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # PICKING
    # --------------------------------------------------------

    picking_delay = random.randint(60, 360)

    # Warehouse-specific bottleneck
    if warehouse == "WH_EAST" and random.random() < 0.30:
        picking_delay += random.randint(300, 900)

    current_time += timedelta(minutes=picking_delay)

    add_event(
        case_id,
        "Picking",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # REWORK
    # --------------------------------------------------------

    rework = random.random() < 0.08

    if rework:

        current_time += timedelta(
            minutes=random.randint(120, 600)
        )

        add_event(
            case_id,
            "Rework",
            current_time,
            customer_id,
            warehouse,
            order_value
        )

        current_time += timedelta(
            minutes=random.randint(60, 240)
        )

        add_event(
            case_id,
            "Picking",
            current_time,
            customer_id,
            warehouse,
            order_value
        )

    # --------------------------------------------------------
    # PACKING
    # --------------------------------------------------------

    current_time += timedelta(
        minutes=random.randint(30, 180)
    )

    add_event(
        case_id,
        "Packing",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # SHIPPING
    # --------------------------------------------------------

    shipping_delay = random.randint(60, 300)

    if shipping_method == "Standard":
        shipping_delay += random.randint(100, 400)

    current_time += timedelta(minutes=shipping_delay)

    add_event(
        case_id,
        "Shipping",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    delivery_delay = {
        "Standard": random.randint(1440, 4320),
        "Express": random.randint(720, 2160),
        "Priority": random.randint(360, 1440)
    }[shipping_method]

    if warehouse == "WH_WEST" and random.random() < 0.20:
        delivery_delay += random.randint(1000, 3000)

    current_time += timedelta(minutes=delivery_delay)

    add_event(
        case_id,
        "Delivery",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # INVOICE
    # --------------------------------------------------------

    invoice_delay = random.randint(30, 240)

    current_time += timedelta(minutes=invoice_delay)

    add_event(
        case_id,
        "Invoice Created",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    payment_delay = random.randint(1440, 10080)

    # Enterprise customers sometimes pay later.
    if customer_type == "Enterprise":
        payment_delay += random.randint(0, 5000)

    current_time += timedelta(minutes=payment_delay)

    add_event(
        case_id,
        "Payment",
        current_time,
        customer_id,
        warehouse,
        order_value
    )

    # --------------------------------------------------------
    # ORDER LEVEL RECORD
    # --------------------------------------------------------

    total_hours = (
        current_time - order_start
    ).total_seconds() / 3600

    # Delay definition:
    # Entire O2C process taking more than 7 days.
    delayed = total_hours > 7 * 24

    orders.append({
        "case_id": case_id,
        "customer_id": customer_id,
        "customer_type": customer_type,
        "warehouse": warehouse,
        "shipping_method": shipping_method,
        "product_category": product_category,
        "order_value": order_value,
        "start_time": order_start,
        "end_time": current_time,
        "total_hours": round(total_hours, 2),
        "delayed": int(delayed),
        "manual_approval": int(manual_approval),
        "rework": int(rework)
    })


# ============================================================
# DATAFRAMES
# ============================================================

events_df = pd.DataFrame(events)
orders_df = pd.DataFrame(orders)

events_df["timestamp"] = pd.to_datetime(events_df["timestamp"])
orders_df["start_time"] = pd.to_datetime(orders_df["start_time"])
orders_df["end_time"] = pd.to_datetime(orders_df["end_time"])


# ============================================================
# SAVE
# ============================================================

events_path = os.path.join(
    RAW_DIR,
    "o2c_events.csv"
)

orders_path = os.path.join(
    RAW_DIR,
    "o2c_orders.csv"
)

events_df.to_csv(events_path, index=False)
orders_df.to_csv(orders_path, index=False)


print("=" * 60)
print("O2C DATA GENERATION COMPLETE")
print("=" * 60)

print(f"Orders generated : {len(orders_df):,}")
print(f"Events generated : {len(events_df):,}")

print("\nDelayed orders:")
print(
    orders_df["delayed"]
    .value_counts()
    .rename({0: "On Time", 1: "Delayed"})
)

print("\nEvent distribution:")
print(events_df["activity"].value_counts())

print("\nFiles:")
print(events_path)
print(orders_path)