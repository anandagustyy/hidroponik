import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")

# =========================
# STYLE DARK MODE & INTERFASIAL SINYAL
# =========================
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
    background-color: #333d4b; /* Warna default abu-abu saat mati */
    border-radius: 3px;
    transition: background-color 0.3s ease;
}
/* Tinggi masing-masing tingkatan bar sinyal */
.bar-1 { height: 20%; }
.bar-2 { height: 40%; }
.bar-3 { height: 60%; }
.bar-4 { height: 80%; }
.bar-5 { height: 100%; }

/* 3. PERBAIKAN JITU UNTUK BILAH MENU TABEL (ST.DATAFRAME) */
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

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=30000, key="refresh")

st.title("Smart Hydroponic Monitoring")

# =========================
# FIREBASE
# =========================
url = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json"
history_url = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"

# =========================
# AMBIL DATA
# =========================
try:
    data = requests.get(url).json()
    ph = float(data.get("ph", 0))
    ppm = int(data.get("ppm", 0))
except Exception:
    ph = 0.0
    ppm = 0

# =========================
# SIMPAN HISTORI
# =========================
new_data = {
    "time": str(datetime.now()),
    "ph": ph,
    "ppm": ppm
}
try:
    requests.post(history_url, json=new_data)
except Exception:
    pass

# =========================
# PENENTUAN LEVEL & WARNA SINYAL
# =========================

# Logika Sinyal pH
if 0 <= ph < 3.00:
    ph_level = 1
    ph_color = "#FF0000" # Merah
    ph_status = "Terlalu Asam"
elif 3.01 <= ph < 5.49:
    ph_level = 2
    ph_color = "#FFA500" # Oranye
    ph_status = "Asam"
elif 5.50 <= ph <= 7.00:
    ph_level = 3
    ph_color = "#00FF00" # Hijau
    ph_status = "Ideal"
elif 7.01 < ph < 10.00:
    ph_level = 4
    ph_color = "#00FFFF" # Biru Muda
    ph_status = "Basa"
else:
    ph_level = 5
    ph_color = "#0000FF" # Biru Tua
    ph_status = "Terlalu Basa"

# Logika Sinyal PPM
if 0 <= ppm <= 200:
    ppm_level = 1
    ppm_color = "#FF0000" # Merah
    ppm_status = "Nutrisi Sangat Rendah"
elif 201 <= ppm <= 499:
    ppm_level = 2
    ppm_color = "#FFA500" # Oranye
    ppm_status = "Kekurangan Nutrisi"
elif 500 <= ppm <= 1200:
    ppm_level = 3
    ppm_color = "#00FF00" # Hijau
    ppm_status = "Ideal"
elif 1201 <= ppm <= 1500:
    ppm_level = 4
    ppm_color = "#00FFFF" # Biru Muda
    ppm_status = "Nutrisi Berlebih"
else:
    ppm_level = 5
    ppm_color = "#0000FF" # Biru Tua
    ppm_status = "Nutrisi Terlalu Banyak"

# Opsi fungsi untuk me-render HTML Sinyal Bar secara akumulatif
def render_signal(level, color):
    bars = []
    for i in range(1, 6):
        # Jika i kurang dari atau sama dengan level status saat ini, nyalakan warna spesifiknya
        current_color = color if i <= level else "#333d4b"
        bars.append(f"<div class='signal-bar bar-{i}' style='background-color: {current_color};'></div>")
    
    return f"<div class='signal-container'>{''.join(bars)}</div>"


# =========================
# LAYOUT UTAMA (ANGKA METRIK & SINYAL)
# =========================
main_col1, main_col2 = st.columns(2)

with main_col1:
    # Memisahkan area metrik dan bar sinyal berdampingan kiri-kanan
    sub_col1, sub_col2 = st.columns([2, 1])
    with sub_col1:
        st.metric(label="pH", value=f"{ph:.2f}")
    with sub_col2:
        st.markdown("<p style='margin-bottom:-10px; font-size:14px; color:#aaa;'>Sinyal pH</p>", unsafe_allow_html=True)
        st.markdown(render_signal(ph_level, ph_color), unsafe_allow_html=True)

with main_col2:
    sub_col3, sub_col4 = st.columns([2, 1])
    with sub_col3:
        st.metric(label="PPM", value=f"{ppm}")
    with sub_col4:
        st.markdown("<p style='margin-bottom:-10px; font-size:14px; color:#aaa;'>Sinyal PPM</p>", unsafe_allow_html=True)
        st.markdown(render_signal(ppm_level, ppm_color), unsafe_allow_html=True)


# =========================
# STATUS TEXT (WARNA DEAFULT PUTIH)
# =========================
st.subheader("Status Nutrisi dan Keasaman")
st.write(f"Status pH: **{ph_status}**")
st.write(f"Status PPM: **{ppm_status}**")

# =========================
# PROSES DATA HISTORI
# =========================
try:
    history_data = requests.get(history_url).json()
except Exception:
    history_data = None

rows = []
if history_data:
    for key, value in history_data.items():
        rows.append(value)

df = pd.DataFrame(rows)

if not df.empty:
    df["time"] = pd.to_datetime(df["time"])
    df["ph"] = pd.to_numeric(df["ph"], errors='coerce')
    df["ppm"] = pd.to_numeric(df["ppm"], errors='coerce')
    df = df.dropna()
    df = df.sort_values("time")
    
    df_display = df.copy()
    df_display["time"] = df_display["time"].dt.strftime('%Y-%m-%d %H:%M:%S')

    # =========================
    # GRAFIK MONITORING
    # =========================
    st.subheader("Grafik Monitoring")
    
    graph_col1, graph_col2 = st.columns(2)
    
    with graph_col1:
        st.write("pH")
        st.line_chart(df.set_index("time")["ph"])
        
    with graph_col2:
        st.write("PPM")
        st.line_chart(df.set_index("time")["ppm"])

    # =========================
    # TABEL RIWAYAT LENGKAP
    # =========================
    st.subheader("Riwayat Lengkap")
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Belum ada data histori yang tersimpan.")
