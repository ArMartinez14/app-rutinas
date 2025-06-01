import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

def mostrar_menu():
    st.set_page_config(page_title="Motion Center", layout="wide")

    # Reducir el ancho de la barra lateral
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            min-width: 180px;
            max-width: 180px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("📋 Menú principal")

    # Botones en lugar de selectbox
    ver = st.sidebar.button("Ver Rutinas")
    crear = st.sidebar.button("Crear Rutinas")

    if ver:
        ver_rutinas()
    elif crear:
        crear_rutinas()
