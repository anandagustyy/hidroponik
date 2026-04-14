import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from datetime import datetime

# AUTO REFRESH
st_autorefresh(interval=2000, key="refresh")

# BACKGROUND
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1501004318641-b39e6451bec6");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌱 Smart Hydroponic Monitoring")

# FIREBASE URL
url = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json"

# AMBIL DATA
data = requests.get(url).json()
ph = data.get("ph", 0)
ppm = data.get("ppm", 0)

# =======================
# 📶 INDIKATOR PH (SIGNAL)
# =======================
def ph_indicator(ph):
    bars = ["⬜", "⬜", "⬜", "⬜", "⬜"]

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

col1, col2 = st.columns(2)

with col1:
    st.subheader("pH")
    st.metric("Nilai pH", round(ph,2))
    st.write(ph_indicator(ph))

# =======================
# 🧭 GAUGE PPM
# =======================
def ppm_gauge(ppm):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ppm,
        title={'text': "PPM"},
        gauge={
            'axis': {'range': [0, 2000]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 200], 'color': "red"},
                {'range': [200, 500], 'color': "yellow"},
                {'range': [500, 1000], 'color': "green"},
                {'range': [1000, 2000], 'color': "blue"},
            ],
        }
    ))
    return fig

with col2:
    st.plotly_chart(ppm_gauge(ppm), use_container_width=True)

# =======================
# 🔔 NOTIFIKASI
# =======================
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

# =======================
# 📊 GRAFIK REALTIME
# =======================
if "history" not in st.session_state:
    st.session_state.history = []

st.session_state.history.append({
    "time": datetime.now(),
    "ph": ph,
    "ppm": ppm
})

df = pd.DataFrame(st.session_state.history)

st.subheader("Grafik Realtime")

st.line_chart(df.set_index("time")[["ph","ppm"]])

# =======================
# 📁 HISTORI DATA
# =======================
st.subheader("📁 Riwayat Data")

st.dataframe(df.tail(20))