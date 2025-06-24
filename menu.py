import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas
from evaluaciones import registrar_evaluacion


def mostrar_menu():
    st.set_page_config(page_title="Motion Center", layout="wide")

    st.sidebar.title("Menú Principal")
    opcion = st.sidebar.radio("Selecciona una opción:", ["Ver Rutinas", "Crear Rutinas", "Evaluaciones"])

    if opcion == "Ver Rutinas":
        ver_rutinas()
    elif opcion == "Crear Rutinas":
        crear_rutinas()
    elif opcion == "Evaluaciones":
        evaluacion()