"""
app.py
------
STEP 5: INTERACTIVE DASHBOARD

A Streamlit dashboard for business stakeholders to explore sales performance
without touching SQL or Python. Filters by date range, region, and category;
shows KPIs, trend charts, category/regional breakdowns, and the RFM segment view.

Run locally:
    streamlit run dashboard/app.py

Deploy free on Streamlit Community Cloud by pointing it at this file in your
GitHub repo -- gives you a live demo link for your resume.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="E-Commerce Sales Analytics", layout="wide", page_icon="📊")


@st.cache_data
def load_data():
    fact = pd.read_csv("data/processed/fact_sales.csv", parse_dates=["order_date"])
    rfm = pd.read_csv("data/processed/rfm_segments.csv")
    return fact, rfm


fact, rfm = load_data()
sold = fact[fact["order_status"] != "canceled"].copy()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = sold["order_date"].min(), sold["order_date"].max()
date_range = st.sidebar.date_input("Order date range", (min_date, max_date), min_value=min_date, max_value=max_date)

regions = sorted(sold["region"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(sold["category"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask = (
        sold["order_date"].between(start, end)
        & sold["region"].isin(selected_regions)
        & sold["category"].isin(selected_categories)
    )
    filtered = sold[mask]
else:
    filtered = sold[sold["region"].isin(selected_regions) & sold["category"].isin(selected_categories)]

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
st.title("📊 E-Commerce Sales Analytics Dashboard")
st.caption("End-to-end sales performance, customer segmentation, and operational health")

col1, col2, col3, col4 = st.columns(4)
total_revenue = filtered["gross_revenue"].sum()
total_profit = filtered["profit"].sum()
num_orders = filtered["order_id"].nunique()
aov = total_revenue / num_orders if num_orders else 0

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Profit", f"₹{total_profit:,.0f}")
col3.metric("Orders", f"{num_orders:,}")
col4.metric("Avg Order Value", f"₹{aov:,.0f}")

st.divider()

# ---------------------------------------------------------------------------
# Revenue trend
# ---------------------------------------------------------------------------
st.subheader("Monthly Revenue & Profit Trend")
monthly = filtered.groupby("order_month").agg(
    revenue=("gross_revenue", "sum"), profit=("profit", "sum")
).reset_index().sort_values("order_month")
fig_trend = px.line(monthly, x="order_month", y=["revenue", "profit"], markers=True,
                     labels={"value": "₹", "order_month": "Month", "variable": "Metric"})
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------------------------------------------------
# Category + Region breakdown
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Revenue by Category")
    cat_rev = filtered.groupby("category")["gross_revenue"].sum().sort_values(ascending=False).reset_index()
    fig_cat = px.bar(cat_rev, x="gross_revenue", y="category", orientation="h",
                      labels={"gross_revenue": "Revenue (₹)", "category": ""})
    st.plotly_chart(fig_cat, use_container_width=True)

with c2:
    st.subheader("Revenue by Region")
    reg_rev = filtered.groupby("region")["gross_revenue"].sum().sort_values(ascending=False).reset_index()
    fig_reg = px.pie(reg_rev, names="region", values="gross_revenue", hole=0.4)
    st.plotly_chart(fig_reg, use_container_width=True)

# ---------------------------------------------------------------------------
# Operational health: delivery + cancellations
# ---------------------------------------------------------------------------
st.subheader("Operational Health: Delivery Time & Cancellations by Region")
op = fact.groupby("region").agg(
    avg_delivery_days=("delivery_days", "mean"),
    cancellation_rate=("order_status", lambda x: (x == "canceled").mean() * 100),
).reset_index()
fig_op = px.scatter(op, x="avg_delivery_days", y="cancellation_rate", text="region", size="avg_delivery_days",
                     labels={"avg_delivery_days": "Avg Delivery Days", "cancellation_rate": "Cancellation Rate (%)"})
fig_op.update_traces(textposition="top center")
st.plotly_chart(fig_op, use_container_width=True)

# ---------------------------------------------------------------------------
# RFM segments
# ---------------------------------------------------------------------------
st.subheader("Customer Segments (RFM Analysis)")
seg_summary = rfm.groupby("segment").agg(
    customers=("customer_id", "count"), revenue=("monetary", "sum")
).reset_index().sort_values("revenue", ascending=False)

c3, c4 = st.columns([1, 1])
with c3:
    fig_seg = px.pie(seg_summary, names="segment", values="revenue", hole=0.4,
                      title="Revenue Share by Segment")
    st.plotly_chart(fig_seg, use_container_width=True)
with c4:
    st.dataframe(seg_summary.rename(columns={
        "segment": "Segment", "customers": "# Customers", "revenue": "Revenue (₹)"
    }), use_container_width=True, hide_index=True)

st.divider()
st.caption("Data: synthetic e-commerce dataset generated for portfolio purposes | "
           "Built with Streamlit + Plotly | See README.md for full pipeline and business recommendations")
