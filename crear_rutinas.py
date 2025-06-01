import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime

# Inicializar Firebase si no está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_CREDENTIALS"])
    firebase_admin.initialize_app(cred)

db = firestore.client()

def crear_rutinas():
    st.title("📅 Crear nueva rutina")

    # Obtener lista de usuarios
    docs = db.collection("usuarios").stream()
    usuarios = [doc.to_dict() for doc in docs if doc.exists]
    nombres = sorted(set(u.get("nombre", "") for u in usuarios))

    # Nombre del cliente con sugerencias
    if "nombre_cliente" not in st.session_state:
        st.session_state.nombre_cliente = ""
    if "correo_cliente" not in st.session_state:
        st.session_state.correo_cliente = ""

    nombre_input = st.text_input("👤 Nombre del cliente:", value=st.session_state.nombre_cliente)

    coincidencias = [n for n in nombres if nombre_input.lower() in n.lower()]
    nombre_sel = st.selectbox("O selecciona de la lista:", coincidencias if coincidencias else nombres)

    if nombre_sel and nombre_sel != st.session_state.nombre_cliente:
        st.session_state.nombre_cliente = nombre_sel
        st.session_state.correo_cliente = next((u["correo"] for u in usuarios if u.get("nombre") == nombre_sel), "")

    correo = st.text_input("✉️ Correo del cliente:", value=st.session_state.correo_cliente)

    # Mostrar el correo automáticamente
    correo = st.text_input("✉️ Correo del cliente:", value=correo_auto)

    fecha_inicio = st.date_input("📆 Fecha de inicio de rutina:", value=datetime.today())
    semanas = st.number_input("🔁 Semanas de duración:", min_value=1, max_value=12, value=4)
    entrenador = st.text_input("🏋️ Nombre del entrenador responsable:")

    st.markdown("---")
    st.info("🛠️ Aquí irá la lógica para cargar ejercicios por día")

    # Aquí seguiremos agregando más campos y lógica en los siguientes pasos
