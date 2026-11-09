"""
Customer Lifecycle and Revenue Intelligence System - Summary Report
This script loads the processed data and displays key findings
"""
import pandas as pd
import os

print("=" * 80)
print("CUSTOMER LIFECYCLE AND REVENUE INTELLIGENCE SYSTEM")
print("Summary Report")
print("=" * 80)
print()

# Load KPI Summary
print("📊 EXECUTIVE KPI SUMMARY")
print("-" * 80)
kpi = pd.read_csv("sql_exports/kpi_summary.csv")
print(kpi.to_string(index=False))
print()

# Load Monthly Revenue
print("📈 MONTHLY REVENUE TRENDS")
print("-" * 80)
monthly = pd.read_csv("sql_exports/monthly_revenue.csv")
print(monthly.head(10).to_string(index=False))
print(f"... showing first 10 of {len(monthly)} months")
print()

# Load Cohort Average Retention
print("📅 COHORT RETENTION CURVE")
print("-" * 80)
cohort_avg = pd.read_csv("sql_exports/cohort_avg_curve.csv")
print(cohort_avg.to_string(index=False))
print()

# Load RFM Segment Summary
print("👥 RFM CUSTOMER SEGMENTATION")
print("-" * 80)
rfm = pd.read_csv("sql_exports/rfm_segments.csv")
segment_summary = rfm.groupby('segment').agg({
    'customer_id': 'count',
    'lifetime_revenue': 'sum',
    'total_orders': 'mean',
    'days_since_last_purchase': 'mean'
}).round(2)
segment_summary.columns = ['Customer Count', 'Total Revenue', 'Avg Orders', 'Avg Days Since Last Purchase']
segment_summary = segment_summary.sort_values('Total Revenue', ascending=False)
print(segment_summary.to_string())
print()

# Load Country Revenue
print("🌍 TOP 10 COUNTRIES BY REVENUE")
print("-" * 80)
country = pd.read_csv("sql_exports/country_revenue.csv")
print(country.head(10).to_string(index=False))
print()

# Load Customer Frequency
print("🔄 CUSTOMER PURCHASE FREQUENCY DISTRIBUTION")
print("-" * 80)
frequency = pd.read_csv("sql_exports/customer_frequency.csv")
print(frequency.to_string(index=False))
print()

# Load New vs Returning
print("🆕 NEW VS RETURNING CUSTOMER REVENUE")
print("-" * 80)
new_return = pd.read_csv("sql_exports/new_vs_returning.csv")
summary = new_return.groupby('customer_type').agg({
    'customers': 'sum',
    'revenue': 'sum'
}).round(2)
summary['revenue_pct'] = (summary['revenue'] / summary['revenue'].sum() * 100).round(2)
print(summary.to_string())
print()

print("=" * 80)
print("✅ All processed data and visualizations are available in:")
print("   📁 data/ - Cleaned CSV files")
print("   📁 sql_exports/ - SQL analysis results")
print("   📁 outputs/ - Visualization charts (PNG)")
print("   📁 retail_analytics.db - SQLite database")
print("=" * 80)
print()
print("📋 To explore further:")
print("   1. Open the Jupyter notebook to see the data cleaning process")
print("   2. Use DBeaver to query retail_analytics.db")
print("   3. Open the Power BI dashboard (.pbix file) in Power BI Desktop")
print("   4. View the PDF export of the dashboard")
print("=" * 80)
