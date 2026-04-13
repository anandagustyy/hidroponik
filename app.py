import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

st.title("Monitoring Hidroponik")

# Refresh tiap 2 detik
st_autorefresh(interval=2000, key="datarefresh")

url = "http://127.0.0.1:5000/data"

response = requests.get(url)
data = response.json()

ph = data["ph"]
ppm = data["ppm"]

st.metric("pH", round(ph, 2))
st.metric("PPM", round(ppm, 2))