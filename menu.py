from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas
import streamlit as st

def mostrar_menu():
    st.sidebar.title("🏋️ Menú principal")
    opciones = ["🏠 Inicio", "👀 Ver Rutinas", "✏️ Crear Rutina"]
    eleccion = st.sidebar.radio("¿Qué deseas hacer?", opciones)

    if eleccion == "🏠 Inicio":
        st.title("Bienvenido a Motion Center")
        st.markdown("Selecciona una opción del menú para comenzar.")
    elif eleccion == "👀 Ver Rutinas":
        ver_rutinas()
    elif eleccion == "✏️ Crear Rutina":
        crear_rutinas()
