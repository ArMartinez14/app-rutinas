import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date
import json
import unicodedata

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# === FUNCIÓN PARA NORMALIZAR NOMBRE ===
def normalizar_nombre(nombre):
    nombre = unicodedata.normalize("NFD", nombre)
    nombre = nombre.encode("ascii", "ignore").decode("utf-8")  # quitar tildes
    return " ".join(p.capitalize() for p in nombre.strip().split())

# === FUNCIÓN PRINCIPAL ===
def registrar_evaluacion():
    st.title("🧾 Evaluaciones del Cliente")

    # === TABS ===
    tab1, tab2, tab3 = st.tabs(["📝 Anamnesis", "🏋️ Evaluación Sala Pesas", "📏 Evaluaciones Físicas"])

    # === TAB 1: ANAMNESIS ===
    with tab1:
        st.subheader("Anamnesis del Cliente")

        with st.form("form_anamnesis"):
            nombre_input = st.text_input("Nombre completo del cliente")
            edad = st.number_input("Edad", min_value=1, max_value=120, step=1)
            deporte = st.text_input("Deporte")
            historial = st.text_area("Historial deportivo")
            lesiones = st.text_area("Lesiones relevantes")
            objetivo = st.text_area("Objetivo del entrenamiento")
            competiciones = st.text_area("Competiciones", placeholder="Competencias pasadas o futuras")
            nutricion = st.text_area("Nutrición actual")
            experiencia_pesas = st.selectbox("¿Tiene experiencia en sala de pesas?", ["", "Sí", "No", "Poca experiencia"])
            como_llego = st.text_input("¿Cómo llegó a nosotros?")

            submit = st.form_submit_button("Guardar evaluación")

        if submit:
            if not nombre_input:
                st.warning("⚠️ Debes ingresar el nombre.")
                return

            nombre = normalizar_nombre(nombre_input)

            evaluacion_data = {
                "nombre": nombre,
                "edad": edad,
                "deporte": deporte,
                "historial_deportivo": historial,
                "lesiones": lesiones,
                "objetivo": objetivo,
                "competiciones": competiciones,
                "nutricion": nutricion,
                "experiencia_sala_pesas": experiencia_pesas,
                "como_llego": como_llego,
                "fecha": str(date.today())
            }

            doc_id = f"{nombre.lower().replace(' ', '_')}_{date.today()}"
            db.collection("evaluaciones").document(doc_id).set(evaluacion_data)

            st.success(f"✅ Evaluación guardada correctamente para {nombre}.")

    # === TAB 2: SALA PESAS ===
    with tab2:
        st.subheader("🏋️ Evaluación en Sala de Pesas")
        st.info("Aquí podrás registrar tests y observaciones relacionados al rendimiento en ejercicios de fuerza. (Próximamente)")

    # === TAB 3: EVALUACIONES FÍSICAS ===
    with tab3:
        st.subheader("📏 Evaluaciones Físicas y Rangos de Movimiento")
        st.info("Aquí se registrarán datos como peso, altura, IMC, rangos articulares, movilidad, etc. (Próximamente)")
