import streamlit as st
from queries import clear_all_receipts

def render_sidebar():
    with st.sidebar:
        st.title("🧾 Receipt Vault")
        
        # --- API KEY INPUT ---
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Enter your Google Gemini API Key for AI features",
            key="gemini_api_key_input"
        )
        
        if api_key:
            st.session_state["GEMINI_API_KEY"] = api_key
            st.success("API Key set!")
        else:
            st.warning("Please enter API Key")

        st.divider()

        # --- NAVIGATION ---
        st.subheader("Navigation")
        page = st.radio(
            "Go to",
            ["Upload Receipt", "Validation", "Dashboard", "Analytics", "Chat with Data"],
            index=0
        )

        st.divider()

        # --- UTILS ---
        with st.expander("⚙️ Settings"):
            if st.button("🗑 Clear All Data", type="primary"):
                clear_all_receipts()
                st.toast("All receipts deleted!", icon="🗑")
                st.rerun()

        st.markdown("---")
        st.caption("v1.0 • Built with Streamlit & Gemini")
        
        return page