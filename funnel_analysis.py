"""
E-commerce Conversion Funnel Analysis
======================================
Covers all requirements from the project brief:
1. Define funnel stages (visit -> product_view -> add_to_cart -> purchase)
2. Analyze user drop-off at each stage
3. Calculate conversion rates between stages
4. Identify bottlenecks in the funnel
5. Suggest improvements to increase conversions
6. Visualize funnel using charts/dashboards
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#444444"
plt.rcParams["axes.labelcolor"] = "#222222"
plt.rcParams["text.color"] = "#222222"
plt.rcParams["xtick.color"] = "#333333"
plt.rcParams["ytick.color"] = "#333333"

# -------------------------------------------------------------------
# 1. LOAD DATA & DEFINE FUNNEL STAGES
# -------------------------------------------------------------------
df = pd.read_csv("ecommerce_funnel_data.csv")

STAGES = ["visit", "product_view", "add_to_cart", "purchase"]
STAGE_LABELS = ["Visit", "Product View", "Add to Cart", "Purchase"]

overall_counts = df[STAGES].sum()
print("=" * 60)
print("FUNNEL STAGE DEFINITION & OVERALL COUNTS")
print("=" * 60)
for stage, label in zip(STAGES, STAGE_LABELS):
    print(f"  {label:<15}: {overall_counts[stage]:,}")

# -------------------------------------------------------------------
# 2. DROP-OFF ANALYSIS AT EACH STAGE
# -------------------------------------------------------------------
drop_off = []
for i in range(len(STAGES) - 1):
    current = overall_counts[STAGES[i]]
    nxt = overall_counts[STAGES[i + 1]]
    dropped = current - nxt
    drop_pct = (dropped / current) * 100
    drop_off.append({
        "from_stage": STAGE_LABELS[i],
        "to_stage": STAGE_LABELS[i + 1],
        "users_entering": current,
        "users_continuing": nxt,
        "users_dropped": dropped,
        "drop_off_rate_pct": round(drop_pct, 2)
    })

drop_off_df = pd.DataFrame(drop_off)
print("\n" + "=" * 60)
print("DROP-OFF ANALYSIS")
print("=" * 60)
print(drop_off_df.to_string(index=False))

# -------------------------------------------------------------------
# 3. CONVERSION RATES BETWEEN STAGES (+ overall conversion)
# -------------------------------------------------------------------
conversion = []
for i in range(len(STAGES) - 1):
    current = overall_counts[STAGES[i]]
    nxt = overall_counts[STAGES[i + 1]]
    conv_pct = (nxt / current) * 100
    conversion.append({
        "step": f"{STAGE_LABELS[i]} -> {STAGE_LABELS[i+1]}",
        "conversion_rate_pct": round(conv_pct, 2)
    })

conversion_df = pd.DataFrame(conversion)
overall_conversion = (overall_counts["purchase"] / overall_counts["visit"]) * 100

print("\n" + "=" * 60)
print("STEP-BY-STEP CONVERSION RATES")
print("=" * 60)
print(conversion_df.to_string(index=False))
print(f"\nOverall conversion rate (Visit -> Purchase): {overall_conversion:.2f}%")

# -------------------------------------------------------------------
# 4. BOTTLENECK IDENTIFICATION
# -------------------------------------------------------------------
bottleneck_idx = drop_off_df["drop_off_rate_pct"].idxmax()
bottleneck = drop_off_df.iloc[bottleneck_idx]

print("\n" + "=" * 60)
print("BOTTLENECK IDENTIFICATION")
print("=" * 60)
print(f"Largest drop-off: {bottleneck['from_stage']} -> {bottleneck['to_stage']}")
print(f"  {bottleneck['drop_off_rate_pct']}% of users are lost at this step")
print(f"  ({bottleneck['users_dropped']:,.0f} users dropped out of {bottleneck['users_entering']:,.0f})")

# Segment-level bottleneck analysis: by device and traffic source
print("\n--- Bottleneck breakdown by DEVICE (Add to Cart -> Purchase) ---")
device_bottleneck = df.groupby("device").apply(
    lambda g: pd.Series({
        "add_to_cart": g["add_to_cart"].sum(),
        "purchase": g["purchase"].sum(),
        "conversion_pct": round((g["purchase"].sum() / g["add_to_cart"].sum()) * 100, 2)
        if g["add_to_cart"].sum() > 0 else 0
    }),
    include_groups=False
).sort_values("conversion_pct")
print(device_bottleneck.to_string())

print("\n--- Funnel performance by TRAFFIC SOURCE (Visit -> Purchase) ---")
source_perf = df.groupby("traffic_source").apply(
    lambda g: pd.Series({
        "visits": g["visit"].sum(),
        "purchases": g["purchase"].sum(),
        "overall_conversion_pct": round((g["purchase"].sum() / g["visit"].sum()) * 100, 2)
    }),
    include_groups=False
).sort_values("overall_conversion_pct", ascending=False)
print(source_perf.to_string())

# -------------------------------------------------------------------
# 5. SAVE SUMMARY TABLES FOR REPORT/DASHBOARD USE
# -------------------------------------------------------------------
drop_off_df.to_csv("drop_off_analysis.csv", index=False)
conversion_df.to_csv("conversion_rates.csv", index=False)
device_bottleneck.to_csv("device_bottleneck.csv")
source_perf.to_csv("traffic_source_performance.csv")

print("\nSummary CSVs saved: drop_off_analysis.csv, conversion_rates.csv, device_bottleneck.csv, traffic_source_performance.csv")

# -------------------------------------------------------------------
# 6. VISUALIZATIONS
# -------------------------------------------------------------------

# --- Chart 1: Funnel bar chart (classic funnel shape) ---
fig, ax = plt.subplots(figsize=(9, 6))
colors = ["#5B6EE8", "#7B61E0", "#A654D8", "#D1499E"]
bars = ax.barh(STAGE_LABELS[::-1], overall_counts[::-1], color=colors[::-1], height=0.6)

for bar, val in zip(bars, overall_counts[::-1]):
    pct_of_top = (val / overall_counts["visit"]) * 100
    ax.text(bar.get_width() + max(overall_counts) * 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:,}  ({pct_of_top:.1f}%)", va="center", fontsize=11, fontweight="bold")

ax.set_xlabel("Number of Users")
ax.set_title("E-commerce Conversion Funnel", fontsize=15, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("chart1_funnel_overview.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nSaved chart1_funnel_overview.png")

# --- Chart 2: Drop-off rate per step ---
fig, ax = plt.subplots(figsize=(9, 5.5))
steps = [f"{row['from_stage']}\n->\n{row['to_stage']}" for _, row in drop_off_df.iterrows()]
drop_rates = drop_off_df["drop_off_rate_pct"]
bar_colors = ["#D1499E" if v == drop_rates.max() else "#7B61E0" for v in drop_rates]
bars = ax.bar(steps, drop_rates, color=bar_colors, width=0.55)

for bar, val in zip(bars, drop_rates):
    ax.text(bar.get_x() + bar.get_width()/2, val + 1, f"{val:.1f}%",
            ha="center", fontsize=11, fontweight="bold")

ax.set_ylabel("Drop-off Rate (%)")
ax.set_title("Drop-off Rate at Each Funnel Step", fontsize=15, fontweight="bold", pad=15)
ax.set_ylim(0, max(drop_rates) + 18)
ax.spines[["top", "right"]].set_visible(False)
ax.annotate("Bottleneck", xy=(drop_rates.idxmax(), drop_rates.max() + 4.5),
            xytext=(drop_rates.idxmax(), drop_rates.max() + 14),
            ha="center", fontsize=10, color="#D1499E", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#D1499E", lw=1.5))
plt.tight_layout()
plt.savefig("chart2_dropoff_rates.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart2_dropoff_rates.png")

# --- Chart 3: Conversion by device (the bottleneck driver) ---
fig, ax = plt.subplots(figsize=(8, 5.5))
device_sorted = device_bottleneck.sort_values("conversion_pct")
bar_colors = ["#D1499E" if v == device_sorted["conversion_pct"].min() else "#5B6EE8"
              for v in device_sorted["conversion_pct"]]
bars = ax.bar(device_sorted.index, device_sorted["conversion_pct"], color=bar_colors, width=0.5)

for bar, val in zip(bars, device_sorted["conversion_pct"]):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.8, f"{val:.1f}%",
            ha="center", fontsize=11, fontweight="bold")

ax.set_ylabel("Cart -> Purchase Conversion Rate (%)")
ax.set_title("Checkout Conversion Rate by Device", fontsize=15, fontweight="bold", pad=15)
ax.set_ylim(0, max(device_sorted["conversion_pct"]) + 8)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("chart3_device_conversion.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart3_device_conversion.png")

# --- Chart 4: Overall conversion rate by traffic source ---
fig, ax = plt.subplots(figsize=(9, 5.5))
source_sorted = source_perf.sort_values("overall_conversion_pct")
bars = ax.barh(source_sorted.index, source_sorted["overall_conversion_pct"], color="#5B6EE8", height=0.55)

for bar, val in zip(bars, source_sorted["overall_conversion_pct"]):
    ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.2f}%",
            va="center", fontsize=10, fontweight="bold")

ax.set_xlabel("Overall Conversion Rate: Visit -> Purchase (%)")
ax.set_title("Overall Conversion Rate by Traffic Source", fontsize=15, fontweight="bold", pad=15)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("chart4_traffic_source_conversion.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart4_traffic_source_conversion.png")

print("\nAnalysis complete. All charts and summary tables generated.")
