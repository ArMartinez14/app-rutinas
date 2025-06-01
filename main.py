# Archivo principal de la app
import streamlit as st
from menu import mostrar_menu

# Configuración general
def main():
    st.set_page_config(page_title="Motion Center", layout="centered")
    mostrar_menu()

if __name__ == "__main__":
    main()
