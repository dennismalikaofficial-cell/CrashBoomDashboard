import streamlit as st
import requests
import pandas as pd

DEFAULT_TUNNEL_URL = "https://desktop-ai0n2q3.tailc88f10.ts.net"
DEFAULT_SECRET = "dennis_secret_998877"
TIMEOUT_SEC = 15

st.set_page_config(
    page_title="Malika Synthetic Edge: Crash & Boom Command",
    page_icon="⚡",
    layout="wide",
)

# Initialize session defaults
if "saved_loaded" not in st.session_state:
    st.session_state["saved_loaded"] = False
if "login_id" not in st.session_state:
    st.session_state["login_id"] = 41028777
if "mt5_password" not in st.session_state:
    st.session_state["mt5_password"] = ""
if "account_type" not in st.session_state:
    st.session_state["account_type"] = "DEMO"
if "server_name" not in st.session_state:
    st.session_state["server_name"] = "Deriv-Demo"
if "secret_key" not in st.session_state:
    st.session_state["secret_key"] = DEFAULT_SECRET

# --- Sidebar: Bridge & Saved MT5 Account Login ---
st.sidebar.header("🌐 Cloud-to-PC Bridge")
tunnel_url = st.sidebar.text_input(
    "Tailscale / Tunnel URL",
    value=DEFAULT_TUNNEL_URL,
).rstrip("/")

secret_key = st.sidebar.text_input(
    "Bridge Secret Key",
    value=st.session_state["secret_key"],
    type="password",
)
st.session_state["secret_key"] = secret_key

# Fetch saved credentials once when bridge URL & secret are present
if tunnel_url and secret_key and not st.session_state["saved_loaded"]:
    try:
        s_resp = requests.get(
            f"{tunnel_url}/saved_login",
            params={"secret": secret_key},
            timeout=TIMEOUT_SEC,
        ).json()
        if s_resp.get("status") == "success" and s_resp.get("config"):
            cfg = s_resp["config"]
            if cfg.get("login"):
                st.session_state["login_id"] = int(cfg["login"])
            if cfg.get("password"):
                st.session_state["mt5_password"] = cfg["password"]
            if cfg.get("account_type"):
                st.session_state["account_type"] = cfg["account_type"]
            if cfg.get("server"):
                st.session_state["server_name"] = cfg["server"]
        st.session_state["saved_loaded"] = True
    except Exception:
        pass

st.sidebar.divider()
st.sidebar.header("🔐 MT5 Account Login")

account_type = st.sidebar.radio(
    "Account Environment",
    ["DEMO", "LIVE"],
    index=0 if st.session_state["account_type"] == "DEMO" else 1,
    horizontal=True,
)
login_id = st.sidebar.number_input(
    "Account ID",
    min_value=1,
    step=1,
    value=int(st.session_state["login_id"]),
)
mt5_password = st.sidebar.text_input(
    "MT5 Password",
    value=st.session_state["mt5_password"],
    type="password",
)
server_name = st.sidebar.text_input(
    "Server Name",
    value=st.session_state["server_name"],
)
save_login = st.sidebar.checkbox("Save / Remember Login Details", value=True)

if st.sidebar.button("🔗 Connect & Save Account", use_container_width=True, type="primary"):
    if not tunnel_url:
        st.sidebar.warning("Enter your Tunnel URL first.")
    else:
        try:
            l_res = requests.post(
                f"{tunnel_url}/login",
                json={
                    "secret": secret_key,
                    "login": int(login_id),
                    "password": mt5_password,
                    "account_type": account_type,
                    "server": server_name,
                    "save_login": save_login,
                },
                timeout=TIMEOUT_SEC,
            ).json()
            if l_res.get("status") == "success":
                st.session_state["login_id"] = int(login_id)
                st.session_state["mt5_password"] = mt5_password
                st.session_state["account_type"] = account_type
                st.session_state["server_name"] = server_name
                st.sidebar.success(l_res.get("message", "Connected!"))
            else:
                st.sidebar.error(l_res.get("message", "Login failed"))
        except Exception as e:
            st.sidebar.error(f"Login Bridge Error: {e}")

# --- Main Header & Controls ---
st.title("⚡ Malika Synthetic Edge: Crash & Boom Command")
st.caption("Smart Spike-Hunting Only • Timeframe Direction Analysis • Saved Credentials")

col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
with col1:
    symbol = st.selectbox(
        "Select Synthetic Index",
        [
            "Boom 1000 Index",
            "Crash 1000 Index",
            "Boom 500 Index",
            "Crash 500 Index",
            "Step Index",
            "Volatility 75 Index",
        ],
    )
with col2:
    timeframe = st.selectbox(
        "Timeframe",
        ["M1", "M5", "M15", "M30", "H1", "H4"],
        index=0,
    )
with col3:
    lot_size = st.number_input("Lot Size", min_value=0.01, max_value=50.0, value=0.20, step=0.05)
with col4:
    sl_dollars = st.number_input("Stop Loss ($)", min_value=0.10, max_value=500.0, value=1.50, step=0.10)
with col5:
    tp_dollars = st.number_input("Take Profit ($)", min_value=0.10, max_value=500.0, value=2.00, step=0.10)

is_boom = "BOOM" in symbol.upper()
is_crash = "CRASH" in symbol.upper()

if is_boom:
    st.info("🎯 **Boom Spike Mode:** Bot hunts **BUY** spike entries only — **SELL** (counter-spike) is blocked.")
elif is_crash:
    st.info("🎯 **Crash Spike Mode:** Bot hunts **SELL** spike entries only — **BUY** (counter-spike) is blocked.")
else:
    st.info("Assigned Magic Number: **998877** | Python USD SL/TP Watcher Active")

# --- Execution Mode Toggle Buttons ---
st.subheader("🎛️ Execution Mode Control")
mode_col1, mode_col2 = st.columns(2)


def update_mode(auto_flag: bool):
    if not tunnel_url:
        st.warning("Enter your Tunnel URL in the left sidebar first.")
        return
    try:
        res = requests.post(
            f"{tunnel_url}/set_mode",
            json={
                "secret": secret_key,
                "auto_mode": auto_flag,
                "symbol": symbol,
                "timeframe": timeframe,
                "lot": lot_size,
                "sl_dollars": sl_dollars,
                "tp_dollars": tp_dollars,
            },
            timeout=TIMEOUT_SEC,
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

# --- Sync Telemetry, Timeframe Direction & Signal Sprayer ---
st.divider()
st.subheader(f"📡 Live MT5 Telemetry & {timeframe} Direction Analysis")

if st.button("🔄 Sync Live Account, Direction & Tick Data"):
    pass

if tunnel_url and secret_key:
    try:
        resp = requests.get(
            f"{tunnel_url}/status",
            params={"secret": secret_key, "symbol": symbol, "timeframe": timeframe},
            timeout=TIMEOUT_SEC,
        ).json()

        if resp.get("status") == "connected":
            st.sidebar.success(f"Connected: {resp['login']} ({resp['server']})")
            active_auto = resp.get("auto_mode", False)

            if active_auto:
                st.success("🟢 CURRENT MODE: **ALLOW AUTOMATICALLY** (Bot executes smart spike setups automatically)")
            else:
                st.warning("🟡 CURRENT MODE: **TRADE MANUALLY** (Bot sprays direction & spike signals; you execute)")

            # Market Direction & Spike Environment Banner
            direction = resp.get("market_direction", "SIDEWAYS")
            rsi_val = resp.get("rsi_value", 50.0)
            spike_env = resp.get("spike_environment", "SCANNING...")
            sig_text = resp.get("latest_signal", "SCANNING...")
            sig_action = resp.get("signal_action", "WAIT")

            d1, d2 = st.columns(2)
            d1.metric(f"{timeframe} Market Direction", direction)
            d2.metric("RSI (14)", f"{rsi_val}")
            st.caption(f"🎯 **Spike Environment:** {spike_env}")

            if sig_action == "BUY":
                st.success(f"📣 LIVE SPIKE SIGNAL: **{sig_text}**")
            elif sig_action == "SELL":
                st.error(f"📣 LIVE SPIKE SIGNAL: **{sig_text}**")
            else:
                st.info(f"📣 ANALYSIS STATUS: **{sig_text}**")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Balance", f"${resp['balance']:.2f}")
            m2.metric("Equity", f"${resp['equity']:.2f}")
            m3.metric(f"{symbol} Bid", f"{resp['bid']:.4f}")
            m4.metric(f"{symbol} Ask", f"{resp['ask']:.4f}")

            # Manual Spike Scalp Buttons (Counter-spike side disabled on Boom/Crash)
            st.divider()
            st.subheader("🚀 Manual Spike Execution")
            b1, b2, b3 = st.columns([2, 2, 1])

            with b1:
                buy_disabled = is_crash
                if st.button(
                    "🟢 BUY SPIKE" if not buy_disabled else "🚫 BUY BLOCKED (CRASH = SELL ONLY)",
                    use_container_width=True,
                    disabled=buy_disabled,
                ):
                    t_res = requests.post(
                        f"{tunnel_url}/trade",
                        json={
                            "secret": secret_key,
                            "symbol": symbol,
                            "action": "BUY",
                            "lot": lot_size,
                            "sl_dollars": sl_dollars,
                            "tp_dollars": tp_dollars,
                        },
                        timeout=TIMEOUT_SEC,
                    ).json()
                    if t_res.get("status") == "success":
                        st.success(f"✅ BUY Executed! Ticket #{t_res['ticket']} @ {t_res['price']:.4f}")
                    else:
                        st.error(f"❌ Execution Failed: {t_res.get('message')}")

            with b2:
                sell_disabled = is_boom
                if st.button(
                    "🔴 SELL SPIKE" if not sell_disabled else "🚫 SELL BLOCKED (BOOM = BUY ONLY)",
                    use_container_width=True,
                    disabled=sell_disabled,
                ):
                    t_res = requests.post(
                        f"{tunnel_url}/trade",
                        json={
                            "secret": secret_key,
                            "symbol": symbol,
                            "action": "SELL",
                            "lot": lot_size,
                            "sl_dollars": sl_dollars,
                            "tp_dollars": tp_dollars,
                        },
                        timeout=TIMEOUT_SEC,
                    ).json()
                    if t_res.get("status") == "success":
                        st.success(f"✅ SELL Executed! Ticket #{t_res['ticket']} @ {t_res['price']:.4f}")
                    else:
                        st.error(f"❌ Execution Failed: {t_res.get('message')}")

            with b3:
                if st.button("🛑 CLOSE ALL", use_container_width=True):
                    c_res = requests.post(
                        f"{tunnel_url}/close_all",
                        json={"secret": secret_key},
                        timeout=TIMEOUT_SEC,
                    ).json()
                    st.info(f"Closed {c_res.get('closed', 0)} position(s).")

            # Active Positions & Signal History Log
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
                    st.caption("Signals will appear here when valid spike setups form.")
        else:
            st.sidebar.error(resp.get("message", "Connection error"))
    except Exception as e:
        st.error(f"Could not reach Windows PC bridge: {e}")
