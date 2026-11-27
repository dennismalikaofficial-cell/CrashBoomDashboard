from datetime import datetime
import requests
import streamlit as st

BRIDGE_URL_DEFAULT = "http://127.0.0.1:8000"
BRIDGE_SECRET_DEFAULT = "dennis_secret_998877"

FALLBACK_WEEKLY_SCHEDULE = {
    "Monday": ["Boom 1000 Index", "Step Index"],
    "Tuesday": ["Crash 1000 Index", "Volatility 75 Index", "XAUUSD"],
    "Wednesday": ["Boom 500 Index", "Step Index", "EURUSD"],
    "Thursday": ["Crash 500 Index", "Volatility 75 Index", "XAUUSD"],
    "Friday": ["Boom 300 Index", "Step Index"],
    "Saturday": ["Boom 1000 Index", "Crash 1000 Index"],
    "Sunday": ["Step Index", "Volatility 75 Index"],
}

ALL_SYMBOLS = [
    "Boom 1000 Index",
    "Boom 500 Index",
    "Boom 300 Index",
    "Crash 1000 Index",
    "Crash 500 Index",
    "Crash 300 Index",
    "Step Index",
    "Volatility 75 Index",
    "XAUUSD",
    "EURUSD",
]

st.set_page_config(page_title="Malika Synthetic Edge Dashboard", layout="wide")
st.title("⚡ Malika Synthetic Edge — MT5 Control & Spike Telemetry")

if "bridge_schedule" not in st.session_state:
    st.session_state["bridge_schedule"] = None
if "bridge_today_name" not in st.session_state:
    st.session_state["bridge_today_name"] = datetime.now().strftime("%A")

with st.sidebar:
    st.header("🌐 Connection Mode")
    bridge_url = st.text_input("Bridge URL", value=BRIDGE_URL_DEFAULT)
    bridge_secret = st.text_input("Bridge Secret Key", value=BRIDGE_SECRET_DEFAULT, type="password")
    req_timeout = st.slider("Bridge Timeout (sec)", min_value=10, max_value=45, value=25)

    st.divider()
    st.header("🔐 MT5 Account Login")
    acc_type = st.radio("Account Environment", ["DEMO", "LIVE"], horizontal=True)
    login_id = st.number_input("Account ID", value=41028777, step=1)
    password = st.text_input("Password", type="password")
    server = st.text_input("Server", value="Deriv-Demo" if acc_type == "DEMO" else "Deriv-Server")
    if st.button("Connect / Login MT5", use_container_width=True):
        try:
            r = requests.post(
                f"{bridge_url.rstrip('/')}/login",
                json={
                    "secret": bridge_secret,
                    "login": int(login_id),
                    "password": password,
                    "account_type": acc_type,
                    "server": server,
                    "save_login": True,
                },
                timeout=req_timeout,
            )
            data = r.json()
            if data.get("status") == "success":
                st.success(data.get("message", "Connected"))
            else:
                st.error(data.get("message", "Login failed"))
        except Exception as exc:
            st.error(f"Could not reach bridge at {bridge_url}: {exc}")

st.subheader("📅 Daily Product Timetable & Risk Guardrails")
use_daily_schedule = st.toggle(
    "Follow Daily Product Timetable (Manual Switch — OFF by default)",
    value=False,
)
max_concurrent_symbols = st.slider("Max Concurrent Symbols", min_value=2, max_value=4, value=3)

today_name = st.session_state.get("bridge_today_name") or datetime.now().strftime("%A")
todays_focus = (
    st.session_state.get("bridge_schedule")
    or FALLBACK_WEEKLY_SCHEDULE.get(today_name, ALL_SYMBOLS[:3])
)

if use_daily_schedule:
    st.info(f"**{today_name} Active Timetable:** {', '.join(todays_focus)}")
    active_symbols = todays_focus[: int(max_concurrent_symbols)]
else:
    st.caption("Timetable is **OFF** — select your symbols manually below.")
    selected_symbols = st.multiselect(
        "Active Symbols",
        options=ALL_SYMBOLS,
        default=["Boom 1000 Index", "Crash 1000 Index", "Step Index"],
    )
    if len(selected_symbols) > int(max_concurrent_symbols):
        st.warning(
            f"Selected {len(selected_symbols)} symbols; capping active scan to Max Concurrent Symbols ({int(max_concurrent_symbols)})."
        )
    active_symbols = selected_symbols[: int(max_concurrent_symbols)]

col_tf, col_lot, col_auto = st.columns(3)
with col_tf:
    timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "M30", "H1"], index=0)
with col_lot:
    base_lot = st.number_input("Base Lot", min_value=0.01, max_value=10.0, value=0.20, step=0.01)
with col_auto:
    auto_mode = st.toggle("Auto Spike Execution", value=False)

if st.button("Apply Mode & Schedule Settings", use_container_width=True):
    try:
        r = requests.post(
            f"{bridge_url.rstrip('/')}/set_mode",
            json={
                "secret": bridge_secret,
                "auto_mode": auto_mode,
                "use_daily_schedule": use_daily_schedule,
                "max_concurrent_symbols": int(max_concurrent_symbols),
                "symbols": active_symbols,
                "timeframe": timeframe,
                "lot": float(base_lot),
            },
            timeout=req_timeout,
        )
        res_data = r.json()
        st.success(f"Updated settings ({res_data.get('status', 'ok')})")
    except Exception as exc:
        st.error(f"Failed to update bridge: {exc}")

st.subheader("📡 Live MT5 Telemetry & Spike Intelligence")
if st.button("Sync Live Account & Spike Telemetry", use_container_width=True):
    try:
        r = requests.get(
            f"{bridge_url.rstrip('/')}/status",
            params={
                "secret": bridge_secret,
                "symbols": ",".join(active_symbols),
                "timeframe": timeframe,
                "use_daily_schedule": use_daily_schedule,
            },
            timeout=req_timeout,
        )
        payload = r.json()
        if payload.get("scheduled_symbols"):
            st.session_state["bridge_schedule"] = payload["scheduled_symbols"]
        if payload.get("today_name"):
            st.session_state["bridge_today_name"] = payload["today_name"]

        if payload.get("status") != "connected":
            st.warning(payload.get("message", "Bridge not connected to MT5"))
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Balance ($)", f"{payload.get('balance', 0.0):.2f}")
            m2.metric("Equity ($)", f"{payload.get('equity', 0.0):.2f}")
            m3.metric("Open Bot Trades", payload.get("active_bot_trades_count", 0))

            telem = payload.get("symbol_telemetry", {})
            if telem:
                rows = [
                    {
                        "Symbol": sym,
                        "Action": info.get("signal_action"),
                        "Confidence": info.get("confidence"),
                        "Direction": info.get("direction"),
                        "RSI": info.get("rsi"),
                        "Environment": info.get("spike_environment"),
                        "Lot": info.get("effective_lot"),
                    }
                    for sym, info in telem.items()
                ]
                st.dataframe(rows, use_container_width=True)

            if payload.get("exit_warnings"):
                for w in payload["exit_warnings"]:
                    st.warning(w.get("message"))

            if payload.get("signal_history"):
                st.markdown("**Recent Signals & Guard Events**")
                for line in payload["signal_history"][:12]:
                    st.text(line)
    except Exception as exc:
        st.error(f"Sync timed out or failed: {exc}")
