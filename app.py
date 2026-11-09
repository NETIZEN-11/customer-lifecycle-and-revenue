"""
Customer Lifecycle & Revenue Intelligence System
Interactive Analytical Dashboard (Streamlit)
Replicates and expands on the 4-page Power BI Dashboard and SQLite analytics layer.
"""
import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Customer Lifecycle & Revenue Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load cached CSV data
@st.cache_data
def load_csv_data():
    base_dir = "sql_exports"
    kpi = pd.read_csv(os.path.join(base_dir, "kpi_summary.csv"))
    monthly = pd.read_csv(os.path.join(base_dir, "monthly_revenue.csv"))
    new_vs_ret = pd.read_csv(os.path.join(base_dir, "new_vs_returning.csv"))
    cohort_ret = pd.read_csv(os.path.join(base_dir, "cohort_retention.csv"))
    cohort_avg = pd.read_csv(os.path.join(base_dir, "cohort_avg_curve.csv"))
    rfm = pd.read_csv(os.path.join(base_dir, "rfm_segments.csv"))
    freq = pd.read_csv(os.path.join(base_dir, "customer_frequency.csv"))
    country = pd.read_csv(os.path.join(base_dir, "country_revenue.csv"))
    products = pd.read_csv(os.path.join(base_dir, "product_performance.csv"))
    return kpi, monthly, new_vs_ret, cohort_ret, cohort_avg, rfm, freq, country, products

kpi, monthly, new_vs_ret, cohort_ret, cohort_avg, rfm, freq, country, products = load_csv_data()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=64)
st.sidebar.title("Intelligence System")
st.sidebar.markdown("**Customer Lifecycle & Revenue Analytics**")
st.sidebar.divider()

page = st.sidebar.radio(
    "Select Dashboard View:",
    [
        "1. Executive Overview",
        "2. Cohort Retention",
        "3. Customer Behavior",
        "4. RFM Segmentation",
        "5. Product & Geography",
        "6. Live SQL Console"
    ]
)

st.sidebar.divider()
st.sidebar.info("""
**Project Stack:**
- **Database:** SQLite (`retail_analytics.db`)
- **Data Size:** 1,067,371 raw → 790k cleaned rows
- **Period:** Dec 2009 – Dec 2011
- **Retailer:** UK Occasion Gift-ware
""")

# -------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if page == "1. Executive Overview":
    st.markdown('<div class="main-header">📊 Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Top-line business performance, revenue growth trends, and macroeconomic metrics</div>', unsafe_allow_html=True)

    # Top KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Revenue", f"£{kpi['total_revenue'].iloc[0]:,.2f}")
    with col2:
        st.metric("Total Orders", f"{kpi['total_orders'].iloc[0]:,}")
    with col3:
        st.metric("Total Customers", f"{kpi['total_customers'].iloc[0]:,}")
    with col4:
        st.metric("Avg Order Value", f"£{kpi['avg_order_value'].iloc[0]:.2f}")
    with col5:
        st.metric("Repeat Purchase Rate", f"{kpi['repeat_purchase_rate_pct'].iloc[0]:.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Year filter for monthly view
    monthly['year'] = monthly['period'].str.slice(0, 4)
    available_years = ["All"] + sorted(monthly['year'].unique().tolist())
    selected_year = st.selectbox("Filter Revenue Trends by Year:", available_years, index=0)

    filtered_monthly = monthly if selected_year == "All" else monthly[monthly['year'] == selected_year]

    # Revenue & AOV Combo Chart
    c1, c2 = st.columns([7, 3])

    with c1:
        st.subheader("Monthly Revenue & Average Order Value (AOV)")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=filtered_monthly['period'],
                y=filtered_monthly['total_revenue'],
                name="Total Revenue (£)",
                marker_color='#2563EB',
                opacity=0.85
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=filtered_monthly['period'],
                y=filtered_monthly['avg_order_value'],
                name="Avg Order Value (£)",
                mode="lines+markers",
                line=dict(color='#DC2626', width=2.5),
                marker=dict(size=6)
            ),
            secondary_y=True
        )
        fig.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_yaxes(title_text="Revenue (£)", secondary_y=False)
        fig.update_yaxes(title_text="AOV (£)", secondary_y=True)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("MoM Growth Status")
        growth_counts = filtered_monthly['growth_label'].value_counts().reset_index()
        growth_counts.columns = ['Status', 'Months']
        color_map = {
            "Strong Growth": "#10B981",
            "Growth": "#3B82F6",
            "Baseline": "#6B7280",
            "Decline": "#EF4444"
        }
        fig_donut = px.pie(
            growth_counts,
            names="Status",
            values="Months",
            hole=0.55,
            color="Status",
            color_discrete_map=color_map
        )
        fig_donut.update_layout(margin=dict(l=10, r=10, t=30, b=20))
        st.plotly_chart(fig_donut, width="stretch")

    # Monthly Summary Data Table
    with st.expander("📄 View Monthly Revenue Breakdown Table"):
        st.dataframe(
            filtered_monthly[['period', 'total_revenue', 'total_orders', 'total_customers', 'avg_order_value', 'mom_growth_pct', 'growth_label', 'cumulative_revenue']],
            width="stretch"
        )

# -------------------------------------------------------------
# PAGE 2: COHORT RETENTION
# -------------------------------------------------------------
elif page == "2. Cohort Retention":
    st.markdown('<div class="main-header">📅 Cohort Retention Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tracking customer retention decay over 12 months across acquisition cohorts</div>', unsafe_allow_html=True)

    # Average Retention Curve Chart
    c1, c2 = st.columns([7, 3])
    with c1:
        st.subheader("Average vs. Minimum Retention Curve (Months 0 - 12)")
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=cohort_avg['month_number'],
            y=cohort_avg['avg_retention_pct'],
            mode='lines+markers',
            name='Avg Retention %',
            line=dict(color='#2563EB', width=3),
            marker=dict(size=8)
        ))
        fig_curve.add_trace(go.Scatter(
            x=cohort_avg['month_number'],
            y=cohort_avg['min_retention_pct'],
            mode='lines+markers',
            name='Min Retention %',
            line=dict(color='#EF4444', dash='dot', width=2),
            marker=dict(size=6)
        ))
        fig_curve.add_trace(go.Scatter(
            x=cohort_avg['month_number'],
            y=cohort_avg['max_retention_pct'],
            mode='lines',
            name='Max Retention %',
            line=dict(color='#10B981', dash='dot', width=1.5)
        ))
        fig_curve.update_layout(
            xaxis_title="Month Number (Offset from Cohort Acquisition)",
            yaxis_title="Retention Rate (%)",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_curve, width="stretch")

    with c2:
        st.subheader("Key Retention Takeaways")
        st.markdown("""
        - **Month 1 Drop-off:** Retention sharply declines from **100%** at acquisition to **21.0%** in Month 1 (~79% churn immediately).
        - **Long-term Plateau:** Between Month 2 and Month 12, retention stabilizes in the **15% – 21%** corridor.
        - **Acquisition Seasonality:** Earlier cohorts (Dec 2009) maintain higher lifetime retention due to wholesale client concentration.
        """)
        st.image("outputs/cohort_retention_heatmap.png", caption="Python Heatmap Reference", width="stretch")

    # Interactive Pivot Heatmap
    st.subheader("Interactive Cohort Retention Matrix (%)")
    pivot_retention = cohort_ret.pivot(index='cohort_month', columns='month_number', values='retention_rate_pct')
    fig_heat = px.imshow(
        pivot_retention,
        labels=dict(x="Month Offset", y="Cohort Month", color="Retention %"),
        x=pivot_retention.columns,
        y=pivot_retention.index,
        color_continuous_scale="Blues",
        aspect="auto"
    )
    fig_heat.update_layout(margin=dict(l=30, r=30, t=20, b=20))
    st.plotly_chart(fig_heat, width="stretch")

# -------------------------------------------------------------
# PAGE 3: CUSTOMER BEHAVIOR
# -------------------------------------------------------------
elif page == "3. Customer Behavior":
    st.markdown('<div class="main-header">🔄 Customer Behavior & Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">New vs. Returning customers and purchase frequency distributions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Revenue Split: New vs Returning")
        new_ret_summary = new_vs_ret.groupby('customer_type')['revenue'].sum().reset_index()
        fig_pie = px.pie(
            new_ret_summary,
            names="customer_type",
            values="revenue",
            color="customer_type",
            color_discrete_map={"Returning": "#1E3A8A", "New": "#60A5FA"},
            hole=0.5
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, width="stretch")

    with col2:
        st.subheader("Purchase Frequency Distribution")
        fig_freq = px.bar(
            freq,
            x="frequency_bucket",
            y="customers",
            color="revenue_share_pct",
            color_continuous_scale="Purples",
            labels={"customers": "Customer Count", "frequency_bucket": "Frequency Bucket", "revenue_share_pct": "Rev Share %"},
            text="customers"
        )
        fig_freq.update_layout(xaxis_tickangle=-15, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_freq, width="stretch")

    # Monthly Trend of New vs Returning Revenue
    st.subheader("Monthly Revenue Contribution by Customer Type")
    fig_bar = px.bar(
        new_vs_ret,
        x="period",
        y="revenue",
        color="customer_type",
        barmode="stack",
        color_discrete_map={"Returning": "#2563EB", "New": "#93C5FD"},
        labels={"revenue": "Revenue (£)", "period": "Period"}
    )
    fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified")
    st.plotly_chart(fig_bar, width="stretch")

# -------------------------------------------------------------
# PAGE 4: RFM SEGMENTATION
# -------------------------------------------------------------
elif page == "4. RFM Segmentation":
    st.markdown('<div class="main-header">👥 RFM Customer Segmentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Recency, Frequency, and Monetary quintile classification across 5,864 customers</div>', unsafe_allow_html=True)

    # Segment Summary Table
    seg_summary = rfm.groupby('segment').agg(
        customers=('customer_id', 'count'),
        total_revenue=('lifetime_revenue', 'sum'),
        avg_ltv=('lifetime_revenue', 'mean'),
        avg_orders=('total_orders', 'mean'),
        avg_recency=('days_since_last_purchase', 'mean')
    ).round(2).sort_values('total_revenue', ascending=False).reset_index()

    # Top Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        at_risk_rev = seg_summary.loc[seg_summary['segment'] == 'At Risk', 'total_revenue'].iloc[0]
        st.metric("At Risk Revenue", f"£{at_risk_rev:,.2f}")
    with c2:
        loyal_rev = seg_summary.loc[seg_summary['segment'] == 'Loyal Customers', 'total_revenue'].iloc[0]
        st.metric("Loyal Customers Revenue", f"£{loyal_rev:,.2f}")
    with c3:
        champ_rev = seg_summary.loc[seg_summary['segment'] == 'Champions', 'total_revenue'].iloc[0]
        st.metric("Champions Revenue", f"£{champ_rev:,.2f}")
    with c4:
        total_cust = seg_summary['customers'].sum()
        st.metric("Total Scored Customers", f"{total_cust:,}")

    col1, col2 = st.columns([6, 4])
    with col1:
        st.subheader("Revenue by RFM Segment")
        fig_seg_rev = px.bar(
            seg_summary,
            x="total_revenue",
            y="segment",
            orientation="h",
            color="segment",
            labels={"total_revenue": "Total Lifetime Revenue (£)", "segment": "Segment"},
            text_auto='.2s'
        )
        fig_seg_rev.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_seg_rev, width="stretch")

    with col2:
        st.subheader("Customer Count by Segment")
        fig_seg_pie = px.pie(
            seg_summary,
            names="segment",
            values="customers",
            hole=0.4
        )
        fig_seg_pie.update_layout(margin=dict(l=10, r=10, t=20, b=20))
        st.plotly_chart(fig_seg_pie, width="stretch")

    # Scatter Plot
    st.subheader("RFM Landscape: Orders vs. Lifetime Revenue")
    sample_rfm = rfm.sample(min(1500, len(rfm)), random_state=42)
    fig_scatter = px.scatter(
        sample_rfm,
        x="total_orders",
        y="lifetime_revenue",
        color="segment",
        size="recency_days",
        hover_data=["customer_id", "country"],
        labels={"total_orders": "Total Orders (Frequency)", "lifetime_revenue": "Lifetime Revenue (£)", "recency_days": "Recency (Days)"},
        log_y=True,
        log_x=True
    )
    fig_scatter.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_scatter, width="stretch")

    # Segment Explorer Table
    st.subheader("Detailed Segment Performance Table")
    st.dataframe(seg_summary, width="stretch")

# -------------------------------------------------------------
# PAGE 5: PRODUCT & GEOGRAPHY
# -------------------------------------------------------------
elif page == "5. Product & Geography":
    st.markdown('<div class="main-header">🌍 Product & Geographic Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Country performance rankings and top revenue-generating products</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Countries by Revenue")
        top_countries = country.head(10)
        fig_c = px.bar(
            top_countries,
            x="total_revenue",
            y="country",
            orientation="h",
            color="total_revenue",
            color_continuous_scale="Blues",
            labels={"total_revenue": "Revenue (£)", "country": "Country"},
            text="revenue_share_pct"
        )
        fig_c.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_c.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_c, width="stretch")

    with col2:
        st.subheader("Top 10 Products by Revenue")
        top_prod = products.head(10)
        fig_p = px.bar(
            top_prod,
            x="total_revenue",
            y="description",
            orientation="h",
            color="total_revenue",
            color_continuous_scale="Viridis",
            labels={"total_revenue": "Revenue (£)", "description": "Product Description"}
        )
        fig_p.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_p, width="stretch")

    st.subheader("Top 200 Products Search & Explorer")
    st.dataframe(products, width="stretch")

# -------------------------------------------------------------
# PAGE 6: LIVE SQL CONSOLE
# -------------------------------------------------------------
elif page == "6. Live SQL Console":
    st.markdown('<div class="main-header">⚡ Live SQLite Analytical Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Execute live SQL queries directly against <code>retail_analytics.db</code></div>', unsafe_allow_html=True)

    db_file = "retail_analytics.db"
    if not os.path.exists(db_file) or os.path.getsize(db_file) < 1000:
        st.error("⚠️ `retail_analytics.db` is not initialized or still an LFS placeholder. Run `python build_database.py` first!")
    else:
        sample_queries = {
            "Total Revenue & Orders by Country": "SELECT country, COUNT(DISTINCT invoice) AS orders, ROUND(SUM(revenue), 2) AS revenue FROM transactions GROUP BY country ORDER BY revenue DESC LIMIT 10;",
            "Top 10 Highest Spending Customers": "SELECT customer_id, country, total_orders, ROUND(lifetime_revenue, 2) AS ltv FROM customers ORDER BY lifetime_revenue DESC LIMIT 10;",
            "Monthly Order Trend": "SELECT invoice_yearmonth, COUNT(DISTINCT invoice) AS orders, ROUND(SUM(revenue), 2) AS revenue FROM transactions GROUP BY invoice_yearmonth ORDER BY invoice_yearmonth LIMIT 12;",
            "Sample 10 Transactions": "SELECT invoice, stock_code, description, quantity, price, revenue, invoice_date_only, customer_id, country FROM transactions LIMIT 10;"
        }

        query_choice = st.selectbox("Choose a query template:", list(sample_queries.keys()))
        custom_query = st.text_area("SQL Query Editor:", value=sample_queries[query_choice], height=120)

        if st.button("▶️ Execute Query"):
            try:
                conn = sqlite3.connect(db_file)
                query_result = pd.read_sql_query(custom_query, conn)
                conn.close()
                st.success(f"Query returned {len(query_result):,} rows.")
                st.dataframe(query_result, width="stretch")
            except Exception as e:
                st.error(f"SQL Execution Error: {e}")

