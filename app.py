import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

st.set_page_config(
    page_title="Monitoring Hidroponik",
    page_icon="🌱",
    layout="wide"
)

FIREBASE_REALTIME_URL = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json"
FIREBASE_HISTORY_URL  = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"

st.title("🌱 Dashboard Monitoring Hidroponik Terkalibrasi")
st.markdown("Monitoring Parameter pH dan Kepekatan Nutrisi (TDS PPM) secara Realtime.")

# Request realtime dengan header pencegah cache
headers = {'Cache-Control': 'no-cache'}

try:
    res_realtime = requests.get(FIREBASE_REALTIME_URL, headers=headers).json()
except Exception:
    res_realtime = None

if res_realtime and isinstance(res_realtime, dict):
    ph_val = float(res_realtime.get("ph", 0.0))
    ppm_val = int(res_realtime.get("ppm", 0))
    status = res_realtime.get("status", "Offline")
else:
    ph_val, ppm_val, status = 0.0, 0, "Offline"

# Kartu Metrik Realtime
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="pH Air Nutrisi", value=f"{ph_val:.2f}")
    if 5.5 <= ph_val <= 6.5:
        st.success("Kondisi pH Ideal (5.5 - 6.5)")
    else:
        st.warning("pH di Luar Ambang Ideal")

with col2:
    st.metric(label="TDS Nutrisi", value=f"{ppm_val} PPM")
    if 500 <= ppm_val <= 1200:
        st.success("Nutrisi Normal")
    elif ppm_val < 500:
        st.info("Nutrisi Kurang")
    else:
        st.warning("Nutrisi Pekat")

with col3:
    st.metric(label="Status Alat", value=status)
    if status == "Online":
        st.success("Sistem Terhubung")
    else:
        st.error("Sistem Terputus")

st.divider()

# Ambil data Histori
st.subheader("📈 Riwayat Data Sensor (Histori)")

try:
    res_history = requests.get(FIREBASE_HISTORY_URL, headers=headers).json()
except Exception:
    res_history = None

if res_history and isinstance(res_history, dict):
    records = []
    for key, item in res_history.items():
        if isinstance(item, dict):
            # Penanganan fleksibel untuk format timestamp
            raw_time = item.get("time")
            waktu_dt = None
            
            if isinstance(raw_time, (int, float)):
                # Jika time berupa timestamp milidetik Firebase
                waktu_dt = datetime.fromtimestamp(raw_time / 1000.0)
            elif isinstance(raw_time, str):
                try:
                    waktu_dt = datetime.fromisoformat(raw_time)
                except Exception:
                    waktu_dt = datetime.now()
            else:
                waktu_dt = datetime.now()

            records.append({
                "Waktu": waktu_dt,
                "pH": float(item.get("ph", 0.0)),
                "PPM": int(item.get("ppm", 0))
            })
    
    if records:
        df = pd.DataFrame(records).sort_values("Waktu")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            fig_ph = px.line(df, x="Waktu", y="pH", title="Grafik Fluktuasi pH", markers=True)
            st.plotly_chart(fig_ph, use_container_width=True)

        with chart_col2:
            fig_ppm = px.line(df, x="Waktu", y="PPM", title="Grafik Fluktuasi TDS (PPM)", markers=True)
            st.plotly_chart(fig_ppm, use_container_width=True)

        with st.expander("Lihat Tabel Data Log (Terbaru di Atas)"):
            df_display = df.copy()
            df_display["Waktu"] = df_display["Waktu"].dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(df_display.sort_values("Waktu", ascending=False), use_container_width=True)
    else:
        st.info("Belum ada data histori yang valid.")
else:
    st.info("Belum ada data histori di Firebase.")

# Auto refresh setiap 10 detik
time.sleep(10)
st.rerun()
