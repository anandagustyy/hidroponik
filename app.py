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
# STYLE DARK MODE & PERBAIKAN TOTAL DATA FRAME TOOLBAR
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

/* 2. PERBAIKAN JITU UNTUK BILAH MENU TABEL (ST.DATAFRAME) */
/* Menargetkan kontainer luar bilah menu agar berwarna Cokelat Tua */
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"],
div[data-testid="stDataFrame"] [style*="background-color"] {
    background-color: #5c4033 !important; /* Mengubah bilah menjadi Cokelat Tua */
}

/* Menembus masuk ke elemen internal Glide Data Grid untuk mengubah warna background toolbar */
div[data-testid="stDataFrame"] > div {
    --gdt-toolbar-background: #5c4033 !important;
}

/* Memaksa semua ikon (SVG), titik tiga, panah, dan teks di dalam bilah tersebut menjadi PUTIH PEKAT */
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] svg,
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] button,
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] span,
div[data-testid="stDataFrame"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* Menghilangkan efek warna putih/abu-abu yang menutupi tombol saat diarahkan kursor */
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] button:hover {
    background-color: #704d3e !important;
}

/* 3. Perbaikan Toolbar pada Grafik */
[data-testid="stVegaLiteChartToolbar"] {
    background-color: #5c4033 !important;
    border-radius: 4px;
    opacity: 1 !important;
}
[data-testid="stVegaLiteChartToolbar"] button svg {
    fill: #ffffff !important;
}

/* 4. Modifikasi Tombol Utama (Jika ada komponen tombol lain di masa depan) */
div.stButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-weight: bold;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover {
    background-color: #222222 !important;
    border-color: #aaaaaa !important;
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
# LAYOUT UTAMA (MENAMPILKAN ANGKA BESAR)
# =========================
col1, col2 = st.columns(2)

with col1:
    st.metric(label="pH", value=f"{ph:.2f}")

with col2:
    st.metric(label="PPM", value=f"{ppm}")

# =========================
# STATUS TEXT (KUSTOM WARNA)
# =========================
st.subheader("Status Nutrisi dan Keasaman")

# Teks pH
if 0 <= ph < 3.00:
    st.markdown("Status pH: <span style='color: #FF0000; font-weight: bold;'>Terlalu Asam</span>", unsafe_allow_html=True)
elif 3.01 <= ph < 5.49:
    st.markdown("Status pH: <span style='color: #FFA500; font-weight: bold;'>Asam</span>", unsafe_allow_html=True)
elif 5.50 <= ph <= 7.00:
    st.markdown("Status pH: <span style='color: #00FF00; font-weight: bold;'>Ideal</span>", unsafe_allow_html=True)
elif 7.01 < ph < 10.00:
    st.markdown("Status pH: <span style='color: #00FFFF; font-weight: bold;'>Basa</span>", unsafe_allow_html=True)
elif ph >= 10.01:
    st.markdown("Status pH: <span style='color: #0000FF; font-weight: bold;'>Terlalu Basa</span>", unsafe_allow_html=True)

# Teks PPM
if 0 <= ppm <= 200:
    st.markdown("Status PPM: <span style='color: #FF0000; font-weight: bold;'>Nutrisi Sangat Rendah</span>", unsafe_allow_html=True)
elif 201 <= ppm <= 499:
    st.markdown("Status PPM: <span style='color: #FFA500; font-weight: bold;'>Kekurangan Nutrisi</span>", unsafe_allow_html=True)
elif 500 <= ppm <= 1200:
    st.markdown("Status PPM: <span style='color: #00FF00; font-weight: bold;'>Ideal</span>", unsafe_allow_html=True)
elif 1201 <= ppm <= 1500:
    st.markdown("Status PPM: <span style='color: #00FFFF; font-weight: bold;'>Nutrisi Berlebih</span>", unsafe_allow_html=True)
elif ppm >= 1501:
    st.markdown("Status PPM: <span style='color: #0000FF; font-weight: bold;'>Nutrisi Terlalu Banyak</span>", unsafe_allow_html=True)

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
    
    # Menampilkan tabel (fitur download CSV otomatis tersedia di dalam bilah cokelat tua tabel ini)
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Belum ada data histori yang tersimpan.")
