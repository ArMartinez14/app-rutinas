import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas
from evaluaciones import registrar_evaluacion
from borrar_rutinas import borrar_rutinas  # 👈 IMPORTAR TU ARCHIVO
from editar_rutinas import editar_rutinas

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
if st.sidebar.button("Evaluaciones"):
    st.session_state.opcion = "Evaluaciones"
if st.sidebar.button("Borrar Rutinas"):
    st.session_state.opcion = "Borrar Rutinas"
if st.sidebar.button("Editar Rutinas"):
    st.session_state.opcion = "Editar Rutinas"

# Mostrar la opción seleccionada o el mensaje de bienvenida
if st.session_state.opcion:
    if st.session_state.opcion == "Ver Rutinas":
        ver_rutinas()
    elif st.session_state.opcion == "Crear Rutinas":
        crear_rutinas()
    elif st.session_state.opcion == "Evaluaciones":
        registrar_evaluacion()
    elif st.session_state.opcion == "Borrar Rutinas":
        borrar_rutinas()
    elif st.session_state.opcion == "Editar Rutinas":
        editar_rutinas()

else:
    st.markdown("""
        <div style='text-align: center; margin-top: 100px;'>
            <img src='https://i.ibb.co/YL1HbLj/motion-logo.png' width='100'>
            <h1>Bienvenido a Motion Center</h1>
            <p style='font-size:18px;'>Selecciona una opción del menú para comenzar</p>
        </div>
        """, unsafe_allow_html=True)