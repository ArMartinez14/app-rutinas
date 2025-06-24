# menu.py
import streamlit as st

def show_menu():
    with st.sidebar:
        st.markdown("📌 **Menú de Navegación**")
        st.page_link("app.py", label="🏠 Inicio")
        st.page_link("pages/1_ver_rutinas.py", label="🔍 Ver Rutinas")
        st.page_link("pages/2_crear_rutinas.py", label="📝 Crear Rutinas")
        st.page_link("pages/3_borrar_rutinas.py", label="🗑️ Borrar Rutinas")
