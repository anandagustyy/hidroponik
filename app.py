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
# STYLE DARK MODE & PERBAIKAN POPUP/SEARCH TABEL (COKELAT & PUTIH)
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

/* 2. PERBAIKAN UNTUK MENU PENCARIAN / FILTER / TOOLBAR DI BAWAH DOWNLOAD (ST.DATAFRAME) */
/* Menargetkan kontainer menu toolbar, popover, dan search box bawaan tabel agar berwarna Cokelat Tua */
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"],
div[data-testid="stDataFrame"] div[role="dialog"],
div[data-testid="stDataFrame"] input,
div[data-testid="stDataFrame"] [data-testid="stDataFrameSearchBox"] {
    background-color: #5c4033 !important; /* Warna Cokelat Tua */
    color: #ffffff !important;           /* Teks menjadi Putih pekat */
    border: 1px solid #ffffff !important;
    border-radius: 6px;
    opacity: 1 !important;
}

/* Memaksa semua elemen anak (ikon, teks, placeholder) di dalam area tersebut menjadi putih */
div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] *,
div[data-testid="stDataFrame"] div[role="dialog"] *,
div[data-testid="stDataFrame"] [data-testid="stDataFrameSearchBox"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
}

/* Mengatur input text di dalam box pencarian tabel agar teks yang diketik berwarna putih */
div[data-testid="stDataFrame"] input {
    color: #ffffff !important;
    background-color: #4a3228 !important; /* Cokelat sedikit lebih gelap untuk box input */
}

/* Efek hover pada tombol-tombol menu di dalam tabel */
div[data-testid="stDataFrame"] button:hover {
    background-color: #704d3e !important;
}

/* 3. Perbaikan Toolbar pada Grafik (Sinkron menggunakan Cokelat Tua) */
[data-testid="stVegaLiteChartToolbar"] {
    background-color: #5c4033 !important;
    border-radius: 4px;
    opacity: 1 !important;
}
[data-testid="stVegaLiteChartToolbar"] button svg {
    fill: #ffffff !important;
}

/* 4. Modifikasi Tombol Utama (Download CSV) */
div.stButton > button, div[data-testid="stDownloadButton"] > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-weight: bold;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
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
    # DOWNLOAD & TABEL RIWAYAT
    # =========================
    st.subheader("Riwayat Lengkap")
    
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data CSV",
        data=csv,
        file_name='data_hidroponik.csv',
        mime='text/csv',
    )
    
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Belum ada data histori yang tersimpan.")
