import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

st.sidebar.title("Menú Principal")
opcion = st.sidebar.radio("Selecciona una opción:", ["Ver Rutinas", "Crear Rutinas"])

if opcion == "Ver Rutinas":
    ver_rutinas()
elif opcion == "Crear Rutinas":
    crear_rutinas()

