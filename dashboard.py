import streamlit as st
import pandas as pd
import time
from db import get_recent

st.set_page_config(page_title = "Compressor Monitor", layout = 'wide')
st.title("Compressor Telemetry Monitor")

placeholder = st.empty()

while True:
    rows = get_recent(200)

    if len(rows) == 0 :
        with placeholder.container():
            st.warning("No data found")
        time.sleep(2)
        continue

    df = pd.DataFrame(rows, columns=["timestamp", "pressure", "is_anomaly"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["rolling_mean"] = df["pressure"].rolling(window=20, min_periods=1).mean()
    df["rolling_std"]  = df["pressure"].rolling(window=20, min_periods=1).std().fillna(0)
    df["upper_bound"]  = df["rolling_mean"] + 2 * df["rolling_std"]

    anomalies = df[df["is_anomaly"] == 1]
    latest = df.iloc[-1]

    with placeholder.container():
        c1, c2, c3 = st.columns(3)
        c1.metric("Latest Pressure", f"{latest['pressure']:.2f} PSI")
        c2.metric("Rolling Mean", f"{latest['rolling_mean']:.2f} PSI")
        status = " ANOMALY DETECTED" if latest["is_anomaly"] else " System Healthy"
        c3.metric("System Status", status)

        st.divider()

        # --- Pressure Chart ---
        st.subheader("Pressure Over Time")
        chart_df = df.set_index("timestamp")[["pressure", "rolling_mean", "upper_bound"]]
        st.line_chart(chart_df)

        # --- Anomaly Log ---
        st.subheader(f"Anomaly Log ({len(anomalies)} detected)")
        if len(anomalies) > 0:
            st.dataframe(
                anomalies[["timestamp", "pressure"]].tail(10),
                use_container_width=True
            )
        else:
            st.info("No anomalies detected yet.")

    time.sleep(2)