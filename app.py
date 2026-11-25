import pandas as pd
import requests
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

if "selected_products" not in st.session_state:
    st.session_state.selected_products = ALL_PRODUCTS.copy()
if "pending_products" not in st.session_state:
    st.session_state.pending_products = None

if st.session_state.pending_products is not None:
    st.session_state.selected_products = list(st.session_state.pending_products)
    st.session_state.pending_products = None


def queue_products(products):
    st.session_state.pending_products = list(products)


# Sidebar: Connection Mode, Bridge & MT5 Credentials
with st.sidebar:
    st.header("🌐 Connection Mode")
    conn_mode = st.radio(
        "Dashboard Location",
        ["Cloud Link (Tailscale)", "Local PC (127.0.0.1)"],
        index=0,
    )
    default_url = (
        "http://127.0.0.1:8000"
        if conn_mode == "Local PC (127.0.0.1)"
        else "https://desktop-ai0n2q3.tailc88f10.ts.net"
    )
    tunnel_url = st.text_input("Bridge URL", value=default_url).rstrip("/")
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
st.caption("Multi-Product Precision Spike Exhaustion • Priority Ranker • 1 Active Trade Per Selected Product")

# Fetch status early so Top Priority Banner can display live scores
timeframe_preview = "M1"
status_data = None
try:
    resp = requests.get(
        f"{tunnel_url}/status",
        params={
            "secret": bridge_secret,
            "symbols": ",".join(st.session_state.selected_products or ALL_PRODUCTS),
            "timeframe": timeframe_preview,
        },
        timeout=10,
    )
    status_data = resp.json()
except Exception:
    status_data = None

telemetry_map = (status_data or {}).get("symbol_telemetry", {})
top_item = None
if telemetry_map:
    ranked_items = sorted(
        telemetry_map.values(),
        key=lambda x: x.get("score", 0),
        reverse=True,
    )
    if ranked_items:
        top_item = ranked_items[0]

# #1 Top Priority Product Banner (Single-Product Focus for Clean Records)
if top_item:
    top_sym = top_item.get("symbol", "Boom 1000 Index")
    top_score = top_item.get("score", 0)
    top_dir = top_item.get("direction", "SIDEWAYS")
    top_env = top_item.get("spike_environment", "-")
    p_col1, p_col2 = st.columns([3, 1.3])
    with p_col1:
        st.success(
            f"🥇 **#1 PRIORITY PRODUCT RIGHT NOW:** **{top_sym}** "
            f"(Quality Score: **{top_score}/100** • Trend: **{top_dir}** • Radar: **{top_env}**)"
        )
    with p_col2:
        st.write("")
        st.button(
            f"🎯 Lock to {top_sym.replace(' Index', '')} Only",
            use_container_width=True,
            on_click=queue_products,
            args=([top_sym],),
        )

# Product Selection Presets & Multi-Select Pills
st.subheader("🎯 Select Boom & Crash Products to Hunt")

preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
with preset_col1:
    st.button(
        "1️⃣ Option 1: Boom 1000 Only",
        use_container_width=True,
        on_click=queue_products,
        args=(["Boom 1000 Index"],),
    )
with preset_col2:
    st.button(
        "2️⃣ Option 2: Boom 1000 + Crash 1000",
        use_container_width=True,
        on_click=queue_products,
        args=(["Boom 1000 Index", "Crash 1000 Index"],),
    )
with preset_col3:
    st.button(
        "🔥 All Booms (1000 / 500 / 300)",
        use_container_width=True,
        on_click=queue_products,
        args=(["Boom 1000 Index", "Boom 500 Index", "Boom 300 Index"],),
    )
with preset_col4:
    st.button(
        "⚡ All 6 Booms & Crashes",
        use_container_width=True,
        on_click=queue_products,
        args=(ALL_PRODUCTS,),
    )

selected_products = st.multiselect(
    "Active Spike-Hunting Products (Add or remove any combination — max 1 trade per selected product):",
    options=ALL_PRODUCTS,
    key="selected_products",
)

if not selected_products:
    st.warning("Select at least 1 Boom or Crash product above.")
    selected_products = ["Boom 1000 Index"]

st.info(
    f"🛡️ **Risk & Capacity Rule:** **{len(selected_products)} product(s)** selected $\\rightarrow$ "
    f"Max **{len(selected_products)} concurrent trade(s)** total (**1 active trade per product**, "
    f"entering only after 4+ anti-spike drift ticks & momentum stall). Boom = **BUY only** | Crash = **SELL only**."
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
    tp_dollars = st.number_input("Take Profit ($) Per Trade", min_value=0.10, max_value=1000.0, value=0.50, step=0.25)

enable_auto_sl = st.checkbox(
    "Enable Automatic USD Stop-Loss Exit (Off by default — no auto SL battle; USD TP stays active)",
    value=False,
)

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
                    "auto_sl_enabled": bool(enable_auto_sl),
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
                    "auto_sl_enabled": bool(enable_auto_sl),
                    "symbols": selected_products,
                    "timeframe": timeframe,
                    "lot": float(lot_size),
                    "sl_dollars": float(sl_dollars),
                    "tp_dollars": float(tp_dollars),
                },
                timeout=10,
            )
            if r.json().get("status") == "success":
                st.info("Switched to Manual Mode (Auto entries paused; USD TP active).")
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
    status_data = None

if status_data and status_data.get("status") == "connected":
    auto_sl_status = "ON" if status_data.get("auto_sl_enabled", False) else "OFF (Manual SL)"
    if status_data.get("auto_mode"):
        st.success(
            f"🟢 **CURRENT MODE: ALLOW AUTOMATICALLY** — Scanning **{len(selected_products)}** product(s) "
            f"| Active Bot Trades: **{status_data.get('active_bot_trades_count', 0)} / {len(selected_products)} max** "
            f"| Auto SL: **{auto_sl_status}**"
        )
    else:
        st.warning(
            f"🟡 **CURRENT MODE: TRADE MANUALLY** — Scanner active; automatic entries paused "
            f"| Auto SL: **{auto_sl_status}**"
        )

    telemetry_map = status_data.get("symbol_telemetry", {})
    default_focus_idx = 0
    if top_item and top_item.get("symbol") in selected_products:
        default_focus_idx = selected_products.index(top_item.get("symbol"))

    focus_sym = st.selectbox("Inspect Trend & RSI Focus Product", selected_products, index=default_focus_idx)
    focus_item = telemetry_map.get(focus_sym, {})
    focus_dir = focus_item.get("direction", "SIDEWAYS")
    focus_rsi = focus_item.get("rsi", "-")
    focus_env = focus_item.get("spike_environment", "-")
    focus_sig = focus_item.get("latest_signal", f"{focus_sym} [{timeframe}]")
    focus_entry = focus_item.get("rec_entry", 0.0)
    focus_sl = focus_item.get("rec_sl", 0.0)
    focus_tp = focus_item.get("rec_tp", 0.0)
    focus_conf = focus_item.get("confidence", "-")
    focus_score = focus_item.get("score", 0)

    trend_badge = (
        "📈 UPTREND"
        if focus_dir == "UPTREND"
        else ("📉 DOWNTREND" if focus_dir == "DOWNTREND" else "↔️ SIDEWAYS")
    )

    d1, d2 = st.columns(2)
    with d1:
        st.caption(f"{timeframe} Market Direction ({focus_sym})")
        st.markdown(f"## {trend_badge}")
    with d2:
        st.caption(f"RSI (14) — {focus_sym}")
        st.markdown(f"## {focus_rsi}")

    st.caption(
        f"🎯 Spike Environment: **{focus_env}** | Setup Confidence: **{focus_conf}** | "
        f"Priority Score: **{focus_score}/100**"
    )
    st.info(f"📢 **ANALYSIS STATUS:** {focus_sig}")

    # Manual Recommended Entry, SL & TP Readout
    rec1, rec2, rec3 = st.columns(3)
    rec1.metric("Manual Rec Entry", f"{focus_entry}")
    rec2.metric("Manual Rec SL", f"{focus_sl}")
    rec3.metric("Manual Rec TP", f"{focus_tp}")

    # Account Metrics
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Balance", f"${status_data.get('balance', 0):,.2f}")
    b2.metric("Equity", f"${status_data.get('equity', 0):,.2f}")
    b3.metric("Selected Products", f"{len(selected_products)}")
    b4.metric(
        "Active Bot Slots Used",
        f"{status_data.get('active_bot_trades_count', 0)} / {len(selected_products)}",
    )

    # Compact Multi-Product Live Scanner Table (sorted by Priority Score)
    st.markdown("### 📊 Live Spike Scanner (Ranked by Setup Priority Score)")
    rows = []
    for sym in ALL_PRODUCTS:
        item = telemetry_map.get(sym, {})
        rows.append({
            "Score": item.get("score", 0),
            "Product": sym.replace(" Index", ""),
            "Active": "✅" if sym in selected_products else "—",
            "Side": item.get("side", "-"),
            "Price": item.get("ask", 0.0) if "BOOM" in sym.upper() else item.get("bid", 0.0),
            "Trend": item.get("direction", "-"),
            "RSI": item.get("rsi", "-"),
            "Rec Entry": item.get("rec_entry", 0.0),
            "Rec SL": item.get("rec_sl", 0.0),
            "Rec TP": item.get("rec_tp", 0.0),
            "Radar": item.get("spike_environment", "-"),
            "Slot": f"{item.get('open_count', 0)}/1",
        })
    if rows:
        scanner_df = pd.DataFrame(rows).sort_values(by="Score", ascending=False)
        st.dataframe(scanner_df, use_container_width=True, hide_index=True)

    st.divider()

    # Manual Spike Execution for Any Selected Product
    st.subheader("🚀 Manual Spike Execution")
    mc1, mc2, mc3, mc4 = st.columns([2, 1, 1.3, 1])
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
                    "use_recommended_levels": False,
                },
                timeout=10,
            ).json()
            if tr.get("status") == "success":
                st.success(f"Opened {manual_action} on {manual_sym} (Ticket {tr.get('ticket')})")
            else:
                st.error(tr.get("message", "Order rejected"))

    with mc3:
        st.write("")
        if st.button("🎯 USE BOT REC ENTRY, SL & TP", use_container_width=True):
            tr = requests.post(
                f"{tunnel_url}/trade",
                json={
                    "secret": bridge_secret,
                    "symbol": manual_sym,
                    "action": manual_action,
                    "lot": float(lot_size),
                    "sl_dollars": float(sl_dollars),
                    "tp_dollars": float(tp_dollars),
                    "use_recommended_levels": True,
                },
                timeout=10,
            ).json()
            if tr.get("status") == "success":
                st.success(
                    f"Opened {manual_action} on {manual_sym} with Bot Rec SL/TP "
                    f"(Ticket {tr.get('ticket')})"
                )
            else:
                st.error(tr.get("message", "Order rejected"))

    with mc4:
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

    # Stage 1: 30-Day Proof Ledger
    st.divider()
    st.subheader("🏆 Stage 1: 30-Day Proof Ledger (Magic 998877)")
    journal = status_data.get("journal", [])
    if journal:
        j_df = pd.DataFrame(journal)
        j_df["Profit_USD"] = pd.to_numeric(j_df["Profit_USD"], errors="coerce").fillna(0.0)
        total_trades = len(j_df)
        wins = len(j_df[j_df["Profit_USD"] > 0])
        win_rate = round((wins / total_trades) * 100, 1) if total_trades > 0 else 0.0
        net_profit = round(float(j_df["Profit_USD"].sum()), 2)

        j1, j2, j3, j4 = st.columns(4)
        j1.metric("Logged Closed Trades", total_trades)
        j2.metric("Win Rate", f"{win_rate}%")
        j3.metric("Net Closed Profit", f"${net_profit:,.2f}")
        j4.download_button(
            "📥 Export CSV Proof",
            data=j_df.to_csv(index=False).encode("utf-8"),
            file_name="Malika_Stage1_30Day_Proof.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.dataframe(j_df.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.caption("Closed bot trades will automatically log here and save to trade_journal.csv.")
elif status_data:
    st.error(status_data.get("message", "MT5 terminal not connected"))
