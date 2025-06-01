import streamlit as st

# ✅ Este debe ser el primer comando streamlit ejecutado en toda la app
st.set_page_config(page_title="Motion Center", layout="wide")

from menu import mostrar_menu

mostrar_menu()
