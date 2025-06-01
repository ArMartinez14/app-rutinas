import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

def mostrar_menu():
    # 👇 Esta configuración debe ir siempre al inicio

    # 📌 Mostrar logo desde base64 si existe
    if "LOGO_BASE64" in st.secrets:
        st.sidebar.image("data:image/png;base64," + st.secrets["LOGO_BASE64"], use_column_width=True)

    # 🔄 Inicializar estado
    if "pagina_actual" not in st.session_state:
        st.session_state.pagina_actual = "Inicio"

    # 🎯 Barra lateral
    st.sidebar.markdown("## ¿Qué deseas hacer?")
    if st.sidebar.button("📋 Ver Rutinas"):
        st.session_state.pagina_actual = "Ver Rutinas"
    if st.sidebar.button("🛠️ Crear Rutina"):
        st.session_state.pagina_actual = "Crear Rutina"

    # 🔀 Mostrar contenido según navegación
    if st.session_state.pagina_actual == "Ver Rutinas":
        ver_rutinas()
    elif st.session_state.pagina_actual == "Crear Rutina":
        crear_rutinas()
    else:
        st.markdown("<h3 style='text-align:center'>Bienvenido a Motion Center</h3>", unsafe_allow_html=True)
