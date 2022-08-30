import streamlit as st
import os

st.set_page_config(page_title="NEAR Directory - Your guide to the City of NEAR", page_icon="🌆", layout="wide")
st.title("NEAR Directory")
st.caption("Your guide to the City of NEAR")

shroomdk_key = os.getenv("SHROOMDK_KEY")
figment_key = os.getenv("FIGMENT_API_KEY")

st.write(shroomdk_key[:5])
st.write(figment_key[:5])