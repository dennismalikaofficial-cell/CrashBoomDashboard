import streamlit as st
import pandas as pd

# Safely handle MetaTrader5 import for Linux Cloud hosting
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# Page Configuration
st.set_page_config(
    page_title="Crash & Boom Signal Command Center",
    page_icon="📈",
    layout="wide"
)

MAGIC_NUMBER = 998877

st.title("⚡ Crash & Boom Manual-Hybrid Signal Dashboard")
st.markdown("---")

# Sidebar: MT5 Account Login Form
st.sidebar.header("🔐 MT5 Account Login")

if not MT5_AVAILABLE:
    st.sidebar.info("☁️ Running in Cloud Mode (MT5 terminal runs locally on Windows).")

with st.sidebar.form("mt5_login_form"):
    mt5_login = st.number_input("Account Login ID", min_value=1, step=1, value=12345678)
    mt5_password = st.text_input("Password", type="password")
    mt5_server = st.text_input("Broker Server", placeholder="e.g., Deriv-Demo")
    submit_login = st.form_submit_button("Connect & Login to MT5")

if submit_login:
    if not MT5_AVAILABLE:
        st.sidebar.warning("Direct MT5 login requires running on your local Windows PC or via a Cloud Bridge.")
    else:
        # Initialize and attempt login with provided credentials
        if not mt5.initialize(login=int(mt5_login), password=mt5_password, server=mt5_server):
            st.sidebar.error(f"Connection/Login Failed! Error: {mt5.last_error()}")
        else:
            account_info = mt5.account_info()
            if account_info is not None:
                st.sidebar.success(f"Logged in as {account_info.name}")
                st.sidebar.json({
                    "Login": account_info.login,
                    "Server": account_info.server,
                    "Balance": account_info.balance,
                    "Equity": account_info.equity
                })
            else:
                st.sidebar.warning("Initialized, but could not fetch account details.")

# Main Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Active Instrument Watchlist")
    symbols = ["Boom 1000 Index", "Crash 1000 Index", "Boom 500 Index", "Crash 500 Index"]
    selected_symbol = st.selectbox("Select Synthetic Index", symbols)

with col2:
    st.subheader("⚙️ Execution Parameters")
    lot_size = st.number_input("Lot Size", min_value=0.20, max_value=50.0, value=0.20, step=0.01)
    st.info(f"Assigned Magic Number: **{MAGIC_NUMBER}** (Isolated from automated EAs)")

st.markdown("---")
st.subheader("📊 Signal Feed & Execution Panel")
st.write("Waiting for market ticks and signal conditions...")

if st.button("Execute Manual Scalp Entry"):
    if not MT5_AVAILABLE:
        st.info("Cloud Trigger Queued: Waiting for local Windows MT5 bridge to pick up signal.")
    else:
        st.warning("Manual execution hook ready. Link order send function to MT5.")
