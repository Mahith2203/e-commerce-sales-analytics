# Business Insights Report — E-Commerce Sales Analytics

**Period analyzed:** Jan 2023 – Dec 2024
**Total revenue:** ₹122,356,990 | **Total profit:** ₹39,820,108 | **Overall margin:** 32.5%

---

## 1. Customer Value is Concentrated — Retention Strategy Should Follow

| Segment | Customers | Revenue | % of Revenue |
|---|---|---|---|
| Champions | 715 | ₹58,830,268 | 48.1% |
| Loyal | 1,143 | ₹47,768,169 | 39.0% |
| At Risk | 631 | ₹13,004,336 | 10.6% |
| Dormant / Churned | 424 | ₹2,754,216 | 2.3% |

**Finding:** 62% of customers (Champions + Loyal) generate 87% of revenue.

**Recommendation:** Reallocate retention marketing budget away from broad win-back campaigns
(targeting Dormant customers, who represent only 2.3% of revenue potential) and toward
loyalty perks / early access for the **Loyal** segment — they are the cheapest segment to move
up the value ladder and carry the largest revenue upside per customer converted.

---

## 2. Category Performance — Volume Leader vs. Margin Leader

| Category | Revenue | Avg Margin % |
|---|---|---|
| Electronics | ₹87,574,057 | 32.82% |
| Sports & Outdoors | ₹12,760,963 | 31.82% |
| Home & Kitchen | ₹8,983,239 | 30.65% |
| Fashion | ₹4,493,589 | **35.42%** |
| Beauty & Personal Care | ₹2,978,649 | 29.49% |
| Toys | ₹2,695,127 | 31.55% |
| Books | ₹1,583,799 | 31.56% |
| Grocery | ₹1,287,567 | 33.10% |

**Finding:** Electronics is the clear volume/revenue leader (72% of total revenue) but its margin
is unremarkable. Fashion has the smallest revenue base but the best margin in the catalog.

**Recommendation:** Two parallel plays — (a) protect Electronics volume since it's the revenue
engine, and (b) run a deliberate growth experiment on Fashion (bundling, ad spend, homepage
placement) since each rupee of incremental Fashion revenue converts to more profit than
almost any other category.

---

## 3. Regional Cancellations Are Not Explained by Delivery Speed

| Region | Orders | Avg Delivery Days | Cancellation Rate |
|---|---|---|---|
| West | 2,939 | 7.0 | 14.15% |
| North | 2,642 | 7.0 | 14.69% |
| South | 2,388 | 7.0 | 13.48% |
| East | 2,150 | 7.0 | 12.56% |
| Central | 1,795 | 7.0 | 14.76% |

**Finding:** Delivery time is flat across regions, yet cancellation rate ranges from 12.6% to
14.8%. If delivery speed were the cause, we'd expect the fastest region to also have the
lowest cancellation rate — it doesn't consistently.

**Recommendation:** Don't spend logistics budget assuming courier speed is the fix. Instead,
run a regional survey or funnel-drop analysis (where in checkout are Central/North customers
dropping off?) to find the actual driver before allocating budget.

---

## 4. Seasonality: Plan Inventory Around a Nov Dip / Dec Rebound

| Month | Revenue | MoM Growth |
|---|---|---|
| 2023-11 | ₹4,460,451 | −21.1% |
| 2023-12 | ₹5,598,077 | **+25.5%** |
| 2024-10 | ₹4,258,181 | −11.6% |
| 2024-11 | ₹4,710,110 | +10.6% |
| 2024-12 | ₹5,654,085 | **+20.0%** |

**Finding:** Both years show softness heading into November followed by a strong December —
consistent with a holiday/year-end shopping effect.

**Recommendation:** Pre-build inventory and marketing calendars for a December push rather than
reacting to it; consider whether October/November softness is worth countering with a
mid-quarter promotion to smooth revenue rather than concentrating it in December.

---

## 5. Payment Method Is Not a Useful Cancellation Predictor (Here)

| Payment Type | Orders | Cancellation Rate |
|---|---|---|
| UPI | 2,354 | 21.37% |
| Credit Card | 4,783 | 21.30% |
| Debit Card | 3,072 | 21.29% |
| Net Banking | 1,206 | 20.07% |
| COD | 585 | 18.63% |

**Finding:** All payment methods cluster within ~3 points of each other — this is noise, not signal.

**Recommendation:** Do not build a payment-method-specific intervention off this data. Flag it
as a hypothesis to re-test once real transactional data (with true payment-failure reasons) is
available, rather than acting on a spurious pattern.

---

## Methodology Note

All figures above are cross-validated two ways: once via the SQL queries in
`sql/analysis_queries.sql` (run against `sql/ecommerce.db`) and once via the pandas pipeline in
`analysis/04_eda_analysis.py`. Both produced matching numbers, which is a basic but important
sanity check before presenting findings to stakeholders.
