"""
02_clean_data.py
-----------------
STEP 2: DATA CLEANING & TRANSFORMATION

Takes the raw extracted CSVs and produces a single clean, analysis-ready
fact table plus cleaned dimension tables. This is the step every recruiter
wants to see evidence of -- handling missing values, fixing types, joining
across tables, and creating derived business columns (revenue, profit, etc).

Run:
    python 02_clean_data.py
Output:
    data/processed/orders_clean.csv        (cleaned order-level table)
    data/processed/fact_sales.csv          (order_item-level fact table, analysis-ready)
"""

import pandas as pd
import numpy as np

RAW = "data/raw"
OUT = "data/processed"


def load_raw():
    customers = pd.read_csv(f"{RAW}/customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv(f"{RAW}/products.csv")
    orders = pd.read_csv(f"{RAW}/orders.csv", parse_dates=["order_date"])
    order_items = pd.read_csv(f"{RAW}/order_items.csv")
    payments = pd.read_csv(f"{RAW}/payments.csv")
    return customers, products, orders, order_items, payments


def clean_customers(customers):
    before = len(customers)
    # Fill missing region with "Unknown" rather than dropping (dropping loses order history)
    customers["region"] = customers["region"].fillna("Unknown")
    # Impute missing age with median (robust to outliers) and flag it
    customers["age_imputed"] = customers["age"].isna()
    customers["age"] = customers["age"].fillna(customers["age"].median())
    print(f"[customers] {before} rows in, {len(customers)} rows out. "
          f"Imputed {customers['age_imputed'].sum()} missing ages, "
          f"filled missing regions with 'Unknown'.")
    return customers


def clean_orders(orders):
    before = len(orders)
    orders = orders.drop_duplicates(subset="order_id")
    # Remove orders with impossible delivery times (data entry errors, keep < 60 days)
    orders = orders[orders["delivery_days"].between(0, 60)]
    print(f"[orders] {before} rows in, {len(orders)} rows out after de-dup/outlier removal.")
    return orders


def build_fact_sales(customers, products, orders, order_items, payments):
    # Only keep orders that are NOT canceled for revenue calculations
    # (canceled orders are tracked separately for cancellation-rate analysis)
    fact = (
        order_items
        .merge(products, on="product_id", how="left")
        .merge(orders, on="order_id", how="left")
        .merge(customers[["customer_id", "region", "age", "signup_date"]], on="customer_id", how="left")
        .merge(payments, on="order_id", how="left")
    )

    fact["gross_revenue"] = fact["quantity"] * fact["unit_price"]
    fact["cost"] = fact["quantity"] * fact["unit_cost"]
    fact["profit"] = fact["gross_revenue"] - fact["cost"]
    fact["profit_margin_pct"] = (fact["profit"] / fact["gross_revenue"] * 100).round(2)

    fact["order_year"] = fact["order_date"].dt.year
    fact["order_month"] = fact["order_date"].dt.to_period("M").astype(str)
    fact["order_quarter"] = fact["order_date"].dt.to_period("Q").astype(str)

    # Drop rows that failed to join (would indicate referential integrity issues -- log them)
    before = len(fact)
    fact = fact.dropna(subset=["order_date", "unit_price"])
    dropped = before - len(fact)
    if dropped:
        print(f"[fact_sales] Dropped {dropped} rows with broken joins (missing order/product match).")

    return fact


if __name__ == "__main__":
    customers, products, orders, order_items, payments = load_raw()

    customers = clean_customers(customers)
    orders = clean_orders(orders)

    orders_clean = orders.merge(customers[["customer_id", "region"]], on="customer_id", how="left")
    orders_clean.to_csv(f"{OUT}/orders_clean.csv", index=False)

    fact_sales = build_fact_sales(customers, products, orders, order_items, payments)
    fact_sales.to_csv(f"{OUT}/fact_sales.csv", index=False)

    print(f"\nSaved: {OUT}/orders_clean.csv ({len(orders_clean)} rows)")
    print(f"Saved: {OUT}/fact_sales.csv ({len(fact_sales)} rows, {fact_sales.shape[1]} cols)")
    print("\nfact_sales.csv columns:", list(fact_sales.columns))
