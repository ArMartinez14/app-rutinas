import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import menu  # Tu archivo de navegación
import ver_rutinas  # Tu página de ver rutinas
import crear_rutinas
import editar_rutinas
import borrar_rutinas
import evaluaciones
import rutinas_admin

# ✅ Inicializar Firebase (ajusta con tu credencial)
if not firebase_admin._apps:
    cred = credentials.Certificate("credenciales.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# === CONFIG PÁGINA ===
st.set_page_config(page_title="📅 App Rutinas", layout="wide")

st.title("📅 App de Rutinas")

# === 1️⃣ Pide correo al abrir ===
correo_input = st.text_input("🔑 Ingresa tu correo:", key="correo_input")
if not correo_input:
    st.stop()

correo = correo_input.strip().lower()
doc_user = db.collection("usuarios").document(correo).get()

if not doc_user.exists:
    st.error("❌ Este correo no está registrado.")
    st.stop()

rol = doc_user.get("rol").lower()

# === 2️⃣ Define opciones de menú ===
if rol in ["entrenador", "admin", "administrador"]:
    opciones = [
        "Ver Rutinas",
        "Crear Rutinas",
        "Editar Rutinas",
        "Borrar Rutinas",
        "Evaluaciones",
        "Admin Rutinas"
    ]
else:
    opciones = ["Ver Rutinas"]

# === 3️⃣ Mostrar menú ===
opcion = st.sidebar.selectbox("📌 Navegación", opciones)

# === 4️⃣ Mostrar contenido según opción ===
if opcion == "Ver Rutinas":
    ver_rutinas.app(correo, rol)
elif opcion == "Crear Rutinas":
    crear_rutinas.app()
elif opcion == "Editar Rutinas":
    editar_rutinas.app()
elif opcion == "Borrar Rutinas":
    borrar_rutinas.app()
elif opcion == "Evaluaciones":
    evaluaciones.app()
elif opcion == "Admin Rutinas":
    rutinas_admin.app()