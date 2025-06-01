import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime

# === CONFIGURACIÓN DE LA PÁGINA (debe ir al inicio del primer archivo ejecutado) ===
#st.set_page_config(page_title="Motion Center", layout="wide")

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_CREDENTIALS"])
    firebase_admin.initialize_app(cred)

db = firestore.client()

def crear_rutinas():
    st.title("📅 Crear nueva rutina")

    # === OBTENER USUARIOS DESDE FIRESTORE ===
    docs = db.collection("usuarios").stream()
    usuarios = [doc.to_dict() for doc in docs if doc.exists]

    nombres = sorted(set(u.get("nombre", "") for u in usuarios))

    # === INPUT DE NOMBRE CON SUGERENCIAS ===
    nombre_input = st.text_input("👤 Escribe el nombre del cliente:")
    coincidencias = [n for n in nombres if nombre_input.lower() in n.lower()]

    if coincidencias:
        nombre_sel = st.selectbox("🔎 Selecciona de la lista:", coincidencias)
    else:
        nombre_sel = ""

    # === AUTOCOMPLETAR CORREO ===
    correo_auto = ""
    if nombre_sel:
        correo_auto = next((u.get("correo", "") for u in usuarios if u.get("nombre") == nombre_sel), "")

    correo = st.text_input("✉️ Correo del cliente:", value=correo_auto)

    # === OTROS CAMPOS ===
    fecha_inicio = st.date_input("📆 Fecha de inicio de rutina:", value=datetime.today())
    semanas = st.number_input("🔁 Semanas de duración:", min_value=1, max_value=12, value=4)
    entrenador = st.text_input("🏋️ Nombre del entrenador responsable:")

    st.markdown("---")
    st.info("🛠️ Aquí irá la lógica para cargar ejercicios por día")
