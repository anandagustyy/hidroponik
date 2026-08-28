import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time
import random
from datetime import datetime, timedelta
import pytz

# CONFIG
st.set_page_config(layout="wide", page_title="Smart Hydroponic Monitoring")

# ==========================================
# KONFIGURASI BOT TELEGRAM (AKTIF)
# ==========================================
TELEGRAM_BOT_TOKEN = "8946114296:AAH_T6wvZbBtkOmlKD-yDzVLrYQlDP0Yf4k"
TELEGRAM_CHAT_ID   = "5375308615"

def send_telegram_alert(message):
    try:
        url_tele = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url_tele, data=payload, timeout=5)
    except Exception:
        pass

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

# AUTO REFRESH SETIAP 10 DETIK
st_autorefresh(interval=10000, key="refresh_sensor_data")

st.title("Smart Hydroponic Monitoring")

# FIREBASE INTERFACE (Dengan Anti-Cache Query)
timestamp_param = int(time.time() * 1000)
url = f"https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json?t={timestamp_param}"
history_url = f"https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/history.json?t={timestamp_param}"
http_headers = {"Cache-Control": "no-cache"}

# ==========================================
# FITUR GENERATOR & RESET DATA DI SIDEBAR
# ==========================================
with st.sidebar:
    st.subheader("Panel Kontrol Data")
    
    # 1. Tombol Generate Data Simulasi
    if st.button("Generate & Tambah Data (24 - 28 Ags)", use_container_width=True):
        wib = pytz.timezone('Asia/Jakarta')
        start_dt = wib.localize(datetime(2026, 8, 24, 22, 35, 7))
        end_dt = wib.localize(datetime(2026, 8, 28, 23, 35, 7))

        current_ph = 5.91
        current_ppm = 768
        interval = timedelta(minutes=30)
        current_dt = start_dt

        payload = {}
        total_data = 0

        while current_dt <= end_dt:
            noise_ph = round(random.uniform(-0.03, 0.03), 2)
            noise_ppm = random.randint(-6, 6)
            
            drift_ph = 0.0
            drift_ppm = 0.0
            
            # Simulasi Fluktuasi Naik pH (~6.65)
            if current_dt.day == 25 and 10 <= current_dt.hour < 13:
                drift_ph = 0.18
            elif current_dt.day == 25 and 13 <= current_dt.hour < 16:
                drift_ph = -0.16
                
            # Simulasi Fluktuasi Turun pH (~5.40)
            elif current_dt.day == 26 and 2 <= current_dt.hour < 5:
                drift_ph = -0.18
            elif current_dt.day == 26 and 5 <= current_dt.hour < 8:
                drift_ph = 0.16
                
            # Simulasi Fluktuasi PPM Nutrisi
            elif current_dt.day == 27 and 14 <= current_dt.hour < 17:
                drift_ppm = -50
            elif current_dt.day == 27 and 17 <= current_dt.hour < 20:
                drift_ppm = 60
                
            pull_ph = (6.00 - current_ph) * 0.12 if drift_ph == 0 else 0
            pull_ppm = (770 - current_ppm) * 0.12 if drift_ppm == 0 else 0
            
            current_ph += noise_ph + pull_ph + drift_ph
            current_ppm += noise_ppm + pull_ppm + drift_ppm
            
            # Batas Nilai
            current_ph = max(5.40, min(6.65, current_ph))
            current_ppm = max(540, min(1035, current_ppm))
            
            current_ph = round(current_ph, 2)
            current_ppm = int(round(current_ppm))
            
            timestamp_ms = int(current_dt.timestamp() * 1000)
            payload[f"log_{timestamp_ms}"] = {
                "ph": current_ph,
                "ppm": current_ppm,
                "time": timestamp_ms
            }
            current_dt += interval
            total_data += 1

        # Menggunakan PATCH agar data manual sebelumnya tidak terhapus
        res = requests.patch(history_url, json=payload)
        if res.status_code == 200:
            st.success(f"Berhasil menambahkan {total_data} baris data ke Firebase!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Gagal mengunggah data ke Firebase.")

    # 2. Tombol Hapus HANYA Data Generate (Data Manual Lama Aman)
    if st.button("Hapus Hanya Data Generate", type="primary", use_container_width=True):
        wib = pytz.timezone('Asia/Jakarta')
        start_dt = wib.localize(datetime(2026, 8, 24, 22, 35, 7))
        end_dt = wib.localize(datetime(2026, 8, 28, 23, 35, 7))
        interval = timedelta(minutes=30)
        current_dt = start_dt

        # Mengirim payload null ke setiap key generate untuk menghapusnya secara selektif
        delete_payload = {}
        while current_dt <= end_dt:
            timestamp_ms = int(current_dt.timestamp() * 1000)
            delete_payload[f"log_{timestamp_ms}"] = None
            current_dt += interval

        del_res = requests.patch(history_url, json=delete_payload)
        if del_res.status_code == 200:
            st.success("Berhasil menghapus data generate. 58 data manual kamu tetap aman!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Gagal menghapus data dari Firebase.")

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

# ==========================================
# EVALUASI ALARM (pH: 5.50 - 6.50 | PPM: 560 - 1000)
# ==========================================
ph_is_abnormal = (ph < 5.50 or ph > 6.50)
ppm_is_abnormal = (ppm < 560 or ppm > 1000)

alert_messages = []
if ph < 5.50:
    alert_messages.append(f"pH Terlalu Asam ({ph:.2f})")
elif ph > 6.50:
    alert_messages.append(f"pH Terlalu Basa ({ph:.2f})")

if ppm < 560:
    alert_messages.append(f"Nutrisi Kurang ({ppm} PPM)")
elif ppm > 1000:
    alert_messages.append(f"Nutrisi Berlebih ({ppm} PPM)")

# Banner Peringatan di Dashboard Web
if alert_messages:
    st.error(f"PERINGATAN SISTEM: {' & '.join(alert_messages)}! Segera lakukan penyesuaian.")

# Kirim Notifikasi Telegram (Cooldown 10 menit)
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0

current_time = time.time()
if (ph_is_abnormal or ppm_is_abnormal) and (current_time - st.session_state.last_alert_time > 600):
    st.session_state.last_alert_time = current_time
    tele_msg = (
        f"*PERINGATAN SISTEM HIDROPONIK*\n\n"
        f"Terdeteksi kondisi di luar ambang batas ideal:\n"
        f"• Nilai pH: *{ph:.2f}* (Batas: 5.50 - 6.50)\n"
        f"• Nilai TDS: *{ppm} PPM* (Batas: 560 - 1000 PPM)\n"
        f"• Keterangan: *{', '.join(alert_messages)}*\n\n"
        f"Waktu: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    send_telegram_alert(tele_msg)

# Logika Sinyal pH
if 0 <= ph < 3.00:
    ph_level, ph_color, ph_status = 1, "#FF0000", "Terlalu Asam"
elif 3.01 <= ph < 5.49:
    ph_level, ph_color, ph_status = 2, "#FFA500", "Asam"
elif 5.50 <= ph <= 6.50:
    ph_level, ph_color, ph_status = 3, "#00FF00", "Ideal"
elif 6.51 <= ph <= 8.50:
    ph_level, ph_color, ph_status = 4, "#00FFFF", "Basa"
else:
    ph_level, ph_color, ph_status = 5, "#0000FF", "Terlalu Basa"

# Logika Sinyal PPM
if 0 <= ppm <= 200:
    ppm_level, ppm_color, ppm_status = 1, "#FF0000", "Nutrisi Sangat Rendah"
elif 201 <= ppm < 560:
    ppm_level, ppm_color, ppm_status = 2, "#FFA500", "Kekurangan Nutrisi"
elif 560 <= ppm <= 1000:
    ppm_level, ppm_color, ppm_status = 3, "#00FF00", "Ideal"
elif 1001 <= ppm <= 1300:
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
st.write(f"Status pH: **{ph_status}** (Rentang Batas: 5.50 - 6.50)")
st.write(f"Status PPM: **{ppm_status}** (Rentang Batas: 560 - 1000 PPM)")

st.divider()

# PROSES DATA HISTORI DARI FIREBASE
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
    # Konversi waktu ke WIB (Asia/Jakarta)
    df["time"] = pd.to_datetime(df["time"], unit='ms', utc=True).dt.tz_convert('Asia/Jakarta')
    df["ph"] = pd.to_numeric(df["ph"], errors='coerce')
    df["ppm"] = pd.to_numeric(df["ppm"], errors='coerce')
    
    df = df.dropna(subset=["time", "ph", "ppm"])
    df = df.sort_values("time")
    
    df_display = df.copy()
    df_display["time"] = df_display["time"].dt.strftime('%Y-%m-%d %H:%M:%S')

    # GRAFIK MONITORING
    st.subheader("Grafik Monitoring")
    graph_col1, graph_col2 = st.columns(2)
    
    with graph_col1:
        st.write("**Grafik pH**")
        st.line_chart(df.set_index("time")["ph"])
        
    with graph_col2:
        st.write("**Grafik PPM**")
        st.line_chart(df.set_index("time")["ppm"])

    # TABEL RIWAYAT LENGKAP (Tunggal & Terbaru di Atas)
    st.subheader("Riwayat Lengkap")
    df_table = df_display.sort_values("time", ascending=False).reset_index(drop=True)
    st.dataframe(df_table, use_container_width=True)
else:
    st.info("Belum ada data histori yang tersimpan. Menunggu data baru dari ESP32...")
