import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

def mostrar_menu():

    # Estado para mostrar/ocultar menú
    if "mostrar_menu" not in st.session_state:
        st.session_state.mostrar_menu = True

    # Botón para alternar visibilidad
    with st.sidebar:
        if st.button("Ocultar menú" if st.session_state.mostrar_menu else "Mostrar menú"):
            st.session_state.mostrar_menu = not st.session_state.mostrar_menu

    # Mostrar menú si el estado está activo
    if st.session_state.mostrar_menu:
        with st.sidebar:
            st.title("Menú Principal")
            opcion = st.radio("Selecciona una opción:", ["Ver Rutinas", "Crear Rutinas"])
    else:
        opcion = None

    # Mostrar contenido según opción
    if opcion == "Ver Rutinas":
        ver_rutinas()
    elif opcion == "Crear Rutinas":
        crear_rutinas()
