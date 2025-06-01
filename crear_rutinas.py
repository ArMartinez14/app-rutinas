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
            dia_key = f"rutina_dia_{i+1}"
            if dia_key not in st.session_state:
                st.session_state[dia_key] = []

            st.write(f"Ejercicios para {dias[i]}")

            agregar_fila = st.button(f"➕ Agregar fila en {dias[i]}", key=f"add_row_{i}")
            if agregar_fila:
                st.session_state[dia_key].append({k: "" for k in columnas_tabla})

            # Mostrar como tabla editable
            for idx, fila in enumerate(st.session_state[dia_key]):
                cols = st.columns(len(columnas_tabla))
                fila["Circuito"] = cols[0].selectbox("Circuito", ["A", "B", "C", "D", "E", "F", "G"], index=["A", "B", "C", "D", "E", "F", "G"].index(fila["Circuito"]) if fila["Circuito"] else 0, key=f"circ_{i}_{idx}")
                fila["Nombre Ejercicio"] = cols[1].text_input("Nombre Ejercicio", value=fila["Nombre Ejercicio"], key=f"ej_{i}_{idx}")
                fila["Series"] = cols[2].number_input("Series", min_value=1, max_value=10, value=int(fila["Series"] or 3), key=f"ser_{i}_{idx}")
                fila["Repeticiones"] = cols[3].text_input("Reps", value=fila["Repeticiones"], key=f"rep_{i}_{idx}")
                fila["Peso"] = cols[4].text_input("Peso", value=fila["Peso"], key=f"peso_{i}_{idx}")
                fila["Velocidad"] = cols[5].text_input("Velocidad", value=fila["Velocidad"], key=f"vel_{i}_{idx}")
                fila["RIR"] = cols[6].text_input("RIR", value=fila["RIR"], key=f"rir_{i}_{idx}")
                fila["Tipo Ejercicio"] = "Warm-up" if fila["Circuito"] in ["A", "B", "C"] else "Workout"
                cols[7].markdown(f"**{fila['Tipo Ejercicio']}**")
                fila["Progresión"] = cols[8].text_input("Progresión", value=fila["Progresión"], key=f"prog_{i}_{idx}")

    st.markdown("---")
    st.button("🚀 Generar rutina completa")  # Aún no implementado
