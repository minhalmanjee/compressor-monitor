import streamlit as st
import pandas as pd
import time
from db import get_recent

st.set_page_config(page_title="Compressor Monitor", layout="wide")
st.title("🔧 Gas Compressor Telemetry Monitor")

# ─── Session State ────────────────────────────────────────
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

# ─── Buttons ──────────────────────────────────────────────
col1, col2, _ = st.columns([1, 1, 6])
with col1:
    if st.button("▶ Start Monitoring", disabled=st.session_state.monitoring):
        st.session_state.monitoring = True
        st.rerun()
with col2:
    if st.button("⏹ Stop", disabled=not st.session_state.monitoring):
        st.session_state.monitoring = False
        st.rerun()

# ─── Dashboard ────────────────────────────────────────────
placeholder = st.empty()

if not st.session_state.monitoring:
    with placeholder.container():
        st.info("Press ▶ Start Monitoring to begin.")
        st.stop()

while st.session_state.monitoring:
    rows = get_recent(200)

    if len(rows) == 0:
        with placeholder.container():
            st.warning("No data yet — make sure simulator.py and ingestion.py are running.")
        time.sleep(2)
        continue

    df = pd.DataFrame(rows, columns=["timestamp", "pressure", "is_anomaly"])
    df["timestamp"]    = pd.to_datetime(df["timestamp"])
    df["rolling_mean"] = df["pressure"].rolling(window=20, min_periods=1).mean()
    df["rolling_std"]  = df["pressure"].rolling(window=20, min_periods=1).std().fillna(0)
    df["upper_bound"]  = df["rolling_mean"] + 2 * df["rolling_std"]

    anomalies = df[df["is_anomaly"] == 1]
    latest    = df.iloc[-1]

    with placeholder.container():
        c1, c2, c3 = st.columns(3)
        c1.metric("Latest Pressure", f"{latest['pressure']:.2f} PSI")
        c2.metric("Rolling Mean",    f"{latest['rolling_mean']:.2f} PSI")
        status = "ANOMALY DETECTED" if latest["is_anomaly"] else "System Healthy"
        c3.metric("System Status", status)

        st.divider()

        st.subheader("Pressure Over Time")
        st.line_chart(df.set_index("timestamp")[["pressure", "rolling_mean", "upper_bound"]])

        st.subheader(f"Anomaly Log ({len(anomalies)} detected)")
        if len(anomalies) > 0:
            st.dataframe(anomalies[["timestamp", "pressure"]].tail(10),
                         use_container_width=True)
        else:
            st.info("No anomalies detected yet. Wait ~30 seconds.")

    time.sleep(2)