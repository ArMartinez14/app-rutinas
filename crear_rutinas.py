import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime

# === CONFIGURACIÓN DE LA PÁGINA (debe ir al inicio del primer archivo ejecutado) ===
st.set_page_config(page_title="Motion Center", layout="wide")

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

    nombre_sel = st.selectbox("🔎 Selecciona de la lista:", coincidencias) if coincidencias else ""

    # === AUTOCOMPLETAR CORREO ===
    correo_auto = next((u.get("correo", "") for u in usuarios if u.get("nombre") == nombre_sel), "")
    correo = st.text_input("✉️ Correo del cliente:", value=correo_auto)

    # === OTROS CAMPOS ===
    fecha_inicio = st.date_input("📆 Fecha de inicio de rutina:", value=datetime.today())
    semanas = st.number_input("🔁 Semanas de duración:", min_value=1, max_value=12, value=4)
    entrenador = st.text_input("🏋️ Nombre del entrenador responsable:")

    st.markdown("---")
    st.subheader("🗓️ Días de entrenamiento")

    dias = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]
    tabs = st.tabs(dias)

    for i, tab in enumerate(tabs):
        with tab:
            dia_key = f"rutina_dia_{i+1}"
            if dia_key not in st.session_state:
                st.session_state[dia_key] = []

            st.write(f"Ejercicios para {dias[i]}")

            circuito = st.selectbox("🔤 Circuito", ["A", "B", "C", "D", "E", "F"], key=f"circuito_{i}")
            ejercicio = st.text_input("🏋️ Nombre del ejercicio", key=f"ejercicio_{i}")
            series = st.number_input("🔁 Series", min_value=1, max_value=10, value=3, key=f"series_{i}")
            repeticiones = st.text_input("🔢 Repeticiones", key=f"reps_{i}")
            peso = st.text_input("🏋️ Peso (kg)", key=f"peso_{i}")
            tipo = st.text_input("📘 Tipo (ej. fuerza, movilidad…)", key=f"tipo_{i}")
            progresion = st.text_input("📈 Nombre progresión", key=f"prog_{i}")

            if st.button(f"💾 Guardar {dias[i]}", key=f"guardar_{i}"):
                st.session_state[dia_key].append({
                    "circuito": circuito,
                    "ejercicio": ejercicio,
                    "series": series,
                    "repeticiones": repeticiones,
                    "peso": peso,
                    "tipo": tipo,
                    "progresion": progresion
                })
                st.success("Ejercicio guardado en memoria")

            if st.session_state[dia_key]:
                st.markdown("### ✅ Ejercicios guardados")
                for idx, ex in enumerate(st.session_state[dia_key]):
                    st.markdown(f"{idx+1}. **{ex['circuito']} - {ex['ejercicio']}**: {ex['series']}x{ex['repeticiones']} @ {ex['peso']}kg")

    st.markdown("---")
    st.button("🚀 Generar rutina completa")  # Aún no implementado
