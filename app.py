# app.py
import streamlit as st

st.set_page_config(page_title="App de Rutinas y Agenda", layout="wide")

st.title("🏠 App de Rutinas y Agenda")

# Inputs de login
correo = st.text_input("✉️ Ingresa tu correo")
rol = st.selectbox("Selecciona tu rol", ["deportista", "entrenador", "admin"])

if st.button("Iniciar Sesión"):
    st.session_state["correo"] = correo.strip()
    st.session_state["rol"] = rol.strip()
    st.success(f"✅ Sesión iniciada como {rol} — {correo}")

# Menú lateral igual en todas
with st.sidebar:
    st.markdown("📌 **Menú**")
    st.page_link("app.py", label="🏠 Inicio")
    st.page_link("pages/1_Crear_Rutinas.py", label="📝 Crear Rutinas")
    st.page_link("pages/2_Ver_Rutinas.py", label="🔍 Ver Rutinas")
