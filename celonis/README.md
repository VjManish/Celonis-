# Celonis O2C Data Model & PQL

This folder contains the Celonis-oriented representation of the
Order-to-Cash Process Intelligence project.

## Process

Order Created
      ↓
Credit Check
      ↓
Order Approved
      ↓
Picking
      ↓
Packing
      ↓
Shipping
      ↓
Delivery
      ↓
Invoice Created
      ↓
Payment

## Objects

- Customer
- Sales Order
- Delivery
- Invoice
- Payment

## Events

- Order Created
- Credit Check
- Order Approved
- Picking
- Rework
- Packing
- Shipping
- Delivery
- Invoice Created
- Payment

## Main Process KPIs

- Average throughput time
- Median throughput time
- Delay rate
- Rework rate
- Invoice-to-payment time
- Warehouse delay rate
- Shipping-method delay rate
- Customer-segment delay rate

## PQL Concepts

The project is designed to demonstrate understanding of:

- PQL
- Process KPIs
- Throughput time
- Process variants
- Event-based analysis
- Object relationships
- Process filtering
- Aggregation
- Root-cause analysis

## Important

The PQL expressions in `pql_kpis.txt` are learning references.
Final syntax depends on the actual Celonis data model and
event-table configuration.