import os
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

EVENT_FILE = "data/raw/o2c_events.csv"
ORDER_FILE = "data/raw/o2c_orders.csv"

REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

events = pd.read_csv(EVENT_FILE)
orders = pd.read_csv(ORDER_FILE)

events["timestamp"] = pd.to_datetime(events["timestamp"])

orders["start_time"] = pd.to_datetime(orders["start_time"])
orders["end_time"] = pd.to_datetime(orders["end_time"])


print("=" * 70)
print("O2C PROCESS MINING ANALYSIS")
print("=" * 70)

print(f"\nOrders : {len(orders):,}")
print(f"Events : {len(events):,}")


# ============================================================
# 1. PROCESS VARIANTS
# ============================================================

print("\n" + "=" * 70)
print("1. PROCESS VARIANTS")
print("=" * 70)

# Sort events
events = events.sort_values(
    ["case_id", "timestamp"]
)

# Create activity sequence for each order
variants = (
    events
    .groupby("case_id")["activity"]
    .apply(lambda x: " → ".join(x))
    .reset_index(name="variant")
)

# Count variants
variant_counts = (
    variants["variant"]
    .value_counts()
    .reset_index()
)

variant_counts.columns = [
    "variant",
    "order_count"
]

variant_counts["percentage"] = (
    variant_counts["order_count"]
    / len(orders)
    * 100
)

print("\nTop process variants:\n")

print(
    variant_counts
    .head(10)
    .to_string(index=False)
)


# Save
variant_counts.to_csv(
    f"{REPORT_DIR}/process_variants.csv",
    index=False
)


# ============================================================
# 2. ACTIVITY FREQUENCY
# ============================================================

print("\n" + "=" * 70)
print("2. ACTIVITY FREQUENCY")
print("=" * 70)

activity_counts = (
    events["activity"]
    .value_counts()
    .reset_index()
)

activity_counts.columns = [
    "activity",
    "event_count"
]

print(
    activity_counts.to_string(index=False)
)

activity_counts.to_csv(
    f"{REPORT_DIR}/activity_frequency.csv",
    index=False
)


# ============================================================
# 3. ACTIVITY-TO-ACTIVITY THROUGHPUT TIME
# ============================================================

print("\n" + "=" * 70)
print("3. ACTIVITY THROUGHPUT TIME")
print("=" * 70)


events_sorted = events.sort_values(
    ["case_id", "timestamp"]
).copy()

events_sorted["next_activity"] = (
    events_sorted
    .groupby("case_id")["activity"]
    .shift(-1)
)

events_sorted["next_timestamp"] = (
    events_sorted
    .groupby("case_id")["timestamp"]
    .shift(-1)
)

events_sorted["duration_hours"] = (
    (
        events_sorted["next_timestamp"]
        - events_sorted["timestamp"]
    )
    .dt.total_seconds()
    / 3600
)


transitions = (
    events_sorted
    .dropna(subset=["next_activity"])
    .groupby(
        ["activity", "next_activity"]
    )["duration_hours"]
    .agg(
        count="count",
        average_hours="mean",
        median_hours="median",
        max_hours="max"
    )
    .reset_index()
)

transitions["average_hours"] = transitions[
    "average_hours"
].round(2)

transitions["median_hours"] = transitions[
    "median_hours"
].round(2)

transitions["max_hours"] = transitions[
    "max_hours"
].round(2)


transitions = transitions.sort_values(
    "average_hours",
    ascending=False
)

print("\nSlowest transitions:\n")

print(
    transitions
    .head(10)
    .to_string(index=False)
)

transitions.to_csv(
    f"{REPORT_DIR}/activity_transitions.csv",
    index=False
)


# ============================================================
# 4. OVERALL PROCESS PERFORMANCE
# ============================================================

print("\n" + "=" * 70)
print("4. OVERALL PROCESS PERFORMANCE")
print("=" * 70)

avg_cycle_time = orders["total_hours"].mean()
median_cycle_time = orders["total_hours"].median()

delayed_orders = orders["delayed"].sum()

delay_percentage = (
    delayed_orders
    / len(orders)
    * 100
)

rework_orders = orders["rework"].sum()

rework_percentage = (
    rework_orders
    / len(orders)
    * 100
)


print(f"\nAverage cycle time : {avg_cycle_time:.2f} hours")
print(f"Median cycle time  : {median_cycle_time:.2f} hours")

print(
    f"Delayed orders     : "
    f"{delayed_orders:,} ({delay_percentage:.2f}%)"
)

print(
    f"Rework orders      : "
    f"{rework_orders:,} ({rework_percentage:.2f}%)"
)


# ============================================================
# 5. REWORK VS NON-REWORK
# ============================================================

print("\n" + "=" * 70)
print("5. REWORK IMPACT")
print("=" * 70)

rework_analysis = (
    orders
    .groupby("rework")["total_hours"]
    .agg(
        order_count="count",
        average_hours="mean",
        median_hours="median"
    )
    .reset_index()
)

rework_analysis["rework"] = (
    rework_analysis["rework"]
    .map({
        0: "No Rework",
        1: "Rework"
    })
)

rework_analysis["average_hours"] = (
    rework_analysis["average_hours"]
    .round(2)
)

rework_analysis["median_hours"] = (
    rework_analysis["median_hours"]
    .round(2)
)

print(
    rework_analysis.to_string(index=False)
)

rework_analysis.to_csv(
    f"{REPORT_DIR}/rework_analysis.csv",
    index=False
)


# ============================================================
# 6. WAREHOUSE PERFORMANCE
# ============================================================

print("\n" + "=" * 70)
print("6. WAREHOUSE PERFORMANCE")
print("=" * 70)

warehouse_analysis = (
    orders
    .groupby("warehouse")
    .agg(
        orders=("case_id", "count"),
        average_cycle_hours=("total_hours", "mean"),
        median_cycle_hours=("total_hours", "median"),
        delayed_orders=("delayed", "sum"),
        rework_orders=("rework", "sum")
    )
    .reset_index()
)

warehouse_analysis["delay_percentage"] = (
    warehouse_analysis["delayed_orders"]
    / warehouse_analysis["orders"]
    * 100
)

warehouse_analysis["rework_percentage"] = (
    warehouse_analysis["rework_orders"]
    / warehouse_analysis["orders"]
    * 100
)

warehouse_analysis["average_cycle_hours"] = (
    warehouse_analysis["average_cycle_hours"]
    .round(2)
)

warehouse_analysis["median_cycle_hours"] = (
    warehouse_analysis["median_cycle_hours"]
    .round(2)
)

warehouse_analysis["delay_percentage"] = (
    warehouse_analysis["delay_percentage"]
    .round(2)
)

warehouse_analysis["rework_percentage"] = (
    warehouse_analysis["rework_percentage"]
    .round(2)
)

print(
    warehouse_analysis.to_string(index=False)
)

warehouse_analysis.to_csv(
    f"{REPORT_DIR}/warehouse_performance.csv",
    index=False
)


# ============================================================
# 7. SHIPPING METHOD PERFORMANCE
# ============================================================

print("\n" + "=" * 70)
print("7. SHIPPING METHOD PERFORMANCE")
print("=" * 70)

shipping_analysis = (
    orders
    .groupby("shipping_method")
    .agg(
        orders=("case_id", "count"),
        average_cycle_hours=("total_hours", "mean"),
        delayed_orders=("delayed", "sum")
    )
    .reset_index()
)

shipping_analysis["delay_percentage"] = (
    shipping_analysis["delayed_orders"]
    / shipping_analysis["orders"]
    * 100
)

shipping_analysis["average_cycle_hours"] = (
    shipping_analysis["average_cycle_hours"]
    .round(2)
)

shipping_analysis["delay_percentage"] = (
    shipping_analysis["delay_percentage"]
    .round(2)
)

print(
    shipping_analysis.to_string(index=False)
)

shipping_analysis.to_csv(
    f"{REPORT_DIR}/shipping_performance.csv",
    index=False
)


# ============================================================
# 8. CUSTOMER TYPE PERFORMANCE
# ============================================================

print("\n" + "=" * 70)
print("8. CUSTOMER TYPE PERFORMANCE")
print("=" * 70)

customer_analysis = (
    orders
    .groupby("customer_type")
    .agg(
        orders=("case_id", "count"),
        average_cycle_hours=("total_hours", "mean"),
        delayed_orders=("delayed", "sum")
    )
    .reset_index()
)

customer_analysis["delay_percentage"] = (
    customer_analysis["delayed_orders"]
    / customer_analysis["orders"]
    * 100
)

customer_analysis["average_cycle_hours"] = (
    customer_analysis["average_cycle_hours"]
    .round(2)
)

customer_analysis["delay_percentage"] = (
    customer_analysis["delay_percentage"]
    .round(2)
)

print(
    customer_analysis.to_string(index=False)
)

customer_analysis.to_csv(
    f"{REPORT_DIR}/customer_performance.csv",
    index=False
)


# ============================================================
# 9. BUSINESS SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("BUSINESS SUMMARY")
print("=" * 70)

slowest_transition = transitions.iloc[0]

slowest_warehouse = (
    warehouse_analysis
    .sort_values(
        "average_cycle_hours",
        ascending=False
    )
    .iloc[0]
)

highest_delay_warehouse = (
    warehouse_analysis
    .sort_values(
        "delay_percentage",
        ascending=False
    )
    .iloc[0]
)


print(
    f"""
Total orders              : {len(orders):,}
Total events              : {len(events):,}

Average cycle time        : {avg_cycle_time:.2f} hours
Median cycle time         : {median_cycle_time:.2f} hours

Delayed orders            : {delay_percentage:.2f}%
Rework rate               : {rework_percentage:.2f}%

Slowest process transition:
    {slowest_transition['activity']}
    →
    {slowest_transition['next_activity']}

    Average time:
    {slowest_transition['average_hours']:.2f} hours

Slowest warehouse:
    {slowest_warehouse['warehouse']}

    Average cycle:
    {slowest_warehouse['average_cycle_hours']:.2f} hours

Highest delay warehouse:
    {highest_delay_warehouse['warehouse']}

    Delay rate:
    {highest_delay_warehouse['delay_percentage']:.2f}%
"""
)


print("=" * 70)
print("PROCESS ANALYSIS COMPLETE")
print("=" * 70)

print("\nReports saved in:")
print(REPORT_DIR)