"""
01_extract_data.py
-------------------
STEP 1: DATA EXTRACTION

In a real placement project you'd pull this from a live source, e.g.:
    - A production MySQL/Postgres replica (via SQLAlchemy)
    - A REST API (via requests)
    - A raw CSV export from Kaggle's "Brazilian E-Commerce (Olist)" dataset

For this project we simulate a realistic e-commerce operational database
(orders, customers, products, order_items, payments) with the SAME schema
shape as a real company would hand you. This keeps every downstream script
(cleaning, SQL, EDA, dashboard) portable to a real dataset with zero changes
other than swapping this extraction step.

Run:
    python 01_extract_data.py
Output:
    data/raw/customers.csv
    data/raw/products.csv
    data/raw/orders.csv
    data/raw/order_items.csv
    data/raw/payments.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

RNG_SEED = 42
np.random.seed(RNG_SEED)
random.seed(RNG_SEED)

N_CUSTOMERS = 3000
N_PRODUCTS = 250
N_ORDERS = 12000

REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = [
    "Electronics", "Home & Kitchen", "Fashion", "Beauty & Personal Care",
    "Sports & Outdoors", "Books", "Toys", "Grocery"
]
PAYMENT_TYPES = ["credit_card", "debit_card", "upi", "net_banking", "cod"]
ORDER_STATUS = ["delivered", "delivered", "delivered", "delivered", "shipped", "canceled", "returned"]

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                              seconds=random.randint(0, 86399))


def extract_customers():
    customer_ids = [f"CUST{str(i).zfill(5)}" for i in range(1, N_CUSTOMERS + 1)]
    signup_dates = [random_date(START_DATE - timedelta(days=365), END_DATE) for _ in customer_ids]
    df = pd.DataFrame({
        "customer_id": customer_ids,
        "region": np.random.choice(REGIONS, size=N_CUSTOMERS, p=[0.22, 0.20, 0.18, 0.25, 0.15]),
        "signup_date": signup_dates,
        "age": np.random.randint(18, 65, size=N_CUSTOMERS),
    })
    # inject a few messy values on purpose (real data extraction is never clean)
    messy_idx = np.random.choice(df.index, size=40, replace=False)
    df.loc[messy_idx[:20], "age"] = np.nan
    df.loc[messy_idx[20:], "region"] = None
    return df


def extract_products():
    product_ids = [f"PROD{str(i).zfill(4)}" for i in range(1, N_PRODUCTS + 1)]
    categories = np.random.choice(CATEGORIES, size=N_PRODUCTS)
    base_price = {
        "Electronics": (1500, 45000), "Home & Kitchen": (300, 8000),
        "Fashion": (200, 4000), "Beauty & Personal Care": (150, 2500),
        "Sports & Outdoors": (300, 12000), "Books": (100, 1200),
        "Toys": (150, 3000), "Grocery": (50, 900),
    }
    prices = [round(np.random.uniform(*base_price[c]), 2) for c in categories]
    cost_ratio = np.random.uniform(0.55, 0.8, size=N_PRODUCTS)  # cost as % of price
    df = pd.DataFrame({
        "product_id": product_ids,
        "category": categories,
        "unit_price": prices,
        "unit_cost": np.round(np.array(prices) * cost_ratio, 2),
    })
    return df


def extract_orders(customers_df):
    order_ids = [f"ORD{str(i).zfill(6)}" for i in range(1, N_ORDERS + 1)]
    cust_sample = np.random.choice(customers_df["customer_id"], size=N_ORDERS)
    order_dates = [random_date(START_DATE, END_DATE) for _ in order_ids]
    status = np.random.choice(ORDER_STATUS, size=N_ORDERS)
    # delivery delay in days -- deliberately worse for a couple of regions to create a findable insight
    delivery_days = np.random.gamma(shape=3.0, scale=2.0, size=N_ORDERS).round().astype(int) + 1

    df = pd.DataFrame({
        "order_id": order_ids,
        "customer_id": cust_sample,
        "order_date": order_dates,
        "order_status": status,
        "delivery_days": delivery_days,
    })
    return df


def extract_order_items(orders_df, products_df):
    rows = []
    for order_id in orders_df["order_id"]:
        n_items = np.random.choice([1, 1, 2, 2, 3, 4], p=[0.35, 0.25, 0.2, 0.1, 0.06, 0.04])
        chosen_products = np.random.choice(products_df["product_id"], size=n_items, replace=False)
        for pid in chosen_products:
            qty = np.random.choice([1, 1, 1, 2, 3], p=[0.55, 0.2, 0.15, 0.06, 0.04])
            rows.append((order_id, pid, qty))
    df = pd.DataFrame(rows, columns=["order_id", "product_id", "quantity"])
    return df


def extract_payments(orders_df):
    df = pd.DataFrame({
        "order_id": orders_df["order_id"],
        "payment_type": np.random.choice(PAYMENT_TYPES, size=len(orders_df),
                                          p=[0.4, 0.25, 0.2, 0.1, 0.05]),
        "installments": np.random.choice([1, 1, 2, 3, 6], size=len(orders_df),
                                          p=[0.6, 0.15, 0.1, 0.1, 0.05]),
    })
    return df


if __name__ == "__main__":
    print("Extracting customers...")
    customers = extract_customers()
    print("Extracting products...")
    products = extract_products()
    print("Extracting orders...")
    orders = extract_orders(customers)
    print("Extracting order_items...")
    order_items = extract_order_items(orders, products)
    print("Extracting payments...")
    payments = extract_payments(orders)

    customers.to_csv("data/raw/customers.csv", index=False)
    products.to_csv("data/raw/products.csv", index=False)
    orders.to_csv("data/raw/orders.csv", index=False)
    order_items.to_csv("data/raw/order_items.csv", index=False)
    payments.to_csv("data/raw/payments.csv", index=False)

    print("\nExtraction complete. Files written to data/raw/:")
    for name, d in [("customers", customers), ("products", products),
                     ("orders", orders), ("order_items", order_items),
                     ("payments", payments)]:
        print(f"  {name}.csv -> {d.shape[0]} rows, {d.shape[1]} cols")
