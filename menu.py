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
    else:
        st.markdown("<br><br><h2 style='text-align:center;'>Bienvenido a Motion Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Selecciona una opción desde el menú lateral para comenzar.</p>", unsafe_allow_html=True)
        st.image("logo_motion.png", use_column_width="auto")
