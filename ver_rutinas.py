import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import json
from utils import actualizar_progresiones_individual

def ver_rutinas():
    def ver_rutinas(correo=None, rol=None):
    # === INICIALIZAR FIREBASE SOLO UNA VEZ ===
        if not firebase_admin._apps:
            cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
        with open("/tmp/firebase.json", "w") as f:
            json.dump(cred_dict, f)
        cred = credentials.Certificate("/tmp/firebase.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # === Funciones utilitarias ===
    def obtener_fecha_lunes():
        hoy = datetime.now()
        lunes = hoy - timedelta(days=hoy.weekday())
        return lunes.strftime("%Y-%m-%d")

    def normalizar_correo(correo):
        return correo.strip().lower().replace("@", "_").replace(".", "_")

    def es_entrenador(rol):
        return rol.lower() in ["entrenador", "admin", "administrador"]

    def ordenar_circuito(ejercicio):
        orden = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
        return orden.get(ejercicio.get("circuito", ""), 99)

    @st.cache_data
    def cargar_rutinas_filtradas(correo, rol):
        if es_entrenador(rol):
            docs = db.collection("rutinas_semanales").stream()
        else:
            docs = db.collection("rutinas_semanales").where("correo", "==", correo).stream()
        return [doc.to_dict() for doc in docs]

    # === INPUT CORREO ===
    correo_input = st.text_input("🔑 Ingresa tu correo:", key="correo_input")
    if not correo_input:
        st.stop()

    correo_raw = correo_input.strip()
    correo = correo_raw.lower()
    if correo is None:
        correo_input = st.text_input("🔑 Ingresa tu correo:", key="correo_input")
        if not correo_input:
            st.stop()
        correo_raw = correo_input.strip()
        correo = correo_raw.lower()
    else:
        correo_raw = correo.strip()
        correo = correo_raw.lower()
    correo_norm = normalizar_correo(correo_raw)

    # === Verificar usuario ===
    doc_user = db.collection("usuarios").document(correo).get()
    if not doc_user.exists:
        st.error("❌ Este correo no está registrado.")
        st.stop()

    datos_usuario = doc_user.to_dict()
    nombre = datos_usuario.get("nombre", "Usuario")
    rol = datos_usuario.get("rol", "desconocido")
    if rol is None:
        rol = datos_usuario.get("rol", "desconocido")
    rol = rol.lower()

    mostrar_info = st.checkbox("👤 Mostrar información personal", value=True)
    if mostrar_info:
        st.success(f"Bienvenido {nombre} ({rol})")

    # === Cargar rutinas ===
    rutinas = cargar_rutinas_filtradas(correo, rol)
    if not rutinas:
        st.warning("⚠️ No se encontraron rutinas.")
        st.stop()

    if mostrar_info:
        clientes = sorted(set(r["cliente"] for r in rutinas if "cliente" in r))
        cliente_input = st.text_input("👤 Escribe el nombre del cliente:", key="cliente_input")
        cliente_opciones = [c for c in clientes if cliente_input.lower() in c.lower()]
        cliente_sel = st.selectbox("Selecciona cliente:", cliente_opciones if cliente_opciones else clientes, key="cliente_sel")

        rutinas_cliente = [r for r in rutinas if r.get("cliente") == cliente_sel]
        semanas = sorted({r["fecha_lunes"] for r in rutinas_cliente}, reverse=True)
        semana_actual = obtener_fecha_lunes()
        semana_sel = st.selectbox("📆 Semana", semanas, index=semanas.index(semana_actual) if semana_actual in semanas else 0, key="semana_sel")
    else:
        rutinas_cliente = rutinas
        semanas = sorted({r["fecha_lunes"] for r in rutinas_cliente}, reverse=True)
        semana_sel = obtener_fecha_lunes()