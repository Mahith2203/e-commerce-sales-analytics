"""
03_load_to_db.py
-----------------
STEP 3: LOAD INTO DATABASE

Loads the cleaned fact table + dimension tables into a SQLite database so
we can run real SQL against it. (SQLite is used here for portability --
in a company setting this would be Postgres/MySQL/Snowflake/BigQuery, and
every query in analysis_queries.sql would run unchanged.)

Run:
    python sql/03_load_to_db.py
Output:
    sql/ecommerce.db
"""

import sqlite3
import pandas as pd

DB_PATH = "sql/ecommerce.db"

if __name__ == "__main__":
    fact_sales = pd.read_csv("data/processed/fact_sales.csv", parse_dates=["order_date", "signup_date"])
    orders_clean = pd.read_csv("data/processed/orders_clean.csv", parse_dates=["order_date"])
    customers = pd.read_csv("data/raw/customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv("data/raw/products.csv")

    conn = sqlite3.connect(DB_PATH)
    fact_sales.to_sql("fact_sales", conn, if_exists="replace", index=False)
    orders_clean.to_sql("orders", conn, if_exists="replace", index=False)
    customers.to_sql("customers", conn, if_exists="replace", index=False)
    products.to_sql("products", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Loaded fact_sales, orders, customers, products into {DB_PATH}")
