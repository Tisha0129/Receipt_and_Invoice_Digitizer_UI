from gemini_client import GeminiClient
import streamlit as st

def generate_ai_insights(df) -> str:
    """
    Generate natural language spending insights using Gemini.
    """
    api_key = st.session_state.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠ Gemini API Key not found. Please add it in the sidebar."

    try:
        client = GeminiClient(api_key)
        
        # optimized summary generation
        if df.empty:
            return "No data available for analysis."

        total_spend = df["amount"].sum()
        transaction_count = len(df)
        
        top_vendor = df.groupby("vendor")["amount"].sum().idxmax() if not df.empty else "N/A"
        top_category = df.groupby("category")["amount"].sum().idxmax() if "category" in df.columns else "N/A"
        
        # Get last 5 transactions for context
        recent_tx = df.sort_values("date", ascending=False).head(5)[["date", "vendor", "amount", "category"]].to_string(index=False)
        
        summary_str = f"""
        Dataset Summary:
        - Total Spending: ${total_spend:.2f}
        - Total Transactions: {transaction_count}
        - Top Vendor: {top_vendor}
        - Top Category: {top_category}
        - Date Range: {df["date"].min()} to {df["date"].max()}
        
        Recent Transactions:
        {recent_tx}
        """

        return client.generate_insights(summary_str)
    except Exception as e:
        return f"Error generating insights: {str(e)}"