import streamlit as st
from database.db import init_db
from upload_ui import render_upload_ui
from dashboard_ui import render_dashboard
from validation_ui import validation_ui
from analytics_ui import render_analytics

# ================= CONFIG =================
st.set_page_config(
    page_title="Receipt Vault Analyzer",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= PROFESSIONAL CSS =================
st.markdown("""
<style>
    /* ===== HIDE DEFAULT SIDEBAR ===== */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* ===== GLOBAL RESETS & BASE ===== */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8fafc;
    }

    h1, h2, h3, h4, h5, h6 {
        letter-spacing: -0.025em;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ===== TOP NAVBAR ===== */
    .navbar-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 1rem 2.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -1rem -1rem 1.5rem -1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        position: sticky;
        top: 0;
        z-index: 999;
    }

    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 0.625rem;
    }

    .navbar-logo {
        font-size: 1.75rem;
        line-height: 1;
    }

    .navbar-title {
        font-size: 2.0rem;
        font-weight: 700;
        color: #f1f5f9;
        letter-spacing: -0.03em;
    }

    .navbar-title span {
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .navbar-subtitle {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 500;
        margin-top: 2px;
    }

    .navbar-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .navbar-badge {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        color: #38bdf8;
        padding: 0.3rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
/* allow navbar to expand */
.navbar-container {
    min-height: 250px !important;
    padding-top: 20px !important;
    padding-bottom: 20px !important;
}

/* VERY IMPORTANT — override streamlit block container */
.block-container {
    padding-top: 0rem !important;
}

    /* ===== TABS NAVIGATION ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #ffffff;
        padding: 0.375rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        color: #64748b;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        white-space: nowrap;
        border: none;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #1e293b;
        background: #f1f5f9;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ===== SETTINGS EXPANDER ===== */
    div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }

    div[data-testid="stExpander"] summary {
        font-weight: 600;
        color: #334155;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
    }

    /* ===== TEXT INPUTS ===== */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 0.6rem 1rem;
        transition: border-color 0.2s;
    }

    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        border-radius: 14px;
    }

    [data-testid="stFileUploader"] > div {
        border-radius: 14px;
        border: 2px dashed #cbd5e1;
        background: #ffffff;
        transition: all 0.2s ease;
    }

    [data-testid="stFileUploader"] > div:hover {
        border-color: #3b82f6;
        background: #f8fafc;
    }

    /* ===== SELECT BOXES ===== */
    .stSelectbox > div > div {
        border-radius: 10px;
    }

    /* ===== METRICS ===== */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricValue"] {
        font-weight: 700;
        color: #1e293b;
    }

    /* ===== DATAFRAMES ===== */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }

    /* ===== SUCCESS / WARNING / ERROR ALERTS ===== */
    .stAlert {
        border-radius: 12px;
        font-weight: 500;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 1.5rem 0;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }

    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }

    /* ===== FOOTER ===== */
    .app-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        padding: 2rem 0 1rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }

    .app-footer a {
        color: #3b82f6;
        text-decoration: none;
        font-weight: 600;
    }

    .app-footer a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# ================= INIT =================
if "init_done" not in st.session_state:
    init_db()
    st.session_state["init_done"] = True

# ================= NAVBAR COMPONENT =================
def render_navbar():
    st.markdown("""
    <div class="navbar-container">
        <div class="navbar-brand">
            <div>
                <div class="navbar-logo">🧾</div>
            </div>
            <div>
                <div class="navbar-title"><span>Receipt Vault</span> Analyzer</div>
                <div class="navbar-subtitle">Smart Receipt Management</div>
            </div>
        </div>
        
    </div>
    """, unsafe_allow_html=True)

# ================= MAIN LAYOUT =================
def main():
    # Top Navbar
    render_navbar()

    # Settings bar (API Key — moved from sidebar)
    with st.expander("Settings & API Configuration", expanded=False, icon="⚙️"):
        settings_col1, settings_col2 = st.columns([3, 1])
        with settings_col1:
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="Enter your API key (sk-...)",
                help="Your API key is stored only for the current session and is never persisted.",
                label_visibility="collapsed"
            )
        with settings_col2:
            if st.button("Save Key", use_container_width=True, type="primary"):
                if api_key:
                    st.session_state["api_key"] = api_key
                    st.success("API Key saved for this session.", icon="✅")
                else:
                    st.warning("Please enter a valid API key.", icon="⚠️")

        # Show current key status
        if st.session_state.get("api_key"):
            st.caption("✅ API key is configured for this session.")
        else:
            st.caption("⚠️ No API key configured. Some features may be unavailable.")

    # ===== HORIZONTAL TAB NAVIGATION (replaces sidebar) =====
    tab_upload, tab_validation, tab_dashboard, tab_analytics, tab_chat = st.tabs([
        "Upload Receipt",
        "Validation",
        "Dashboard",
        "Analytics",
        "Chat with Data",
    ])

    with tab_upload:
        st.markdown("<br>", unsafe_allow_html=True)
        render_upload_ui()

    with tab_validation:
        st.markdown("<br>", unsafe_allow_html=True)
        validation_ui()

    with tab_dashboard:
        st.markdown("<br>", unsafe_allow_html=True)
        render_dashboard()

    with tab_analytics:
        st.markdown("<br>", unsafe_allow_html=True)
        render_analytics()

    with tab_chat:
        st.markdown("<br>", unsafe_allow_html=True)
        from chat_ui import render_chat
        render_chat()

    # ===== FOOTER =====
    st.markdown("""
    <div class="app-footer">
        Built with Streamlit &middot; <strong>Receipt Vault Analyzer</strong> &middot; All rights reserved.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
