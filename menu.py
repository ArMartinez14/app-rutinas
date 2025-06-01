import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

def mostrar_menu():
    st.image("logo_motion.png", use_column_width=True)
    opcion = st.selectbox("📋 ¿Qué deseas hacer?", ["Ver Rutinas", "Crear Rutinas"])

    if opcion == "Ver Rutinas":
        ver_rutinas()
    elif opcion == "Crear Rutinas":
        crear_rutinas()
