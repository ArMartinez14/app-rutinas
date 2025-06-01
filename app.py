import streamlit as st
from menu import mostrar_menu

# 🔸 ESTA LÍNEA DEBE IR PRIMERO
st.set_page_config(page_title="Motion Center", layout="wide")

if __name__ == "__main__":
    mostrar_menu()
