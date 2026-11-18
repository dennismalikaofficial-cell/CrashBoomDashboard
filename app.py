import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Malika Synthetic Edge: Crash & Boom Command", page_icon="📈", layout="wide")

# --- HARDCODED PERMANENT TUNNEL URL ---
PERMANENT_TUNNEL_URL = "https://your-pc-name.your-tailnet.ts.net"  # Replace with your Tailscale Funnel URL

st.sidebar.header("🔐 MT5 Account Login")
account_mode = st.sidebar.radio("Account Environment", ["DEMO", "LIVE"], horizontal=True)

# Smart defaults based on selection
default_server = "Deriv-Demo" if account_mode == "DEMO" else "DerivSVG-Server"

mt5_login = st.sidebar.number_input("Account ID", value=41028777, step=1)
mt5_password = st.sidebar.text_input("MT5 Password", type="password")
mt5_server = st.sidebar.text_input("Server Name", value=default_server, help="e.g., Deriv-Demo or DerivSVG-Server / DerivSVG-Server-02")
secret_key = st.sidebar.text_input("Bridge Secret Key", value="dennis_secret_998877", type="password")

if st.sidebar.button(f"🔗 Connect to {account_mode} Account", use_container_width=True):
    try:
        res = requests.post(
            f"{PERMANENT_TUNNEL_URL}/login",
            json={
                "secret": secret_key,
                "login": int(mt5_login),
                "password": mt5_password,
                "account_type": account_mode,
                "server": mt5_server,
            },
            timeout=5,
        ).json()
        if res.get("status") == "success":
            st.sidebar.success(res.get("message"))
        else:
            st.sidebar.error(res.get("message"))
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")

st.title("⚡ Malika Synthetic Edge: Crash & Boom Command")
st.caption("Developed by Dennis Malika — Hybrid Automated & Manual Scalping Suite")

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    symbol = st.selectbox(
        "Select Synthetic Index",
        ["Boom 1000 Index", "Crash 1000 Index", "Boom 500 Index", "Crash 500 Index", "Step Index", "Volatility 75 Index"],
    )
with col2:
    lot_size = st.number_input("Lot Size", min_value=0.01, max_value=50.0, value=0.20, step=0.05)
with col3:
    sl_dollars = st.number_input("Stop Loss ($)", min_value=0.10, max_value=500.0, value=0.30, step=0.10)
with col4:
    tp_dollars = st.number_input("Take Profit ($)", min_value=0.10, max_value=500.0, value=0.50, step=0.10)

st.info(f"Active Mode: **{account_mode}** | Assigned Magic Number: **998877** (Python USD SL/TP Watcher Active)")

# --- Execution Mode Toggle Buttons ---
st.subheader("🎛️ Execution Mode Control")
mode_col1, mode_col2 = st.columns(2)

def update_mode(auto_flag: bool):
    try:
        res = requests.post(
            f"{PERMANENT_TUNNEL_URL}/set_mode",
            json={
                "secret": secret_key,
                "auto_mode": auto_flag,
                "symbol": symbol,
                "lot": lot_size,
                "sl_dollars": sl_dollars,
                "tp_dollars": tp_dollars,
            },
            timeout=5,
        ).json()
        if res.get("status") == "success":
            st.session_state["auto_mode"] = auto_flag
        else:
            st.error(res.get("message", "Failed to update mode"))
    except Exception as e:
        st.error(f"Bridge Error: {e}")

with mode_col1:
    if st.button("🤖 ALLOW AUTOMATICALLY", use_container_width=True, type="primary"):
        update_mode(True)

with mode_col2:
    if st.button("🖐️ TRADE MANUALLY", use_container_width=True):
        update_mode(False)

# --- Sync Telemetry & Live Signal Sprayer ---
st.divider()
st.subheader("📡 Live MT5 Telemetry & Signal Sprayer")

if st.button("🔄 Sync Live Account, Signals & Tick Data"):
    pass

try:
    resp = requests.get(
        f"{PERMANENT_TUNNEL_URL}/status",
        params={"secret": secret_key, "symbol": symbol},
        timeout=5,
    ).json()

    if resp.get("status") == "connected":
        st.sidebar.success(f"Connected: {resp['login']} ({resp['server']})")
        active_auto = resp.get("auto_mode", False)

        if active_auto:
            st.success("🟢 CURRENT MODE: **ALLOW AUTOMATICALLY** (Bot executes signals automatically)")
        else:
            st.warning("🟡 CURRENT MODE: **TRADE MANUALLY** (Bot sprays signals; you click Buy/Sell)")

        sig_text = resp.get("latest_signal", "SCANNING...")
        sig_action = resp.get("signal_action", "WAIT")
        if sig_action == "BUY":
            st.success(f"📣 LIVE SIGNAL: **{sig_text}**")
        elif sig_action == "SELL":
            st.error(f"📣 LIVE SIGNAL: **{sig_text}**")
        else:
            st.info(f"📣 MARKET STATUS: **{sig_text}**")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Balance", f"${resp['balance']:.2f}")
        m2.metric("Equity", f"${resp['equity']:.2f}")
        m3.metric(f"{symbol} Bid", f"{resp['bid']:.4f}")
        m4.metric(f"{symbol} Ask", f"{resp['ask']:.4f}")

        st.divider()
        st.subheader("🚀 Manual Scalp Execution")
        b1, b2, b3 = st.columns([2, 2, 1])

        with b1:
            if st.button("🟢 BUY SCALP", use_container_width=True):
                t_res = requests.post(
                    f"{PERMANENT_TUNNEL_URL}/trade",
                    json={
                        "secret": secret_key,
                        "symbol": symbol,
                        "action": "BUY",
                        "lot": lot_size,
                        "sl_dollars": sl_dollars,
                        "tp_dollars": tp_dollars,
                    },
                    timeout=6,
                ).json()
                if t_res.get("status") == "success":
                    st.success(f"✅ BUY Executed! Ticket #{t_res['ticket']} @ {t_res['price']:.4f}")
                else:
                    st.error(f"❌ Execution Failed: {t_res.get('message')}")

        with b2:
            if st.button("🔴 SELL SCALP", use_container_width=True):
                t_res = requests.post(
                    f"{PERMANENT_TUNNEL_URL}/trade",
                    json={
                        "secret": secret_key,
                        "symbol": symbol,
                        "action": "SELL",
                        "lot": lot_size,
                        "sl_dollars": sl_dollars,
                        "tp_dollars": tp_dollars,
                    },
                    timeout=6,
                ).json()
                if t_res.get("status") == "success":
                    st.success(f"✅ SELL Executed! Ticket #{t_res['ticket']} @ {t_res['price']:.4f}")
                else:
                    st.error(f"❌ Execution Failed: {t_res.get('message')}")

        with b3:
            if st.button("🛑 CLOSE ALL", use_container_width=True):
                c_res = requests.post(
                    f"{PERMANENT_TUNNEL_URL}/close_all",
                    json={"secret": secret_key},
                    timeout=5,
                ).json()
                st.info(f"Closed {c_res.get('closed', 0)} position(s).")

        col_pos, col_hist = st.columns(2)
        with col_pos:
            st.markdown("**📊 Active Manual/Bot Positions (Magic 998877)**")
            trades = resp.get("open_trades", [])
            if trades:
                st.dataframe(pd.DataFrame(trades), use_container_width=True, hide_index=True)
            else:
                st.caption("No open positions under Magic 998877.")

        with col_hist:
            st.markdown("**📜 Recent Sprayed Signals**")
            history = resp.get("signal_history", [])
            if history:
                for item in history:
                    st.code(item, language=None)
            else:
                st.caption("Signals will appear here as new M1 bars form.")
    else:
        st.sidebar.error(resp.get("message", "Connection error"))
except Exception as e:
    st.error(f"Could not reach PC bridge via Tailscale: {e}")
