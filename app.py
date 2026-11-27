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


def set_products(products):
    st.session_state.selected_products = list(products)


with st.sidebar:
    st.header("🌐 Connection Mode")
    conn_mode = st.radio(
        "Dashboard Location",
        ["Cloud Link (Tailscale)", "Local PC (127.0.0.1)"],
        index=1,
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

st.title("⚡ Malika Synthetic Edge: Crash & Boom Command")
st.caption("Separated Group SL Controls • Highest-Sense Pre-Spike Trigger • Abrupt Trend-Flip Quit Warning")

st.subheader("🎯 Select Boom & Crash Products to Hunt")

preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
with preset_col1:
    st.button(
        "1️⃣ Option 1: Boom 1000 Only",
        use_container_width=True,
        on_click=set_products,
        args=(["Boom 1000 Index"],),
    )
with preset_col2:
    st.button(
        "2️⃣ Option 2: Boom 1000 + Crash 1000",
        use_container_width=True,
        on_click=set_products,
        args=(["Boom 1000 Index", "Crash 1000 Index"],),
    )
with preset_col3:
    st.button(
        "🔥 All Booms (1000 / 500 / 300)",
        use_container_width=True,
        on_click=set_products,
        args=(["Boom 1000 Index", "Boom 500 Index", "Boom 300 Index"],),
    )
with preset_col4:
    st.button(
        "⚡ All 6 Booms & Crashes",
        use_container_width=True,
        on_click=set_products,
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

# Top row: Timeframe, Base Lot, and TP
p1, p2, p3 = st.columns(3)
with p1:
    timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "M30", "H1"], index=0)
with p2:
    lot_size = st.number_input("Base Lot Size (0.20 Group)", min_value=0.01, max_value=50.0, value=0.20, step=0.05)
with p3:
    tp_dollars = st.number_input("Manual TP ($)", min_value=0.00, max_value=1000.0, value=0.50, step=0.25)

manual_tp_enabled = st.checkbox(
    "Set TP Manually Across Selected Products (Off by default — entry only on MT5)",
    value=False,
)

# Separated SL Controls by Lot Group
st.markdown("#### 🛡️ Separated Stop-Loss Controls by Lot Group")
g1, g2 = st.columns(2)
with g1:
    with st.container(border=True):
        st.markdown("**Group A: Standard 0.20 Lot Group** (Boom/Crash 1000 & 500)")
        std_sl_dollars = st.number_input(
            "0.20 Group SL ($)",
            min_value=0.10,
            max_value=1000.0,
            value=2.00,
            step=0.50,
            key="std_sl_usd",
        )
        std_sl_enabled = st.checkbox(
            "Enable SL for 0.20 Group (Off by default — moves freely)",
            value=False,
            key="std_sl_chk",
        )

with g2:
    with st.container(border=True):
        st.markdown("**Group B: Higher Min-Lot Group** (Boom 300 & Crash 300)")
        alt_sl_dollars = st.number_input(
            "300s Group SL ($)",
            min_value=0.50,
            max_value=1000.0,
            value=5.00,
            step=0.50,
            key="alt_sl_usd",
        )
        alt_sl_enabled = st.checkbox(
            "Enable SL for 300s Group (Off by default — entry only on MT5)",
            value=False,
            key="alt_sl_chk",
        )

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
                    "std_sl_enabled": bool(std_sl_enabled),
                    "std_sl_dollars": float(std_sl_dollars),
                    "alt_sl_enabled": bool(alt_sl_enabled),
                    "alt_sl_dollars": float(alt_sl_dollars),
                    "manual_tp_enabled": bool(manual_tp_enabled),
                    "tp_dollars": float(tp_dollars),
                    "symbols": selected_products,
                    "timeframe": timeframe,
                    "lot": float(lot_size),
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
                    "std_sl_enabled": bool(std_sl_enabled),
                    "std_sl_dollars": float(std_sl_dollars),
                    "alt_sl_enabled": bool(alt_sl_enabled),
                    "alt_sl_dollars": float(alt_sl_dollars),
                    "manual_tp_enabled": bool(manual_tp_enabled),
                    "tp_dollars": float(tp_dollars),
                    "symbols": selected_products,
                    "timeframe": timeframe,
                    "lot": float(lot_size),
                },
                timeout=10,
            )
            if r.json().get("status") == "success":
                st.info("Switched to Manual Mode (Auto entries paused).")
        except Exception as e:
            st.error(f"Failed to update mode: {e}")

st.divider()

st.subheader(f"📡 Live MT5 Multi-Product Telemetry & {timeframe} Direction Analysis")
r1, r2 = st.columns([3, 1])
with r1:
    manual_sync = st.button("🔄 Sync Live Account, Multi-Product Direction & Tick Data", use_container_width=True)
with r2:
    refresh_choice = st.selectbox("Auto-Refresh", ["Off", "15s", "30s"], index=1, label_visibility="collapsed")

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
    # Abrupt Trend-Flip / "Quit Manually" Warning Window
    exit_warnings = status_data.get("exit_warnings", [])
    if exit_warnings:
        with st.container(border=True):
            st.error(
                "🚨 **TREND DIRECTION ABRUPTLY CHANGED — QUIT MANUALLY WINDOW:** "
                "The following setup was highly expected to spike, but direction flipped against it:"
            )
            for w in exit_warnings:
                wc1, wc2 = st.columns([3.5, 1])
                with wc1:
                    st.warning(
                        f"**#{w['ticket']} • {w['symbol']} ({w['side']} {w['lot']}):** {w['message']}"
                    )
                with wc2:
                    if st.button(
                        f"✂️ Quit {w['symbol'].replace(' Index', '')} Now",
                        key=f"quit_btn_{w['ticket']}",
                        use_container_width=True,
                    ):
                        res = requests.post(
                            f"{tunnel_url}/close_ticket",
                            json={"secret": bridge_secret, "ticket": int(w["ticket"])},
                            timeout=10,
                        ).json()
                        if res.get("status") == "success":
                            st.success(f"Closed #{w['ticket']} ({w['symbol']})!")
                            st.rerun()
                        else:
                            st.error(res.get("message", "Could not close ticket"))

    std_sl_txt = f"ON (${std_sl_dollars:.2f})" if status_data.get("std_sl_enabled") else "FREE (Entry Only)"
    alt_sl_txt = f"ON (${alt_sl_dollars:.2f})" if status_data.get("alt_sl_enabled") else "FREE (Entry Only)"
    tp_txt = f"ON (${tp_dollars:.2f})" if status_data.get("manual_tp_enabled") else "OFF (Entry Only)"

    if status_data.get("auto_mode"):
        st.success(
            f"🟢 **MODE: ALLOW AUTOMATICALLY** | Active: **{status_data.get('active_bot_trades_count', 0)}/{len(selected_products)}** "
            f"| 0.20 Group SL: **{std_sl_txt}** | 300s SL: **{alt_sl_txt}** | TP: **{tp_txt}**"
        )
    else:
        st.warning(
            f"🟡 **MODE: TRADE MANUALLY** | 0.20 Group SL: **{std_sl_txt}** "
            f"| 300s SL: **{alt_sl_txt}** | TP: **{tp_txt}**"
        )

    telemetry_map = status_data.get("symbol_telemetry", {})
    focus_sym = st.selectbox("Inspect Trend & RSI Focus Product", selected_products, index=0)
    focus_item = telemetry_map.get(focus_sym, {})
    focus_dir = focus_item.get("direction", "SIDEWAYS")
    focus_rsi = focus_item.get("rsi", "-")
    focus_env = focus_item.get("spike_environment", "-")
    focus_sig = focus_item.get("latest_signal", f"{focus_sym} [{timeframe}]")
    focus_conf = focus_item.get("confidence", "-")
    focus_pre = focus_item.get("pre_spike", "NONE")

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
        f"🎯 Spike Sense: **{focus_env}** | Pre-Spike Status: **{focus_pre}** | Confidence: **{focus_conf}**"
    )
    st.info(f"📢 **ANALYSIS STATUS:** {focus_sig}")

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Balance", f"${status_data.get('balance', 0):,.2f}")
    b2.metric("Equity", f"${status_data.get('equity', 0):,.2f}")
    b3.metric("Selected Products", f"{len(selected_products)}")
    b4.metric(
        "Active Bot Slots Used",
        f"{status_data.get('active_bot_trades_count', 0)} / {len(selected_products)}",
    )

    st.markdown("### 📊 Live Spike Scanner Across Selected Products")
    rows = []
    for sym in selected_products:
        item = telemetry_map.get(sym, {})
        rows.append({
            "Product": sym.replace(" Index", ""),
            "Group": item.get("lot_group", "-"),
            "Side": item.get("side", "-"),
            "Lot": item.get("effective_lot", lot_size),
            "Price": item.get("ask", 0.0) if "BOOM" in sym.upper() else item.get("bid", 0.0),
            "Trend": item.get("direction", "-"),
            "RSI": item.get("rsi", "-"),
            "Pre-Spike": item.get("pre_spike", "NONE"),
            "Radar": item.get("spike_environment", "-"),
            "Slot": f"{item.get('open_count', 0)}/1",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🚀 Manual Spike Execution & Quick Position Quit")
    mc1, mc2, mc3 = st.columns([2.2, 1.3, 1.1])
    with mc1:
        manual_sym = st.selectbox("Target Product for Manual Entry", selected_products, key="manual_target_sym")
    is_boom_manual = "BOOM" in manual_sym.upper()
    manual_action = "BUY" if is_boom_manual else "SELL"
    btn_label = f"🟢 BUY ENTRY ({manual_sym})" if is_boom_manual else f"🔴 SELL ENTRY ({manual_sym})"

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
                    "std_sl_enabled": bool(std_sl_enabled),
                    "std_sl_dollars": float(std_sl_dollars),
                    "alt_sl_enabled": bool(alt_sl_enabled),
                    "alt_sl_dollars": float(alt_sl_dollars),
                    "apply_manual_tp": bool(manual_tp_enabled),
                    "tp_dollars": float(tp_dollars),
                },
                timeout=10,
            ).json()
            if tr.get("status") == "success":
                st.success(f"Opened {manual_action} entry on {manual_sym} (Lot {tr.get('lot')}, Ticket {tr.get('ticket')})")
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

    t_col, s_col = st.columns(2)
    with t_col:
        st.markdown("### 📈 Active Bot Positions (Magic 998877)")
        open_trades = status_data.get("open_trades", [])
        if open_trades:
            st.dataframe(pd.DataFrame(open_trades), use_container_width=True, hide_index=True)
            q_cols = st.columns(min(len(open_trades), 3))
            for idx, pos in enumerate(open_trades):
                with q_cols[idx % len(q_cols)]:
                    if st.button(
                        f"✂️ Quit #{pos['Ticket']} ({pos['Symbol'].replace(' Index', '')} | ${pos['P/L ($)']})",
                        key=f"manual_quit_{pos['Ticket']}",
                        use_container_width=True,
                    ):
                        requests.post(
                            f"{tunnel_url}/close_ticket",
                            json={"secret": bridge_secret, "ticket": int(pos["Ticket"])},
                            timeout=10,
                        )
                        st.rerun()
        else:
            st.caption("No open positions under Magic 998877.")

    with s_col:
        st.markdown("### 📜 Recent Spike Signals & Quit Alerts")
        history = status_data.get("signal_history", [])
        if history:
            for line in history:
                st.text(line)
        else:
            st.caption("Signals and quit alerts will appear here.")

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
