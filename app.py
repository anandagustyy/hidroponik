import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=2000, key="refresh")

st.title("Monitoring Hidroponik")

url = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json"

data = requests.get(url).json()

ph = data["ph"]
ppm = data["ppm"]

st.metric("pH", round(ph, 2))
st.metric("PPM", round(ppm, 0))