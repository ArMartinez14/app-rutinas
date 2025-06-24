import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import menu  # si #tienes un archivo para la barra lateral, usa este import
import ver_rutinas
import crear_rutinas
import editar_rutinas
import borrar_rutinas
import evaluaciones
import rutinas_admin

# === ✅ CONFIGURAR PÁGINA ===
st.set_page_config(
    page_title="📅 App de Rutinas",
    page_icon="📅",
    layout="wide"
)

st.title("📅 App de Rutinas")

# === ✅ INICIALIZAR FIREBASE SOLO UNA VEZ ===
if not firebase_admin._apps:
    cred = credentials.Certificate("credenciales.json")  # Cambia por tu ruta si es necesario
    firebase_admin.initialize_app(cred)

db = firestore.client()

# === ✅ PEDIR CORREO UNA SOLA VEZ ===
correo_input = st.text_input("🔑 Ingresa tu correo:", key="correo_input")
if not correo_input:
    st.stop()

correo = correo_input.strip().lower()

# === ✅ VERIFICAR USUARIO ===
doc_user = db.collection("usuarios").document(correo).get()
if not doc_user.exists:
    st.error("❌ Este correo no está registrado.")
    st.stop()

rol = doc_user.get("rol").lower()

# === ✅ MOSTRAR OPCIONES SEGÚN ROL ===
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

opcion = st.sidebar.selectbox("📌 Menú", opciones)

# === ✅ MOSTRAR PÁGINAS SEGÚN SELECCIÓN ===
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
