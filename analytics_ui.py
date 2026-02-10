import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from queries import fetch_all_receipts
from config import CURRENCY_SYMBOL
from insights import generate_ai_insights
from forecasting import (
    calculate_moving_averages,
    predict_next_month_spending,
    predict_spending_polynomial
)
from advanced_analytics import (
    detect_subscriptions,
    calculate_burn_rate
)

# ================= PLOTLY THEME DEFAULTS =================
PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", color="#334155"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=24, t=48, b=40),
    title_font=dict(size=16, color="#1e293b"),
    legend=dict(
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#e2e8f0",
        borderwidth=1,
        font=dict(size=12),
    ),
    xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0"),
    yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0"),
)

CHART_COLORS = ["#3b82f6", "#06b6d4", "#8b5cf6", "#f59e0b", "#ef4444", "#10b981", "#ec4899"]


def _section_header(title: str, subtitle: str = ""):
    """Render a styled section heading inside the main area."""
    html = f'<h3 style="margin:0 0 0.15rem 0;color:#1e293b;font-weight:700;font-size:1.1rem;">{title}</h3>'
    if subtitle:
        html += f'<p style="margin:0 0 0.75rem 0;color:#64748b;font-size:0.82rem;">{subtitle}</p>'
    st.markdown(html, unsafe_allow_html=True)


def _card_open():
    """Open a styled card wrapper."""
    st.markdown(
        '<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;'
        'padding:1.25rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,0.04);margin-bottom:1rem;">',
        unsafe_allow_html=True,
    )


def _card_close():
    st.markdown("</div>", unsafe_allow_html=True)


# ================= MAIN RENDER =================
def render_analytics():

    # ---------- Page-level CSS additions for this view ----------
    st.markdown("""
    <style>
        /* Nested tabs inside analytics (sub-tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.15rem;
        }

        /* Progress bar styling */
        .stProgress > div > div {
            border-radius: 8px;
            height: 8px;
        }
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #3b82f6, #06b6d4);
            border-radius: 8px;
        }

        /* Number input refinement */
        .stNumberInput > div > div > input {
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }
        .stNumberInput > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
        }

        /* Date input */
        .stDateInput > div > div > input {
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }

        /* Download button */
        .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 600;
            border: 1px solid #e2e8f0;
            transition: all 0.2s ease;
        }
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
    </style>
    """, unsafe_allow_html=True)

    # ---------- Header ----------
    st.markdown(
        '<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">'
        '<span style="font-size:1.5rem;line-height:1;">📈</span>'
        '<span style="font-size:1.35rem;font-weight:700;color:#1e293b;letter-spacing:-0.025em;">'
        'Spending Analytics & Intelligence</span></div>'
        '<p style="color:#64748b;font-size:0.85rem;margin:0 0 1rem 0;">'
        'Track trends, forecast spending, and uncover insights from your receipts.</p>',
        unsafe_allow_html=True,
    )

    # ---------- Fetch Data ----------
    receipts = fetch_all_receipts()

    if not receipts:
        st.info("No receipts found. Upload some receipts to see analytics!")
        return

    df = pd.DataFrame(receipts)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")

    # ================================================================
    #  CONTROLS BAR  (replaces sidebar filters, budget, export)
    # ================================================================
    with st.expander("Filters, Budget & Export", expanded=True, icon="🎛️"):

        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1.5])

        # --- Date Range Filter ---
        with ctrl_col1:
            _section_header("Date Range")
            min_date = df["date"].min().date()
            max_date = df["date"].max().date()

            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed",
            )

        # --- Monthly Budget ---
        with ctrl_col2:
            _section_header("Monthly Budget")
            budget_input = st.number_input(
                "Set Limit",
                min_value=0.0,
                value=st.session_state.get("monthly_budget", 50000.0),
                step=1000.0,
                label_visibility="collapsed",
            )
            st.session_state["monthly_budget"] = budget_input

            current_month = datetime.now().strftime("%Y-%m")
            current_month_df = df[df["date"].dt.strftime("%Y-%m") == current_month]
            current_spend = current_month_df["amount"].sum()
            days_passed = datetime.now().day

            budget_stats = calculate_burn_rate(current_spend, budget_input, days_passed)

            if budget_stats:
                st.progress(
                    min(budget_stats["percent_used"] / 100, 1.0),
                    text=f"{budget_stats['percent_used']:.1f}% of {CURRENCY_SYMBOL}{budget_input:,.0f} used",
                )
                status_color = "#ef4444" if budget_stats["projected"] > budget_input else "#10b981"
                st.markdown(
                    f'<span style="font-size:0.8rem;color:{status_color};font-weight:600;">'
                    f'{budget_stats["status"]}</span>',
                    unsafe_allow_html=True,
                )
                if budget_stats["projected"] > budget_input:
                    st.caption(f"Projected: {CURRENCY_SYMBOL}{budget_stats['projected']:,.0f}")

        # --- Export ---
        with ctrl_col3:
            _section_header("Export")
            # apply date filter
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
                df_filtered = df.loc[mask]
            else:
                df_filtered = df.copy()

            csv = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                csv,
                "receipt_analytics.csv",
                "text/csv",
                use_container_width=True,
            )
            st.caption(f"{len(df_filtered)} receipts in selection")

    # Ensure df_filtered exists outside expander
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df.copy()

    # ================================================================
    #  KPIs
    # ================================================================
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    _section_header("Key Performance Indicators", "Summary metrics for the selected period")

    col1, col2, col3, col4 = st.columns(4)

    total_spending = df_filtered["amount"].sum()
    avg_transaction = df_filtered["amount"].mean() if not df_filtered.empty else 0
    transaction_count = len(df_filtered)

    if not df_filtered.empty:
        cat_group = df_filtered.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_cat = cat_group.index[0]
        top_cat_amt = cat_group.iloc[0]
    else:
        top_cat, top_cat_amt = "N/A", 0

    col1.metric("Total Spending", f"{CURRENCY_SYMBOL}{total_spending:,.2f}")
    col2.metric("Avg Transaction", f"{CURRENCY_SYMBOL}{avg_transaction:,.2f}")
    col3.metric("Receipts Scanned", transaction_count)
    col4.metric("Top Category", top_cat, f"{CURRENCY_SYMBOL}{top_cat_amt:,.2f}")

    st.divider()

    # ================================================================
    #  ANALYSIS TABS
    # ================================================================
    tab_trends, tab_cats, tab_vendors, tab_advanced, tab_ai = st.tabs([
        "Trends & Forecast",
        "Categories",
        "Vendors",
        "Strategies & Outliers",
        "AI Insights",
    ])

    # ================== Trends ==================
    with tab_trends:
        monthly_df = (
            df_filtered.set_index("date")
            .resample("M")["amount"]
            .sum()
            .reset_index()
        )

        fig_line = px.line(
            monthly_df,
            x="date",
            y="amount",
            markers=True,
            title="Monthly Spending Trend",
            color_discrete_sequence=[CHART_COLORS[0]],
        )

        poly_forecast = predict_spending_polynomial(df, degree=2)
        if poly_forecast is not None:
            fig_line.add_trace(go.Scatter(
                x=poly_forecast["date"],
                y=poly_forecast["predicted_amount"],
                mode="lines",
                name="AI Trend (Poly)",
                line=dict(dash="dash", color=CHART_COLORS[3]),
            ))

        fig_line.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
        _section_header("Moving Averages", "Daily spending vs 7-day rolling average")

        daily_spend, ma_7 = calculate_moving_averages(df_filtered, 7)

        fig_ma = go.Figure()
        fig_ma.add_trace(go.Scatter(
            x=daily_spend.index, y=daily_spend, name="Daily",
            line=dict(color=CHART_COLORS[1], width=1),
            fill="tozeroy", fillcolor="rgba(6,182,212,0.08)",
        ))
        fig_ma.add_trace(go.Scatter(
            x=ma_7.index, y=ma_7, name="7-Day Avg",
            line=dict(color=CHART_COLORS[0], width=2.5),
        ))
        fig_ma.update_layout(title="Daily Spend & Moving Average", **PLOTLY_LAYOUT)
        st.plotly_chart(fig_ma, use_container_width=True)

        predicted, avg = predict_next_month_spending(df)
        st.info(
            f"Predicted next month spend: "
            f"**{CURRENCY_SYMBOL}{predicted:,.2f}** "
            f"(Daily Avg: {CURRENCY_SYMBOL}{avg:,.2f})"
        )

    # ================== Categories ==================
    with tab_cats:
        cat_df = df_filtered.groupby("category")["amount"].sum().reset_index()

        col_a, col_b = st.columns(2)

        with col_a:
            _section_header("Spending by Category")
            fig_pie = px.pie(
                cat_df, values="amount", names="category", hole=0.45,
                color_discrete_sequence=CHART_COLORS,
            )
            fig_pie.update_layout(**PLOTLY_LAYOUT)
            fig_pie.update_traces(textinfo="percent+label", textposition="outside")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            _section_header("Category / Vendor Breakdown")
            fig_tree = px.treemap(
                df_filtered,
                path=[px.Constant("All"), "category", "vendor"],
                values="amount",
                color_discrete_sequence=CHART_COLORS,
            )
            fig_tree.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_tree, use_container_width=True)

    # ================== Vendors ==================
    with tab_vendors:
        vendor_df = (
            df_filtered.groupby("vendor")["amount"]
            .sum()
            .reset_index()
            .sort_values("amount")
        )

        top_10 = vendor_df.tail(10)

        _section_header("Top 10 Vendors by Spend")
        fig_bar = px.bar(
            top_10,
            x="amount",
            y="vendor",
            orientation="h",
            text_auto=True,
            color_discrete_sequence=[CHART_COLORS[0]],
        )
        fig_bar.update_traces(
            texttemplate="%{x:.2s}",
            textposition="outside",
            marker_line_width=0,
            marker_cornerradius=6,
        )
        fig_bar.update_layout(**PLOTLY_LAYOUT, title=None)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ================== Advanced ==================
    with tab_advanced:
        _section_header("Spending Distribution", "Outlier detection via box plot")
        fig_box = px.box(
            df_filtered, y="amount", points="all",
            color_discrete_sequence=[CHART_COLORS[2]],
        )
        fig_box.update_layout(**PLOTLY_LAYOUT, title=None)
        st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        _section_header("Recurring Subscriptions", "Auto-detected from transaction patterns")
        subs = detect_subscriptions(df)
        if not subs.empty:
            st.dataframe(subs, use_container_width=True)
        else:
            st.success("No recurring subscriptions detected.")

    # ================== AI ==================
    with tab_ai:
        _section_header("AI-Powered Insights", "Generate a comprehensive spending report using AI")
        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        if st.button("Generate AI Report", type="primary", use_container_width=False):
            with st.spinner("Analyzing your spending data..."):
                insight = generate_ai_insights(df_filtered)
                st.markdown(insight)
