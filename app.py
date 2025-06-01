import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

st.set_page_config(page_title="Motion Center", layout="wide")

st.sidebar.title("Menú Principal")

col1, col2 = st.sidebar.columns(1)

if col1.button("Ver Rutinas"):
    st.session_state['opcion'] = "Ver Rutinas"
elif col2.button("Crear Rutinas"):
    st.session_state['opcion'] = "Crear Rutinas"

# Mostrar opción seleccionada o mensaje de bienvenida
if 'opcion' in st.session_state:
    if st.session_state['opcion'] == "Ver Rutinas":
        ver_rutinas()
    elif st.session_state['opcion'] == "Crear Rutinas":
        crear_rutinas()
else:
    st.markdown("""
        <div style='text-align: center; margin-top: 100px;'>
            <img src='https://i.ibb.co/YL1HbLj/motion-logo.png' width='100'>
            <h1>Bienvenido a Motion Center</h1>
            <p style='font-size:18px;'>Selecciona una opción del menú para comenzar</p>
        </div>
    """, unsafe_allow_html=True)
