import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time

# CONFIG
st.set_page_config(layout="wide", page_title="Smart Hydroponic Monitoring")

# STYLE DARK MODE & INTERFASIAL SINYAL
st.markdown("""
<style>
/* 1. Latar Belakang Aplikasi Utama */
.stApp {
    background-color: #0e1117;
}
.block-container {
    color: #ffffff;
}
h1, h2, h3, h4, h5, h6, p, label {
    color: #ffffff;
}

/* 2. STYLE INDIKATOR SINYAL HP KUSTOM */
.signal-container {
    display: flex;
    align-items: flex-end;
    gap: 6px;
    height: 60px;
    padding-bottom: 5px;
    margin-left: 15px;
}
.signal-bar {
    width: 10px;
    background-color: #333d4b;
    border-radius: 3px;
    transition: background-color 0.3s ease;
}
.bar-1 { height: 20%; }
.bar-2 { height: 40%; }
.bar-3 { height: 60%; }
.bar-4 { height: 80%; }
.bar-5 { height: 100%; }

/* 3. PERBAIKAN BILAH MENU TABEL */
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"],
div[data-testid="stDataFrame"] [style*="background-color"] {
    background-color: #5c4033 !important;
}
div[data-testid="stDataFrame"] > div {
    --gdt-toolbar-background: #5c4033 !important;
}
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] svg,
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] button,
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] span,
div[data-testid="stDataFrame"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] button:hover {
    background-color: #704d3e !important;
}

/* 4. Perbaikan Toolbar pada Grafik */
[data-testid="stVegaLiteChartToolbar"] {
    background-color: #5c4033 !important;
    border-radius: 4px;
    opacity: 1 !important;
}
[data-testid="stVegaLiteChartToolbar"] button svg {
    fill: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# AUTO REFRESH SETIAP 20 DETIK (20000 ms)
st_autorefresh(interval=20000, key="refresh_sensor_data")

st.title("Smart Hydroponic Monitoring")

# FIREBASE INTERFACE (Dengan Query Anti-Cache)
timestamp_param = int(time.time() * 1000)
url = f"https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json?t={timestamp_param}"
history_url = f"https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/history.json?t={timestamp_param}"
http_headers = {"Cache-Control": "no-cache"}

# AMBIL DATA REAL-TIME
try:
    data = requests.get(url, headers=http_headers, timeout=5).json()
    if isinstance(data, dict):
        ph = float(data.get("ph", 0.0))
        ppm = int(data.get("ppm", 0))
    else:
        ph, ppm = 0.0, 0
except Exception:
    ph, ppm = 0.0, 0

# Logika Sinyal pH
if 0 <= ph < 3.00:
    ph_level, ph_color, ph_status = 1, "#FF0000", "Terlalu Asam"
elif 3.01 <= ph < 5.49:
    ph_level, ph_color, ph_status = 2, "#FFA500", "Asam"
elif 5.50 <= ph <= 7.00:
    ph_level, ph_color, ph_status = 3, "#00FF00", "Ideal"
elif 7.01 < ph < 10.00:
    ph_level, ph_color, ph_status = 4, "#00FFFF", "Basa"
else:
    ph_level, ph_color, ph_status = 5, "#0000FF", "Terlalu Basa"

# Logika Sinyal PPM
if 0 <= ppm <= 200:
    ppm_level, ppm_color, ppm_status = 1, "#FF0000", "Nutrisi Sangat Rendah"
elif 201 <= ppm <= 499:
    ppm_level, ppm_color, ppm_status = 2, "#FFA500", "Kekurangan Nutrisi"
elif 500 <= ppm <= 1200:
    ppm_level, ppm_color, ppm_status = 3, "#00FF00", "Ideal"
elif 1201 <= ppm <= 1500:
    ppm_level, ppm_color, ppm_status = 4, "#00FFFF", "Nutrisi Berlebih"
else:
    ppm_level, ppm_color, ppm_status = 5, "#0000FF", "Nutrisi Terlalu Banyak"

def render_signal(level, color):
    bars = []
    for i in range(1, 6):
        current_color = color if i <= level else "#333d4b"
        bars.append(f"<div class='signal-bar bar-{i}' style='background-color: {current_color};'></div>")
    return f"<div class='signal-container'>{''.join(bars)}</div>"

# LAYOUT UTAMA (METRIK & SINYAL)
main_col1, main_col2 = st.columns(2)

with main_col1:
    sub_col1, sub_col2 = st.columns([2, 1])
    with sub_col1:
        st.metric(label="pH", value=f"{ph:.2f}")
    with sub_col2:
        st.markdown(render_signal(ph_level, ph_color), unsafe_allow_html=True)

with main_col2:
    sub_col3, sub_col4 = st.columns([2, 1])
    with sub_col3:
        st.metric(label="PPM", value=f"{ppm}")
    with sub_col4:
        st.markdown(render_signal(ppm_level, ppm_color), unsafe_allow_html=True)

# STATUS TEXT
st.subheader("Status Nutrisi dan Keasaman")
st.write(f"Status pH: **{ph_status}**")
st.write(f"Status PPM: **{ppm_status}**")

st.divider()

# PROSES DATA HISTORI
try:
    history_data = requests.get(history_url, headers=http_headers, timeout=5).json()
except Exception:
    history_data = None

rows = []
if history_data and isinstance(history_data, dict):
    for key, value in history_data.items():
        if isinstance(value, dict) and "time" in value:
            rows.append(value)

df = pd.DataFrame(rows)

if not df.empty:
    df["time"] = pd.to_datetime(df["time"], unit='ms', errors='coerce')
    df["ph"] = pd.to_numeric(df["ph"], errors='coerce')
    df["ppm"] = pd.to_numeric(df["ppm"], errors='coerce')
    
    df = df.dropna(subset=["time", "ph", "ppm"])
    df = df.sort_values("time")
    
    # GRAFIK MONITORING
    st.subheader("Grafik Monitoring")
    graph_col1, graph_col2 = st.columns(2)
    
    with graph_col1:
        st.write("**Grafik pH**")
        st.line_chart(df.set_index("time")["ph"])
        
    with graph_col2:
        st.write("**Grafik PPM**")
        st.line_chart(df.set_index("time")["ppm"])

    # TABEL RIWAYAT LENGKAP
    st.subheader("Riwayat Lengkap")
    df_display = df.copy()
    df_display["time"] = df_display["time"].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df_table = df_display.sort_values("time", ascending=False).reset_index(drop=True)
    st.dataframe(df_table, use_container_width=True)
else:
    st.info("Belum ada data histori yang tersimpan. Menunggu data baru dari ESP32...")
