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
# STYLE DARK MODE (DIPERBAIKI)
# =========================
# Memperbaiki kontras warna teks di dalam alert box agar tidak tabrakan dengan warna background bawaan Streamlit
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

.block-container {
    color: #ffffff;
}

h1, h2, h3, h4, h5, h6, p, div {
    color: #ffffff;
}

/* Memastikan teks di dalam alert box (success, info, warning, error) tetap terbaca dengan jelas */
div[data-testid="stAlert"] p {
    color: #000000 !important;
    font-weight: 500;
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
# LAYOUT UTAMA (ANGKA METRIK)
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("pH")
    st.metric(label="Nilai pH Saat Ini", value=f"{ph:.2f}")

with col2:
    st.subheader("PPM")
    st.metric(label="Nilai PPM Saat Ini", value=f"{ppm} ppm")

# =========================
# NOTIFIKASI STATUS & WARNA (DIYESUAIKAN DENGAN STANDAR)
# =========================
st.subheader("Status Nutrisi dan Keasaman")

# Logika Pewarnaan pH (Merah = Bahaya/Asam, Kuning = Peringatan/Basa, Hijau = Ideal)
if ph < 5.5:
    st.error("Status: pH terlalu asam (kurang dari 5.5)")
elif ph > 6.5:
    st.warning("Status: pH terlalu basa (lebih dari 6.5)")
else:
    st.success("Status: pH normal (ideal untuk tanaman)")

# Logika Pewarnaan PPM (Merah = Kurang, Hijau = Ideal, Biru/Kuning = Terlalu Tinggi)
if ppm < 500:
    st.error("Status: Nutrisi terlalu rendah (kurang dari 500 ppm)")
elif 500 <= ppm <= 1200:
    st.success("Status: Nutrisi ideal (500 - 1200 ppm)")
else:
    st.info("Status: Nutrisi terlalu tinggi (lebih dari 1200 ppm)")

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
        st.write("Tren Nilai pH")
        st.line_chart(df.set_index("time")["ph"])
        
    with graph_col2:
        st.write("Tren Nilai PPM")
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
