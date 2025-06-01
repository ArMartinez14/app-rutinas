import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime

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

    columnas_tabla = [
        "Circuito", "Nombre Ejercicio", "Series", "Repeticiones", "Peso", "Velocidad", "RIR", "Tipo Ejercicio", "Progresión"
    ]

    for i, tab in enumerate(tabs):
        with tab:
            dia_key = f"rutina_dia_{i + 1}"
            if dia_key not in st.session_state:
                st.session_state[dia_key] = []

            st.write(f"📝 Ingresar ejercicios para {dias[i]}")
            st.markdown("**Completa la fila siguiente y guarda cada ejercicio individualmente:**")

            # Mostrar inputs en una sola fila horizontal tipo tabla
            cols = st.columns(9)
            circuito = cols[0].selectbox("Circuito", ["A", "B", "C", "D", "E", "F"], key=f"circ_{i}")
            ejercicio = cols[1].text_input("Ejercicio", key=f"ej_{i}")
            series = cols[2].number_input("Series", min_value=1, max_value=10, value=3, key=f"ser_{i}")
            repes = cols[3].text_input("Reps", key=f"rep_{i}")
            peso = cols[4].text_input("Peso", key=f"pes_{i}")
            velocidad = cols[5].text_input("Vel", key=f"vel_{i}")
            rir = cols[6].text_input("RIR", key=f"rir_{i}")
            tipo = cols[7].text_input("Tipo", key=f"tipo_{i}")
            prog = cols[8].text_input("Progresión", key=f"prog_{i}")

            if st.button(f"💾 Guardar fila {dias[i]}", key=f"guardar_fila_{i}"):
                st.session_state[dia_key].append({
                    "circuito": circuito,
                    "ejercicio": ejercicio,
                    "series": series,
                    "repeticiones": repes,
                    "peso": peso,
                    "velocidad": velocidad,
                    "rir": rir,
                    "tipo": tipo,
                    "progresion": prog
                })
                st.success("✅ Ejercicio agregado al día.")

            if st.session_state[dia_key]:
                st.markdown("### ✅ Ejercicios guardados")
                st.dataframe(st.session_state[dia_key], use_container_width=True)

    st.markdown("---")
    st.button("🚀 Generar rutina completa")  # Aún no implementado
