import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

st.set_page_config(page_title="Motion Center", layout="wide")

# Inicializar el estado de la sesión si no existe
if 'opcion' not in st.session_state:
    st.session_state.opcion = None

# Título del sidebar
st.sidebar.title("Menú principal")

# Botones como menú lateral
if st.sidebar.button("Ver Rutinas"):
    st.session_state.opcion = "Ver Rutinas"
if st.sidebar.button("Crear Rutinas"):
    st.session_state.opcion = "Crear Rutinas"

# Mostrar la opción seleccionada o el mensaje de bienvenida
if st.session_state.opcion:
    if st.session_state.opcion == "Ver Rutinas":
        ver_rutinas()
    elif st.session_state.opcion == "Crear Rutinas":
        crear_rutinas()
else:
    st.markdown("""
        <div style='text-align: center; margin-top: 100px;'>
            <img src='https://i.ibb.co/YL1HbLj/motion-logo.png' width='100'>
            <h1>Bienvenido a Motion Center</h1>
            <p style='font-size:18px;'>Selecciona una opción del menú para comenzar</p>
        </div>
    """, unsafe_allow_html=True)
