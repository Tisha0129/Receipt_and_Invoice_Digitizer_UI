import streamlit as st
from analytics_ui import render_analytics

st.set_page_config(page_title="Analytics", layout="wide")

render_analytics()
