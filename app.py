import streamlit as st
import pandas as pd
import requests

# Safely handle MetaTrader5 import for Linux Cloud hosting
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

st.set_page_config(
    page_title="Crash & Boom Signal Command Center",
    page_icon="📈",
    layout="wide"
)

MAGIC_NUMBER = 998877

st.title("⚡ Crash & Boom Manual-Hybrid Signal Dashboard")
st.markdown("---")

# Sidebar: Cloud Bridge Configuration
st.sidebar.header("🌐 Cloud-to-PC Bridge")
bridge_url = st.sidebar.text_input("Ngrok Tunnel URL", placeholder="https://xxxx.ngrok-free.app").strip().rstrip("/")
bridge_secret = st.sidebar.text_input("Bridge Secret Key", value="dennis_secret_998877", type="password")

# Main Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Active Instrument Watchlist")
    symbols = ["Boom 1000 Index", "Crash 1000 Index", "Boom 500 Index", "Crash 500 Index", "Step Index", "Volatility 75 Index"]
    selected_symbol = st.selectbox("Select Synthetic Index", symbols)

with col2:
    st.subheader("⚙️ Scalp Risk Parameters")
    lot_size = st.number_input("Lot Size", min_value=0.01, max_value=50.0, value=0.20, step=0.01)
    c1, c2 = st.columns(2)
    sl_dollars = c1.number_input("Stop Loss ($)", min_value=0.05, max_value=50.0, value=0.30, step=0.05)
    tp_dollars = c2.number_input("Take Profit ($)", min_value=0.05, max_value=50.0, value=0.50, step=0.05)
    st.info(f"Assigned Magic Number: **{MAGIC_NUMBER}** (Isolated from automated EAs)")

# Live Bridge Telemetry
st.markdown("---")
st.subheader("📡 Live MT5 Terminal Telemetry")

if bridge_url:
    if st.button("🔄 Sync Live Account & Tick Data"):
        try:
            res = requests.get(
                f"{bridge_url}/status",
                params={"secret": bridge_secret, "symbol": selected_symbol},
                headers={"ngrok-skip-browser-warning": "true"},
                timeout=5
            ).json()

            if res.get("connected"):
                st.sidebar.success(f"Connected: {res['login']} ({res['server']})")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Balance", f"${res['balance']:.2f}")
                m2.metric("Equity", f"${res['equity']:.2f}")
                m3.metric(f"{selected_symbol} Bid", f"{res['bid']}")
                m4.metric(f"{selected_symbol} Ask", f"{res['ask']}")
            else:
                st.error(f"Bridge Error: {res}")
        except Exception as e:
            st.error(f"Could not reach Windows PC bridge: {e}")
else:
    st.info("Paste your active Ngrok URL in the left sidebar to link your local Windows MT5 terminal.")

# Execution Panel
st.markdown("---")
st.subheader("🚀 Manual Scalp Execution")

btn_col1, btn_col2 = st.columns(2)

def send_scalp_order(direction):
    if not bridge_url:
        st.warning("Enter your Ngrok URL in the sidebar first.")
        return
    try:
        payload = {
            "secret": bridge_secret,
            "symbol": selected_symbol,
            "action": direction,
            "lot": lot_size,
            "sl_dollars": sl_dollars,
            "tp_dollars": tp_dollars
        }
        res = requests.post(
            f"{bridge_url}/trade",
            json=payload,
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=5
        ).json()

        if res.get("status") == "success":
            st.success(f"✅ {direction} Executed! Ticket #{res['ticket']} @ {res['price']} | SL: {res['sl']} | TP: {res['tp']}")
        else:
            st.error(f"❌ Execution Failed: {res.get('message')}")
    except Exception as e:
        st.error(f"Connection Error: {e}")

if btn_col1.button("🟢 BUY SCALP", use_container_width=True):
    send_scalp_order("BUY")

if btn_col2.button("🔴 SELL SCALP", use_container_width=True):
    send_scalp_order("SELL")
