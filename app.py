import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Malika Synthetic Edge: Crash & Boom Command",
    page_icon="⚡",
    layout="wide",
)

ALL_PRODUCTS = [
    "Boom 1000 Index",
    "Boom 500 Index",
    "Boom 300 Index",
    "Crash 1000 Index",
    "Crash 500 Index",
    "Crash 300 Index",
]

# Sidebar: Bridge & MT5 Credentials
with st.sidebar:
    st.header("🌐 Cloud-to-PC Bridge")
    tunnel_url = st.text_input(
        "Tailscale / Tunnel URL",
        value="https://desktop-ai0n2q3.tailc88f10.ts.net",
    ).rstrip("/")
    bridge_secret = st.text_input(
        "Bridge Secret Key",
        value="dennis_secret_998877",
        type="password",
    )

    st.divider()
    st.header("🔐 MT5 Account Login")
    account_env = st.radio("Account Environment", ["DEMO", "LIVE"], horizontal=True)
    default_server = "Deriv-Demo" if account_env == "DEMO" else "Deriv-Server"
    account_id = st.number_input("Account ID", value=41028777, step=1)
    mt5_password = st.text_input("MT5 Password", type="password")
    server_name = st.text_input("Broker Server", value=default_server)
    save_login = st.checkbox("Remember Login on Local Bridge", value=True)

    if st.button("🔌 Connect / Save MT5 Login", use_container_width=True):
        try:
            r = requests.post(
                f"{tunnel_url}/login",
                json={
                    "secret": bridge_secret,
                    "login": int(account_id),
                    "password": mt5_password,
                    "account_type": account_env,
                    "server": server_name,
                    "save_login": save_login,
                },
                timeout=10,
            )
            data = r.json()
            if data.get("status") == "success":
                st.success(data.get("message"))
            else:
                st.error(data.get("message", "Login failed"))
        except Exception as e:
            st.error(f"Bridge unreachable: {e}")

# Main Header
st.title("⚡ Malika Synthetic Edge: Crash & Boom Command")
st.caption("Multi-Product Smart Spike-Hunting • 1 Active Trade Per Selected Product • Cloud Synced")

# Product Selection Presets & Multi-Select Pills
st.subheader("🎯 Select Boom & Crash Products to Hunt")

preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
if "selected_products" not in st.session_state:
    st.session_state.selected_products = ["Boom 1000 Index"]

with preset_col1:
    if st.button("1️⃣ Option 1: Boom 1000 Only", use_container_width=True):
        st.session_state.selected_products = ["Boom 1000 Index"]
with preset_col2:
    if st.button("2️⃣ Option 2: Boom 1000 + Crash 1000", use_container_width=True):
        st.session_state.selected_products = ["Boom 1000 Index", "Crash 1000 Index"]
with preset_col3:
    if st.button("🔥 All Booms (1000 / 500 / 300)", use_container_width=True):
        st.session_state.selected_products = ["Boom 1000 Index", "Boom 500 Index", "Boom 300 Index"]
with preset_col4:
    if st.button("⚡ All 6 Booms & Crashes", use_container_width=True):
        st.session_state.selected_products = ALL_PRODUCTS.copy()

selected_products = st.multiselect(
    "Active Spike-Hunting Products (Add or remove any combination — max 1 trade per selected product):",
    options=ALL_PRODUCTS,
    default=st.session_state.selected_products,
    key="selected_products",
)

if not selected_products:
    st.warning("Select at least 1 Boom or Crash product above.")
    selected_products = ["Boom 1000 Index"]

st.info(
    f"🛡️ **Risk & Capacity Rule:** **{len(selected_products)} product(s)** selected $\\rightarrow$ "
    f"Max **{len(selected_products)} concurrent trade(s)** total (**1 active trade per product**, "
    f"re-entering only when a fresh spike setup forms). Boom = **BUY only** | Crash = **SELL only**."
)

# Parameters Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "M30", "H1"], index=0)
with c2:
    lot_size = st.number_input("Lot Size (Per Trade)", min_value=0.01, max_value=50.0, value=0.20, step=0.05)
with c3:
    sl_dollars = st.number_input("Stop Loss ($) Per Trade", min_value=0.10, max_value=1000.0, value=2.00, step=0.50)
with c4:
    tp_dollars = st.number_input("Take Profit ($) Per Trade", min_value=0.10, max_value=1000.0, value=2.00, step=0.50)

# Execution Mode Control
st.subheader("🎛️ Execution Mode Control")
m1, m2 = st.columns(2)
with m1:
    if st.button("🤖 ALLOW AUTOMATICALLY", type="primary", use_container_width=True):
        try:
            r = requests.post(
                f"{tunnel_url}/set_mode",
                json={
                    "secret": bridge_secret,
                    "auto_mode": True,
                    "symbols": selected_products,
                    "timeframe": timeframe,
                    "lot": float(lot_size),
                    "sl_dollars": float(sl_dollars),
                    "tp_dollars": float(tp_dollars),
                },
                timeout=10,
            )
            if r.json().get("status") == "success":
                st.success(f"Auto-Mode ACTIVE across {len(selected_products)} product(s)!")
        except Exception as e:
            st.error(f"Failed to update mode: {e}")

with m2:
    if st.button("🖐️ TRADE MANUALLY", use_container_width=True):
        try:
            r = requests.post(
                f"{tunnel_url}/set_mode",
                json={
                    "secret": bridge_secret,
                    "auto_mode": False,
                    "symbols": selected_products,
                    "timeframe": timeframe,
                    "lot": float(lot_size),
                    "sl_dollars": float(sl_dollars),
                    "tp_dollars": float(tp_dollars),
                },
                timeout=10,
            )
            if r.json().get("status") == "success":
                st.info("Switched to Manual Mode (Auto entries paused; USD SL/TP still active).")
        except Exception as e:
            st.error(f"Failed to update mode: {e}")

st.divider()

# Telemetry & Refresh Controls
st.subheader(f"📡 Live MT5 Multi-Product Telemetry & {timeframe} Direction Analysis")
r1, r2 = st.columns([3, 1])
with r1:
    manual_sync = st.button("🔄 Sync Live Account, Multi-Product Direction & Tick Data", use_container_width=True)
with r2:
    refresh_choice = st.selectbox("Auto-Refresh", ["Off", "15s", "30s"], index=0, label_visibility="collapsed")

if refresh_choice == "15s":
    st_autorefresh(interval=15000, key="auto_refresh_15")
elif refresh_choice == "30s":
    st_autorefresh(interval=30000, key="auto_refresh_30")

status_data = None
try:
    resp = requests.get(
        f"{tunnel_url}/status",
        params={
            "secret": bridge_secret,
            "symbols": ",".join(selected_products),
            "timeframe": timeframe,
        },
        timeout=10,
    )
    status_data = resp.json()
except Exception as e:
    st.error(f"Could not reach local bridge at {tunnel_url}: {e}")

if status_data and status_data.get("status") == "connected":
    if status_data.get("auto_mode"):
        st.success(
            f"🟢 **CURRENT MODE: ALLOW AUTOMATICALLY** — Scanning **{len(selected_products)}** product(s) "
            f"| Active Bot Trades: **{status_data.get('active_bot_trades_count', 0)} / {len(selected_products)} max**"
        )
    else:
        st.warning("🟡 **CURRENT MODE: TRADE MANUALLY** — Scanner active; automatic entries paused.")

    telemetry_map = status_data.get("symbol_telemetry", {})
    focus_sym = st.selectbox("Inspect Trend & RSI Focus Product", selected_products, index=0)
    focus_item = telemetry_map.get(focus_sym, {})
    focus_dir = focus_item.get("direction", "SIDEWAYS")
    focus_rsi = focus_item.get("rsi", "-")
    focus_env = focus_item.get("spike_environment", "-")
    focus_sig = focus_item.get("latest_signal", f"{focus_sym} [{timeframe}]")

    trend_badge = "📈 UPTREND" if focus_dir == "UPTREND" else ("📉 DOWNTREND" if focus_dir == "DOWNTREND" else "↔️ SIDEWAYS")

    # Prominent Trend & RSI Readout Cards
    d1, d2 = st.columns(2)
    with d1:
        st.caption(f"{timeframe} Market Direction ({focus_sym})")
        st.markdown(f"## {trend_badge}")
    with d2:
        st.caption(f"RSI (14) — {focus_sym}")
        st.markdown(f"## {focus_rsi}")

    st.caption(f"🎯 Spike Environment: **{focus_env}**")
    st.info(f"📢 **ANALYSIS STATUS:** {focus_sig}")

    # Account Metrics
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Balance", f"${status_data.get('balance', 0):,.2f}")
    b2.metric("Equity", f"${status_data.get('equity', 0):,.2f}")
    b3.metric("Selected Products", f"{len(selected_products)}")
    b4.metric(
        "Active Bot Slots Used",
        f"{status_data.get('active_bot_trades_count', 0)} / {len(selected_products)}",
    )

    # Multi-Product Live Scanner Table
    st.markdown("### 📊 Live Spike Scanner Across Selected Products")
    rows = []
    for sym in selected_products:
        item = telemetry_map.get(sym, {})
        rows.append({
            "Product": sym,
            "Allowed Side": item.get("side", "-"),
            "Bid": item.get("bid", 0.0),
            "Ask": item.get("ask", 0.0),
            f"{timeframe} Trend": item.get("direction", "-"),
            "RSI (14)": item.get("rsi", "-"),
            "Spike Status": item.get("spike_environment", "-"),
            "Active Trade": f"{item.get('open_count', 0)} / 1",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()

    # Manual Spike Execution for Any Selected Product
    st.subheader("🚀 Manual Spike Execution")
    mc1, mc2, mc3 = st.columns([2, 1, 1])
    with mc1:
        manual_sym = st.selectbox("Target Product for Manual Entry", selected_products, key="manual_target_sym")
    is_boom_manual = "BOOM" in manual_sym.upper()
    manual_action = "BUY" if is_boom_manual else "SELL"
    btn_label = f"🟢 BUY SPIKE ({manual_sym})" if is_boom_manual else f"🔴 SELL SPIKE ({manual_sym})"

    with mc2:
        st.write("")
        if st.button(btn_label, use_container_width=True):
            tr = requests.post(
                f"{tunnel_url}/trade",
                json={
                    "secret": bridge_secret,
                    "symbol": manual_sym,
                    "action": manual_action,
                    "lot": float(lot_size),
                    "sl_dollars": float(sl_dollars),
                    "tp_dollars": float(tp_dollars),
                },
                timeout=10,
            ).json()
            if tr.get("status") == "success":
                st.success(f"Opened {manual_action} on {manual_sym} (Ticket {tr.get('ticket')})")
            else:
                st.error(tr.get("message", "Order rejected"))

    with mc3:
        st.write("")
        if st.button("🛑 CLOSE ALL BOT TRADES", use_container_width=True):
            cl = requests.post(
                f"{tunnel_url}/close_all",
                json={"secret": bridge_secret},
                timeout=10,
            ).json()
            st.info(f"Closed {cl.get('closed', 0)} bot position(s).")

    # Open Trades & Recent Signals
    t_col, s_col = st.columns(2)
    with t_col:
        st.markdown("### 📈 Active Bot Positions (Magic 998877)")
        open_trades = status_data.get("open_trades", [])
        if open_trades:
            st.dataframe(pd.DataFrame(open_trades), use_container_width=True, hide_index=True)
        else:
            st.caption("No open positions under Magic 998877.")

    with s_col:
        st.markdown("### 📜 Recent Spike Signals & Executions")
        history = status_data.get("signal_history", [])
        if history:
            for line in history:
                st.text(line)
        else:
            st.caption("Signals will appear here when valid spike setups form.")
elif status_data:
    st.error(status_data.get("message", "MT5 terminal not connected"))
