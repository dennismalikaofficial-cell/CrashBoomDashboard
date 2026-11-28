from datetime import datetime
import time
import pandas as pd
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

st.markdown(
    """
    <style>
    .status-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 14px;
    }
    .pill-on {
        background: #e6f6ec;
        color: #137333;
        border: 1px solid #a8dab5;
        padding: 4px 11px;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 600;
    }
    .pill-off {
        background: #f1f3f4;
        color: #5f6368;
        border: 1px solid #dadce0;
        padding: 4px 11px;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

for k, v in {
    "bridge_schedule": None,
    "bridge_today_name": datetime.now().strftime("%A"),
    "last_payload": None,
    "cfg_hydrated": False,
    "cfg_auto_mode": False,
    "cfg_use_schedule": False,
    "cfg_max_syms": 3,
    "cfg_symbols": ["Boom 1000 Index", "Crash 1000 Index", "Step Index"],
    "cfg_timeframe": "M1",
    "cfg_lot": 0.20,
    "cfg_std_sl_on": False,
    "cfg_std_sl_usd": 2.00,
    "cfg_alt_sl_on": False,
    "cfg_alt_sl_usd": 5.00,
    "cfg_tp_on": False,
    "cfg_tp_usd": 0.50,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


def pill_html(label: str, is_on: bool, detail: str = "") -> str:
    state_txt = f"ON{f' ({detail})' if detail else ''}" if is_on else "OFF"
    cls = "pill-on" if is_on else "pill-off"
    icon = "🟢" if is_on else "⚪"
    return f'<span class="{cls}">{icon} {label}: {state_txt}</span>'


def hydrate_from_payload(payload: dict, force: bool = False):
    if not payload or payload.get("status") != "connected":
        return
    if st.session_state.get("cfg_hydrated") and not force:
        return

    if "auto_mode" in payload:
        st.session_state["cfg_auto_mode"] = bool(payload["auto_mode"])
    if "use_daily_schedule" in payload:
        st.session_state["cfg_use_schedule"] = bool(payload["use_daily_schedule"])
    if "max_concurrent_symbols" in payload:
        st.session_state["cfg_max_syms"] = int(payload["max_concurrent_symbols"])
    if "std_sl_enabled" in payload:
        st.session_state["cfg_std_sl_on"] = bool(payload["std_sl_enabled"])
    if "std_sl_dollars" in payload:
        st.session_state["cfg_std_sl_usd"] = float(payload["std_sl_dollars"])
    if "alt_sl_enabled" in payload:
        st.session_state["cfg_alt_sl_on"] = bool(payload["alt_sl_enabled"])
    if "alt_sl_dollars" in payload:
        st.session_state["cfg_alt_sl_usd"] = float(payload["alt_sl_dollars"])
    if "manual_tp_enabled" in payload:
        st.session_state["cfg_tp_on"] = bool(payload["manual_tp_enabled"])
    if "tp_dollars" in payload:
        st.session_state["cfg_tp_usd"] = float(payload["tp_dollars"])
    if payload.get("timeframe"):
        st.session_state["cfg_timeframe"] = payload["timeframe"]
    if "lot" in payload:
        st.session_state["cfg_lot"] = float(payload["lot"])
    if payload.get("active_symbols") and not st.session_state.get("cfg_use_schedule"):
        st.session_state["cfg_symbols"] = list(payload["active_symbols"])

    st.session_state["cfg_hydrated"] = True


def fetch_status(
    bridge_url: str,
    bridge_secret: str,
    symbols: list[str],
    timeframe: str,
    use_sched: bool,
    timeout: int,
    force_hydrate: bool = False,
):
    r = requests.get(
        f"{bridge_url.rstrip('/')}/status",
        params={
            "secret": bridge_secret,
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "use_daily_schedule": use_sched,
        },
        timeout=timeout,
    )
    payload = r.json()
    if payload.get("scheduled_symbols"):
        st.session_state["bridge_schedule"] = payload["scheduled_symbols"]
    if payload.get("today_name"):
        st.session_state["bridge_today_name"] = payload["today_name"]
    st.session_state["last_payload"] = payload
    hydrate_from_payload(payload, force=force_hydrate)
    return payload


def push_mode_settings(bridge_url: str, bridge_secret: str, active_symbols: list[str], timeout: int):
    r = requests.post(
        f"{bridge_url.rstrip('/')}/set_mode",
        json={
            "secret": bridge_secret,
            "auto_mode": bool(st.session_state["cfg_auto_mode"]),
            "use_daily_schedule": bool(st.session_state["cfg_use_schedule"]),
            "max_concurrent_symbols": int(st.session_state["cfg_max_syms"]),
            "std_sl_enabled": bool(st.session_state["cfg_std_sl_on"]),
            "std_sl_dollars": float(st.session_state["cfg_std_sl_usd"]),
            "alt_sl_enabled": bool(st.session_state["cfg_alt_sl_on"]),
            "alt_sl_dollars": float(st.session_state["cfg_alt_sl_usd"]),
            "manual_tp_enabled": bool(st.session_state["cfg_tp_on"]),
            "tp_dollars": float(st.session_state["cfg_tp_usd"]),
            "symbols": active_symbols,
            "timeframe": st.session_state["cfg_timeframe"],
            "lot": float(st.session_state["cfg_lot"]),
        },
        timeout=timeout,
    )
    return r.json()


# ===================== SIDEBAR ACTION DRAWERS =====================
with st.sidebar:
    st.markdown("### 🎛️ Control Center")
    st.caption("Click any button below to open its controls.")

    # 1) Connection & MT5 Login Drawer
    with st.popover("🔐 MT5 Login & Bridge Connection", use_container_width=True):
        bridge_url = st.text_input("Bridge URL", value=BRIDGE_URL_DEFAULT)
        bridge_secret = st.text_input("Bridge Secret Key", value=BRIDGE_SECRET_DEFAULT, type="password")
        req_timeout = st.slider("Bridge Timeout (sec)", min_value=5, max_value=45, value=15)
        st.divider()
        acc_type = st.radio("Environment", ["DEMO", "LIVE"], horizontal=True)
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
                st.error(f"Bridge error: {exc}")

    # 2) Timetable & Active Symbols Drawer
    with st.popover("📅 Timetable & Symbol Selection", use_container_width=True):
        st.session_state["cfg_use_schedule"] = st.toggle(
            "Daily Product Timetable",
            value=st.session_state["cfg_use_schedule"],
        )
        st.session_state["cfg_max_syms"] = st.slider(
            "Max Concurrent Symbols",
            min_value=2,
            max_value=4,
            value=st.session_state["cfg_max_syms"],
        )
        today_name = st.session_state.get("bridge_today_name") or datetime.now().strftime("%A")
        todays_focus = (
            st.session_state.get("bridge_schedule")
            or FALLBACK_WEEKLY_SCHEDULE.get(today_name, ALL_SYMBOLS[:3])
        )
        if st.session_state["cfg_use_schedule"]:
            st.info(f"**{today_name}:** {', '.join(todays_focus)}")
            resolved_syms = todays_focus[: int(st.session_state["cfg_max_syms"])]
        else:
            picked = st.multiselect(
                "Manual Symbols",
                options=ALL_SYMBOLS,
                default=st.session_state["cfg_symbols"],
            )
            st.session_state["cfg_symbols"] = picked or ["Boom 1000 Index"]
            resolved_syms = st.session_state["cfg_symbols"][: int(st.session_state["cfg_max_syms"])]

        if st.button("Apply Symbol / Schedule Settings", use_container_width=True):
            try:
                res = push_mode_settings(bridge_url, bridge_secret, resolved_syms, req_timeout)
                fetch_status(
                    bridge_url,
                    bridge_secret,
                    resolved_syms,
                    st.session_state["cfg_timeframe"],
                    st.session_state["cfg_use_schedule"],
                    req_timeout,
                    force_hydrate=True,
                )
                st.success(f"Applied ({res.get('status', 'ok')})")
            except Exception as exc:
                st.error(f"Failed: {exc}")

    # 3) Execution, Lot & SL/TP Drawer
    with st.popover("🛡️ Auto Execution & SL / TP Rules", use_container_width=True):
        st.session_state["cfg_auto_mode"] = st.toggle(
            "Auto Spike Execution",
            value=st.session_state["cfg_auto_mode"],
        )
        c1, c2 = st.columns(2)
        with c1:
            tf_list = ["M1", "M5", "M15", "M30", "H1"]
            st.session_state["cfg_timeframe"] = st.selectbox(
                "Timeframe",
                tf_list,
                index=tf_list.index(st.session_state["cfg_timeframe"]),
            )
        with c2:
            st.session_state["cfg_lot"] = st.number_input(
                "Base Lot",
                min_value=0.01,
                max_value=10.0,
                value=float(st.session_state["cfg_lot"]),
                step=0.01,
            )

        st.divider()
        st.session_state["cfg_std_sl_on"] = st.toggle(
            "0.20 Group SL (1000 / 500)",
            value=st.session_state["cfg_std_sl_on"],
        )
        st.session_state["cfg_std_sl_usd"] = st.number_input(
            "0.20 SL Amount ($)",
            min_value=0.10,
            max_value=500.0,
            value=float(st.session_state["cfg_std_sl_usd"]),
            step=0.25,
        )

        st.session_state["cfg_alt_sl_on"] = st.toggle(
            "Min-Lot Group SL (300 / Others)",
            value=st.session_state["cfg_alt_sl_on"],
        )
        st.session_state["cfg_alt_sl_usd"] = st.number_input(
            "Min-Lot SL Amount ($)",
            min_value=0.10,
            max_value=500.0,
            value=float(st.session_state["cfg_alt_sl_usd"]),
            step=0.25,
        )

        st.divider()
        st.session_state["cfg_tp_on"] = st.toggle(
            "Manual Take-Profit (TP)",
            value=st.session_state["cfg_tp_on"],
        )
        st.session_state["cfg_tp_usd"] = st.number_input(
            "TP Target ($)",
            min_value=0.10,
            max_value=500.0,
            value=float(st.session_state["cfg_tp_usd"]),
            step=0.10,
        )

        if st.button("Apply Execution & SL/TP", use_container_width=True):
            try:
                res = push_mode_settings(bridge_url, bridge_secret, resolved_syms, req_timeout)
                fetch_status(
                    bridge_url,
                    bridge_secret,
                    resolved_syms,
                    st.session_state["cfg_timeframe"],
                    st.session_state["cfg_use_schedule"],
                    req_timeout,
                    force_hydrate=True,
                )
                st.success(f"Saved ({res.get('status', 'ok')})")
            except Exception as exc:
                st.error(f"Failed: {exc}")

    # 4) Quick Manual Order & Emergency Close Drawer
    with st.popover("🎯 Quick Order / Emergency Close", use_container_width=True):
        order_sym = st.selectbox("Symbol", options=ALL_SYMBOLS, index=0)
        order_side = st.radio("Direction", ["BUY", "SELL"], horizontal=True)
        order_lot = st.number_input("Order Lot", min_value=0.01, max_value=10.0, value=float(st.session_state["cfg_lot"]), step=0.01)
        if st.button("🚀 Place Manual Order", use_container_width=True):
            try:
                r = requests.post(
                    f"{bridge_url.rstrip('/')}/trade",
                    json={
                        "secret": bridge_secret,
                        "symbol": order_sym,
                        "action": order_side,
                        "lot": float(order_lot),
                        "std_sl_enabled": bool(st.session_state["cfg_std_sl_on"]),
                        "std_sl_dollars": float(st.session_state["cfg_std_sl_usd"]),
                        "alt_sl_enabled": bool(st.session_state["cfg_alt_sl_on"]),
                        "alt_sl_dollars": float(st.session_state["cfg_alt_sl_usd"]),
                        "apply_manual_tp": bool(st.session_state["cfg_tp_on"]),
                        "tp_dollars": float(st.session_state["cfg_tp_usd"]),
                    },
                    timeout=req_timeout,
                )
                st.info(r.json().get("message", r.json().get("status")))
            except Exception as exc:
                st.error(f"Order error: {exc}")

        st.divider()
        if st.button("🛑 Close All Bot Trades", use_container_width=True):
            try:
                r = requests.post(
                    f"{bridge_url.rstrip('/')}/close_all",
                    json={"secret": bridge_secret},
                    timeout=req_timeout,
                )
                st.warning(f"Closed {r.json().get('closed', 0)} trade(s)")
            except Exception as exc:
                st.error(f"Close all error: {exc}")

    st.divider()
    auto_refresh = st.toggle("🔄 Auto-Refresh (3s)", value=False)


# ===================== MAIN CLEAN DASHBOARD =====================
st.title("⚡ Malika Synthetic Edge")

if st.session_state["last_payload"] is None:
    try:
        fetch_status(
            bridge_url,
            bridge_secret,
            resolved_syms,
            st.session_state["cfg_timeframe"],
            st.session_state["cfg_use_schedule"],
            req_timeout,
        )
    except Exception:
        pass

payload = st.session_state.get("last_payload")
live_auto = payload.get("auto_mode", st.session_state["cfg_auto_mode"]) if payload else st.session_state["cfg_auto_mode"]
live_sched = payload.get("use_daily_schedule", st.session_state["cfg_use_schedule"]) if payload else st.session_state["cfg_use_schedule"]
live_std_sl = payload.get("std_sl_enabled", st.session_state["cfg_std_sl_on"]) if payload else st.session_state["cfg_std_sl_on"]
live_alt_sl = payload.get("alt_sl_enabled", st.session_state["cfg_alt_sl_on"]) if payload else st.session_state["cfg_alt_sl_on"]
live_tp = payload.get("manual_tp_enabled", st.session_state["cfg_tp_on"]) if payload else st.session_state["cfg_tp_on"]

# Always-visible ON/OFF status pills reflecting live bridge state
pills_markup = (
    '<div class="status-strip">'
    + pill_html("Auto Spike", bool(live_auto), st.session_state["cfg_timeframe"])
    + pill_html("Timetable", bool(live_sched), st.session_state.get("bridge_today_name", ""))
    + pill_html("0.20 Group SL", bool(live_std_sl), f"${st.session_state['cfg_std_sl_usd']:.2f}")
    + pill_html("Min-Lot SL", bool(live_alt_sl), f"${st.session_state['cfg_alt_sl_usd']:.2f}")
    + pill_html("Manual TP", bool(live_tp), f"${st.session_state['cfg_tp_usd']:.2f}")
    + f'<span class="pill-off">📌 Active: {", ".join(resolved_syms)}</span>'
    + "</div>"
)
st.markdown(pills_markup, unsafe_allow_html=True)

b1, b2 = st.columns([3, 1])
with b1:
    sync_clicked = st.button("📡 Sync Live Account & Spike Telemetry", use_container_width=True)
with b2:
    refresh_clicked = st.button("🔄 Refresh Now", use_container_width=True)

if sync_clicked or refresh_clicked:
    try:
        fetch_status(
            bridge_url,
            bridge_secret,
            resolved_syms,
            st.session_state["cfg_timeframe"],
            st.session_state["cfg_use_schedule"],
            req_timeout,
        )
        payload = st.session_state.get("last_payload")
    except Exception as exc:
        st.error(f"Sync timed out or failed: {exc}")

if payload:
    if payload.get("status") != "connected":
        st.warning(payload.get("message", "Bridge not connected to MT5"))
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Balance ($)", f"{payload.get('balance', 0.0):.2f}")
        m2.metric("Equity ($)", f"{payload.get('equity', 0.0):.2f}")
        m3.metric("Open Bot Trades", payload.get("active_bot_trades_count", 0))

        if payload.get("exit_warnings"):
            for w in payload["exit_warnings"]:
                st.warning(w.get("message"))

        tab_live, tab_trades, tab_ledger, tab_logs = st.tabs(
            ["📡 Spike Telemetry", "📈 Open Positions", "📒 Trade Ledger", "🧾 Signal Log"]
        )

        with tab_live:
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
            else:
                st.caption("Click Sync Live Account & Spike Telemetry to load symbol intelligence.")

        with tab_trades:
            open_trades = payload.get("open_trades", [])
            if open_trades:
                st.dataframe(open_trades, use_container_width=True)
                tickets = [int(t["Ticket"]) for t in open_trades if "Ticket" in t]
                q1, q2 = st.columns([2, 1])
                with q1:
                    selected_ticket = st.selectbox("Ticket to Close", options=tickets)
                with q2:
                    st.write("")
                    if st.button("❌ Quit Selected Trade", use_container_width=True):
                        r = requests.post(
                            f"{bridge_url.rstrip('/')}/close_ticket",
                            json={"secret": bridge_secret, "ticket": int(selected_ticket)},
                            timeout=req_timeout,
                        )
                        st.info(r.json().get("message", r.json().get("status")))
                        fetch_status(
                            bridge_url,
                            bridge_secret,
                            resolved_syms,
                            st.session_state["cfg_timeframe"],
                            st.session_state["cfg_use_schedule"],
                            req_timeout,
                        )
                        st.rerun()
            else:
                st.caption("No open bot trades right now.")

        with tab_ledger:
            journal_rows = payload.get("journal", [])
            if journal_rows:
                st.dataframe(pd.DataFrame(journal_rows), use_container_width=True)
            else:
                st.caption("No closed deals recorded in `trade_journal.csv` yet.")

        with tab_logs:
            if payload.get("signal_history"):
                for line in payload["signal_history"][:20]:
                    st.text(line)
            else:
                st.caption("No recent signals or guard events yet.")

if auto_refresh:
    time.sleep(3)
    st.rerun()
