# === dashboard.py ===
import streamlit as st
import subprocess

st.set_page_config(page_title="Echo Ops Dashboard", layout="wide")

st.title("🌅 Echo Ops Dashboard")
st.markdown("Monitor and launch the autonomous Echo Temple marketing crew")

if st.button("Run CrewAI Marketing Team"):
    with st.spinner("Crew is running..."):
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        st.success("Crew completed!")
        st.code(result.stdout)
