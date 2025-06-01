import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime, timedelta

st.set_page_config(page_title="Motion Center", layout="wide")

if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_CREDENTIALS"])
    firebase_admin.initialize_app(cred)

db = firestore.client()

def crear_rutinas():
    st.title("📅 Crear nueva rutina")

    # === Obtener usuarios ===
    docs = db.collection("usuarios").stream()
    usuarios = [doc.to_dict() for doc in docs if doc.exists]
    nombres = sorted(set(u.get("nombre", "") for u in usuarios))

    # === Inputs principales ===
    nombre_input = st.text_input("👤 Escribe el nombre del cliente:")
    coincidencias = [n for n in nombres if nombre_input.lower() in n.lower()]
    nombre_sel = st.selectbox("🔎 Selecciona de la lista:", coincidencias) if coincidencias else ""
    correo_auto = next((u.get("correo", "") for u in usuarios if u.get("nombre") == nombre_sel), "")
    correo = st.text_input("✉️ Correo del cliente:", value=correo_auto)
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
                st.success("✅ Ejercicio guardado")

            if st.session_state[dia_key]:
                st.markdown("### ✅ Ejercicios guardados")
                for idx, ex in enumerate(st.session_state[dia_key]):
                    st.markdown(f"{idx+1}. **{ex['circuito']} - {ex['ejercicio']}**: {ex['series']}x{ex['repeticiones']} @ {ex['peso']}kg")

    st.markdown("---")

    if st.button("🚀 Generar rutina completa"):
        fecha_lunes = fecha_inicio - timedelta(days=fecha_inicio.weekday())
        fecha_lunes_str = fecha_lunes.strftime("%Y-%m-%d")

        total_subidos = 0
        for i in range(5):
            dia = i + 1
            ejercicios = st.session_state.get(f"rutina_dia_{dia}", [])
            for ex in ejercicios:
                doc_id = f"{correo.replace('@', '_').replace('.', '_')}_{fecha_lunes_str.replace('-', '_')}_{dia}_{ex['circuito']}_{ex['ejercicio']}".lower().replace(" ", "_")
                db.collection("rutinas").document(doc_id).set({
                    "cliente": nombre_sel,
                    "correo": correo,
                    "fecha_lunes": fecha_lunes_str,
                    "dia": str(dia),
                    "bloque": "Workout",
                    "circuito": ex["circuito"],
                    "ejercicio": ex["ejercicio"],
                    "series": ex["series"],
                    "repeticiones": ex["repeticiones"],
                    "peso": ex["peso"],
                    "tipo": ex["tipo"],
                    "progresion": ex["progresion"],
                    "registro_series": [],
                    "comentario": "",
                    "video": "",
                    "entrenador": entrenador
                })
                total_subidos += 1

        st.success(f"✅ Rutina generada y guardada correctamente ({total_subidos} ejercicios subidos a Firestore).")
