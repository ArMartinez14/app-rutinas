import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

def mostrar_menu():
    st.set_page_config(page_title="Motion Center", layout="centered")
    opcion = st.selectbox("📋 ¿Qué deseas hacer?", ["Ver Rutinas", "Crear Rutinas"])

    if opcion == "Ver Rutinas":
        ver_rutinas()
    elif opcion == "Crear Rutinas":
        crear_rutinas()
