import streamlit as st
from ver_rutinas import ver_rutinas
from crear_rutinas import crear_rutinas

# La configuración de página debe ir primero
st.set_page_config(page_title="Motion Center", layout="wide")

def mostrar_menu():
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
        st.markdown("""
            <div style='text-align: center; margin-top: 3rem;'>
                <img src="data:image/png;base64,{}" style="max-height:80px;" />
                <h2 style='color: white;'>Bienvenido a Motion Center</h2>
                <p style='color: gray;'>Selecciona una opción del menú para comenzar</p>
            </div>
        """.format(st.secrets["LOGO_BASE64"].strip()), unsafe_allow_html=True)

# Ejecutar el menú si este archivo es app.py
if __name__ == "__main__":
    mostrar_menu()
