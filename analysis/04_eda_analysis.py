"""
04_eda_analysis.py
-------------------
STEP 4: EXPLORATORY DATA ANALYSIS & INSIGHT GENERATION

Reads the cleaned fact table, runs the core business analyses (mirroring
the SQL queries so the two approaches cross-validate each other), saves
chart images to outputs/charts/, and prints a plain-English insights
summary that becomes the basis for outputs/insights_report.md.

Run:
    python analysis/04_eda_analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120

fact = pd.read_csv("data/processed/fact_sales.csv", parse_dates=["order_date"])
orders = pd.read_csv("data/processed/orders_clean.csv", parse_dates=["order_date"])

sold = fact[fact["order_status"] != "canceled"].copy()

CHART_DIR = "outputs/charts"


# ---------------------------------------------------------------------------
# 1. Monthly revenue trend
# ---------------------------------------------------------------------------
monthly = sold.groupby("order_month").agg(revenue=("gross_revenue", "sum")).reset_index()
plt.figure(figsize=(10, 5))
plt.plot(monthly["order_month"], monthly["revenue"], marker="o", color="#2C6E49")
plt.xticks(rotation=45, ha="right")
plt.title("Monthly Revenue Trend")
plt.ylabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/01_monthly_revenue.png")
plt.close()

# ---------------------------------------------------------------------------
# 2. Revenue by category
# ---------------------------------------------------------------------------
cat_rev = sold.groupby("category")["gross_revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(9, 5))
sns.barplot(x=cat_rev.values, y=cat_rev.index, palette="viridis")
plt.title("Revenue by Product Category")
plt.xlabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/02_revenue_by_category.png")
plt.close()

# ---------------------------------------------------------------------------
# 3. Regional performance: revenue vs delivery delay
# ---------------------------------------------------------------------------
region_rev = sold.groupby("region")["gross_revenue"].sum()
region_delay = orders.groupby("region")["delivery_days"].mean()
region_cancel = (
    orders.assign(is_cancel=orders["order_status"].eq("canceled"))
    .groupby("region")["is_cancel"].mean() * 100
)
region_df = pd.DataFrame({
    "revenue": region_rev, "avg_delivery_days": region_delay, "cancellation_rate_pct": region_cancel
}).sort_values("revenue", ascending=False)

fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()
region_df["revenue"].plot(kind="bar", ax=ax1, color="#4C72B0", alpha=0.8, position=1, width=0.35)
region_df["avg_delivery_days"].plot(kind="bar", ax=ax2, color="#C44E52", alpha=0.8, position=0, width=0.35)
ax1.set_ylabel("Revenue (₹)", color="#4C72B0")
ax2.set_ylabel("Avg Delivery Days", color="#C44E52")
plt.title("Regional Revenue vs. Avg Delivery Days")
fig.tight_layout()
plt.savefig(f"{CHART_DIR}/03_region_revenue_vs_delivery.png")
plt.close()

# ---------------------------------------------------------------------------
# 4. RFM customer segmentation
# ---------------------------------------------------------------------------
snapshot_date = sold["order_date"].max() + pd.Timedelta(days=1)
rfm = sold.groupby("customer_id").agg(
    recency=("order_date", lambda x: (snapshot_date - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("gross_revenue", "sum"),
).reset_index()

rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
rfm["rfm_total"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]


def segment(row):
    if row["rfm_total"] >= 10:
        return "Champions"
    elif row["rfm_total"] >= 7:
        return "Loyal"
    elif row["rfm_total"] >= 5:
        return "At Risk"
    else:
        return "Dormant / Churned"


rfm["segment"] = rfm.apply(segment, axis=1)
rfm.to_csv("data/processed/rfm_segments.csv", index=False)

seg_summary = rfm.groupby("segment").agg(
    customers=("customer_id", "count"), revenue=("monetary", "sum")
).reset_index()
seg_summary["pct_of_revenue"] = (seg_summary["revenue"] / seg_summary["revenue"].sum() * 100).round(1)

plt.figure(figsize=(7, 7))
plt.pie(seg_summary["revenue"], labels=seg_summary["segment"], autopct="%1.1f%%",
        colors=sns.color_palette("Set2"))
plt.title("Revenue Share by Customer Segment (RFM)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/04_rfm_segment_revenue_share.png")
plt.close()

# ---------------------------------------------------------------------------
# 5. Payment type vs cancellation rate
# ---------------------------------------------------------------------------
pay_cancel = (
    fact.assign(is_cancel=fact["order_status"].eq("canceled"))
    .groupby("payment_type")["is_cancel"].mean() * 100
).sort_values(ascending=False)
plt.figure(figsize=(8, 5))
sns.barplot(x=pay_cancel.values, y=pay_cancel.index, palette="rocket")
plt.title("Cancellation Rate by Payment Type")
plt.xlabel("Cancellation Rate (%)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/05_cancellation_by_payment.png")
plt.close()

# ---------------------------------------------------------------------------
# Console insight summary (feeds outputs/insights_report.md)
# ---------------------------------------------------------------------------
print("=" * 70)
print("KEY INSIGHTS")
print("=" * 70)

total_rev = sold["gross_revenue"].sum()
total_profit = sold["profit"].sum()
print(f"Total revenue: ₹{total_rev:,.0f} | Total profit: ₹{total_profit:,.0f} "
      f"| Overall margin: {total_profit/total_rev*100:.1f}%")

best_month, worst_month = monthly.loc[monthly["revenue"].idxmax()], monthly.loc[monthly["revenue"].idxmin()]
print(f"Best month: {best_month['order_month']} (₹{best_month['revenue']:,.0f}) | "
      f"Worst month: {worst_month['order_month']} (₹{worst_month['revenue']:,.0f})")

print(f"\nTop category by revenue: {cat_rev.index[0]} (₹{cat_rev.iloc[0]:,.0f})")

worst_region = region_df["avg_delivery_days"].idxmax()
print(f"\nSlowest region: {worst_region} — {region_df.loc[worst_region, 'avg_delivery_days']:.1f} avg delivery days, "
      f"{region_df.loc[worst_region, 'cancellation_rate_pct']:.1f}% cancellation rate")

print("\nRFM segment revenue concentration:")
print(seg_summary.sort_values("revenue", ascending=False).to_string(index=False))

worst_payment = pay_cancel.index[0]
print(f"\nRiskiest payment method: {worst_payment} — {pay_cancel.iloc[0]:.1f}% cancellation rate "
      f"vs {pay_cancel.mean():.1f}% average across all methods")

print("\nCharts saved to outputs/charts/")
