import streamlit as st
from menu import show_menu

st.set_page_config(page_title="App de Rutinas", layout="wide")

st.title("🏠 App de Rutinas")

# === Inputs para sesión ===
correo = st.text_input("🔑 Ingresa tu correo")
rol = st.selectbox("Selecciona tu rol", ["deportista", "entrenador", "admin"])

if st.button("Iniciar Sesión"):
    st.session_state["correo"] = correo.strip()
    st.session_state["rol"] = rol.strip()
    st.success(f"✅ Sesión iniciada como {rol} — {correo}")

show_menu()
