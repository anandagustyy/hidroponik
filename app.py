import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")

# =========================
# STYLE DARK MODE
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

.block-container {
    color: white;
}

h1, h2, h3, h4, h5, h6, p, div {
    color: white !important;
}

div[data-testid="stAlert"] {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=30000, key="refresh")

st.title("🌱 Smart Hydroponic Monitoring")

# =========================
# FIREBASE
# =========================
url = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json"
history_url = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"

# =========================
# AMBIL DATA
# =========================
data = requests.get(url).json()

ph = data.get("ph", 0)
ppm = data.get("ppm", 0)

st.write("DEBUG PPM:", ppm)

# =========================
# SIMPAN HISTORI
# =========================
new_data = {
    "time": str(datetime.now()),
    "ph": ph,
    "ppm": ppm
}

requests.post(history_url, json=new_data)

# =========================
# GAUGE PPM (HARUS DI ATAS)
# =========================
def ppm_gauge(ppm):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ppm,
        title={'text': "PPM", 'font': {'color': "white"}},
        number={'font': {'color': "white"}},
        gauge={
            'axis': {
                'range': [0, 2000],
                'tickvals': [0, 200, 500, 1000, 1500, 2000],
                'ticktext': ['0', '200', '500', '1000', '1500', '2000'],
                'tickcolor': "white",
                'tickfont': {'color': "white"}
            },
            'bar': {
                'color': "white",
                'thickness': 0.08
            },
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, 200], 'color': "red"},
                {'range': [200, 500], 'color': "yellow"},
                {'range': [500, 1000], 'color': "green"},
                {'range': [1000, 2000], 'color': "blue"},
            ],
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
    )

    return fig

# =========================
# INDIKATOR PH
# =========================
def ph_indicator(ph):
    bars = ["⬜","⬜","⬜","⬜","⬜"]

    if ph < 2:
        bars[0] = "🟥"
    elif ph < 4:
        bars[0] = "🟥"
        bars[1] = "🟧"
    elif ph < 6:
        bars[0] = "🟥"
        bars[1] = "🟧"
        bars[2] = "🟨"
    elif ph < 8:
        bars[0] = "🟥"
        bars[1] = "🟧"
        bars[2] = "🟨"
        bars[3] = "🟩"
    elif ph < 10:
        bars[0] = "🟥"
        bars[1] = "🟧"
        bars[2] = "🟨"
        bars[3] = "🟩"
        bars[4] = "🟦"
    else:
        bars = ["🟦","🟦","🟦","🟦","🟦"]

    return "".join(bars)

# =========================
# LAYOUT
# =========================
col1, col2 = st.columns([1,2])

# pH
with col1:
    st.subheader("pH")
    st.metric("Nilai pH", round(ph,2))
    st.write(ph_indicator(ph))

# PPM
with col2:
    st.subheader("PPM")
    st.plotly_chart(ppm_gauge(ppm), use_container_width=True)

# =========================
# NOTIFIKASI
# =========================
if ph < 5:
    st.error("⚠️ pH terlalu asam!")
elif ph > 8:
    st.warning("⚠️ pH terlalu basa!")
else:
    st.success("✅ pH normal")

if ppm < 200:
    st.error("⚠️ Nutrisi sangat rendah")
elif ppm < 500:
    st.warning("⚠️ Nutrisi rendah")
elif ppm <= 1000:
    st.success("✅ Nutrisi ideal")
else:
    st.info("⚠️ Nutrisi terlalu tinggi")

# =========================
# HISTORI
# =========================
history_data = requests.get(history_url).json()

rows = []
if history_data:
    for key, value in history_data.items():
        rows.append(value)

df = pd.DataFrame(rows)

# =========================
# GRAFIK
# =========================
st.subheader("📊 Grafik Monitoring")

if not df.empty:
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    st.line_chart(df.set_index("time")[["ph","ppm"]])

# =========================
# DOWNLOAD
# =========================
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Data CSV",
    data=csv,
    file_name='data_hidroponik.csv',
    mime='text/csv',
)

# =========================
# TABEL
# =========================
st.subheader("📁 Riwayat Lengkap")
st.dataframe(df)