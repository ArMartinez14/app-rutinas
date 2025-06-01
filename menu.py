import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

def mostrar_menu():
    # Eliminar espacio superior visualmente
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.image("data:image/png;base64," + st.secrets["LOGO_BASE64"], use_column_width=True)

    opcion = st.sidebar.selectbox("📋 ¿Qué deseas hacer?", ["Ver Rutinas", "Crear Rutinas"])

    if opcion == "Ver Rutinas":
        ver_rutinas()
    elif opcion == "Crear Rutinas":
        crear_rutinas()
