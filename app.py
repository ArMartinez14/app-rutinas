import streamlit as st
from menu import show_menu

st.set_page_config(page_title="App de Rutinas", layout="wide")

st.title("🏠 App de Rutinas")

# === Inputs para sesión ===
correo = st.text_input("🔑 Ingresa tu correo")
#rol = st.selectbox("Selecciona tu rol", ["deportista", "entrenador", "admin"])

# ⛔ Esto no se debe pedir manualmente:
# rol = st.selectbox("Selecciona tu rol", ["deportista", "entrenador", "admin"])

# ✅ En su lugar:
rol = ""
if st.button("Iniciar Sesión"):
    # 👉 Aquí deberías consultar Firestore o tu base de usuarios
    # Simulamos que lo obtienes:
    rol = "deportista"  # Ejemplo hardcoded o busca en DB por correo
    st.session_state["correo"] = correo.strip()
    st.session_state["rol"] = rol
    st.success(f"✅ Sesión iniciada como {rol} — {correo}")

show_menu()
