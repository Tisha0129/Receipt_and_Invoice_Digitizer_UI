# Receipt Vault Analyzer - Dashboard UI (Professional Theme)
import streamlit as st
import pandas as pd
from queries import fetch_all_receipts, delete_receipt
from config import CURRENCY_SYMBOL


# ================= STYLED SECTION HEADER =================
def _section_header(title, subtitle=""):
    """Render a professionally styled section header matching app.py theme."""
    sub_html = f'<p style="color:#64748b;font-size:0.9rem;margin:0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:1.25rem;">
        <h2 style="margin:0;font-family:'Inter','Segoe UI',sans-serif;font-weight:700;
                    color:#1e293b;letter-spacing:-0.03em;font-size:1.5rem;">
            {title}
        </h2>
        <div style="width:48px;height:3px;border-radius:2px;
                     background:linear-gradient(135deg,#3b82f6,#818cf8);margin-top:0.5rem;"></div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def _sub_header(title, subtitle=""):
    """Render a styled sub-header."""
    sub_html = f'<p style="color:#64748b;font-size:0.8rem;margin:0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
        <h3 style="margin:0;font-family:'Inter','Segoe UI',sans-serif;font-weight:600;
                    color:#334155;letter-spacing:-0.02em;font-size:1.15rem;">
            {title}
        </h3>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


# ================= CUSTOM METRIC CARD =================
def _metric_card(label, value, icon_svg, accent_color="#3b82f6"):
    """Render a custom metric card with icon, matching the app.py card style."""
    return f"""
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;
                padding:1.35rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,0.04);
                display:flex;align-items:center;gap:1rem;
                transition:all 0.2s ease;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;width:4px;height:100%;
                     background:{accent_color};border-radius:14px 0 0 14px;"></div>
        <div style="width:44px;height:44px;border-radius:12px;display:flex;
                     align-items:center;justify-content:center;flex-shrink:0;
                     background:{accent_color}10;">
            {icon_svg}
        </div>
        <div>
            <div style="font-size:0.7rem;font-weight:600;color:#64748b;
                         text-transform:uppercase;letter-spacing:0.08em;margin-bottom:2px;">
                {label}
            </div>
            <div style="font-size:1.45rem;font-weight:700;color:#1e293b;
                         font-family:'Inter','Segoe UI',sans-serif;letter-spacing:-0.02em;">
                {value}
            </div>
        </div>
    </div>
    """


# ================= EMPTY STATE =================
def _empty_state(message, sub_message=""):
    """Render a styled empty state card."""
    sub_html = f'<p style="color:#94a3b8;font-size:0.85rem;margin:0.5rem 0 0;">{sub_message}</p>' if sub_message else ""
    st.markdown(f"""
    <div style="border:2px dashed #cbd5e1;border-radius:14px;padding:3rem 2rem;
                text-align:center;background:#ffffff;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8"
             stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
             style="margin:0 auto 1rem;">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
        </svg>
        <p style="color:#64748b;font-weight:600;font-size:1rem;margin:0;">
            {message}
        </p>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


# ================= SVG ICONS =================
ICON_SPEND = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
ICON_TAX = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>'
ICON_RECEIPT = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'


# ================= DASHBOARD PAGE STYLES =================
DASHBOARD_CSS = """
<style>
    /* Delete button */
    .delete-btn-wrapper .stButton > button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        font-weight: 600;
    }
    .delete-btn-wrapper .stButton > button:hover {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }

    /* Filter panel */
    .filter-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem 1.5rem 0.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }

    .filter-panel-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Summary strip */
    .summary-strip {
        display: flex;
        align-items: center;
        gap: 1.25rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }

    .summary-strip-item {
        color: #cbd5e1;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .summary-strip-item strong {
        color: #f1f5f9;
        font-weight: 700;
    }

    .summary-strip-divider {
        width: 1px;
        height: 24px;
        background: #334155;
    }
</style>
"""


# ================= MAIN RENDER =================
def render_dashboard():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

    _section_header("Spending Dashboard", "Overview of your receipts and spending activity")

    # 1. Fetch Data
    receipts = fetch_all_receipts()

    if not receipts:
        _empty_state(
            "No receipts found",
            "Go to the Upload Receipt tab to add your first receipt."
        )
        return

    df = pd.DataFrame(receipts)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date", ascending=False)

    # 2. Key Metrics — custom cards
    total_spend = df["amount"].sum()
    total_tax = df["tax"].sum()
    total_receipts = len(df)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(_metric_card(
            "Total Spending",
            f"{CURRENCY_SYMBOL}{total_spend:,.2f}",
            ICON_SPEND,
            "#3b82f6"
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(_metric_card(
            "Total Tax Paid",
            f"{CURRENCY_SYMBOL}{total_tax:,.2f}",
            ICON_TAX,
            "#f59e0b"
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric_card(
            "Receipts Scanned",
            str(total_receipts),
            ICON_RECEIPT,
            "#10b981"
        ), unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # 3. Summary strip
    avg_spend = total_spend / total_receipts if total_receipts else 0
    date_range_start = df["date"].min().strftime("%b %d, %Y") if not df.empty else "—"
    date_range_end = df["date"].max().strftime("%b %d, %Y") if not df.empty else "—"

    st.markdown(f"""
    <div class="summary-strip">
        <div class="summary-strip-item">
            Avg. per Receipt: <strong>{CURRENCY_SYMBOL}{avg_spend:,.2f}</strong>
        </div>
        <div class="summary-strip-divider"></div>
        <div class="summary-strip-item">
            Date Range: <strong>{date_range_start}</strong> to <strong>{date_range_end}</strong>
        </div>
        <div class="summary-strip-divider"></div>
        <div class="summary-strip-item">
            Tax Rate (avg): <strong>{(total_tax / total_spend * 100) if total_spend else 0:.1f}%</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 4. Stored Receipts Table
    _sub_header("Stored Receipts", "Browse, filter, and manage your scanned receipts")

    # --- Filter Panel ---
    st.markdown("""
    <div class="filter-panel">
        <div class="filter-panel-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748b"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
            </svg>
            Filter Receipts
        </div>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        sb_bill = st.text_input("Bill ID", placeholder="Filter by ID...", label_visibility="collapsed",
                                key="dash_filter_bill")
    with f2:
        sb_vendor = st.text_input("Vendor", placeholder="Filter by vendor...", label_visibility="collapsed",
                                  key="dash_filter_vendor")
    with f3:
        sb_subtotal = st.text_input(f"Subtotal ({CURRENCY_SYMBOL})", placeholder="Filter by subtotal...",
                                    label_visibility="collapsed", key="dash_filter_subtotal")

    f4, f5, _ = st.columns(3)
    with f4:
        sb_tax = st.text_input(f"Tax ({CURRENCY_SYMBOL})", placeholder="Filter by tax...",
                               label_visibility="collapsed", key="dash_filter_tax")
    with f5:
        sb_amount = st.text_input(f"Total ({CURRENCY_SYMBOL})", placeholder="Filter by total...",
                                  label_visibility="collapsed", key="dash_filter_amount")

    if not df.empty:
        # Filtering Logic (unchanged)
        if sb_bill:
            df = df[df["bill_id"].str.lower().str.contains(sb_bill.lower(), na=False)]
        if sb_vendor:
            df = df[df["vendor"].str.lower().str.contains(sb_vendor.lower(), na=False)]
        if sb_subtotal:
            df = df[df["subtotal"].astype(str).str.contains(sb_subtotal, na=False)]
        if sb_tax:
            df = df[df["tax"].astype(str).str.contains(sb_tax, na=False)]
        if sb_amount:
            df = df[df["amount"].astype(str).str.contains(sb_amount, na=False)]

        # Results count badge
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="background:#eff6ff;color:#3b82f6;font-weight:600;font-size:0.75rem;
                         padding:0.25rem 0.65rem;border-radius:20px;border:1px solid #bfdbfe;">
                {len(df)} receipt{"s" if len(df) != 1 else ""} found
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Add selection column for deletion
        df_display = df.copy()
        df_display.insert(0, "Select", False)

        edited_df = st.data_editor(
            df_display,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Delete?",
                    help="Select receipts to delete",
                    default=False,
                ),
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "vendor": "Vendor",
                "bill_id": "Bill ID",
                "subtotal": st.column_config.NumberColumn(
                    f"Subtotal ({CURRENCY_SYMBOL})", format=f"{CURRENCY_SYMBOL}%.2f"
                ),
                "tax": st.column_config.NumberColumn(
                    f"Tax ({CURRENCY_SYMBOL})", format=f"{CURRENCY_SYMBOL}%.2f"
                ),
                "amount": st.column_config.NumberColumn(
                    f"Total ({CURRENCY_SYMBOL})", format=f"{CURRENCY_SYMBOL}%.2f"
                ),
            },
            disabled=["bill_id", "vendor", "date", "amount", "tax", "subtotal"],
            hide_index=True,
            use_container_width=True,
        )

        # Batch Delete
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="delete-btn-wrapper">', unsafe_allow_html=True)
        if st.button("Delete Selected Receipts", type="secondary", use_container_width=True,
                      key="dash_delete_btn"):
            to_delete = edited_df[edited_df["Select"] == True]
            if not to_delete.empty:
                for bid in to_delete["bill_id"]:
                    delete_receipt(bid)
                st.success(f"Successfully deleted {len(to_delete)} receipt(s)")
                st.rerun()
            else:
                st.warning("No receipts selected for deletion.")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        _empty_state("No receipts match your filters", "Try adjusting or clearing the filter fields above.")
