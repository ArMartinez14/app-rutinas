import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime, timedelta
import unicodedata
from guardar_rutina import guardar_rutina
from utils import aplicar_progresion, normalizar_texto
import json

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

@st.cache_data
def buscar_usuario_por_nombre(nombre):
    docs = db.collection("usuarios")\
        .where("nombre", ">=", nombre)\
        .where("nombre", "<=", nombre + "\uf8ff")\
        .stream()
    return [doc.to_dict() for doc in docs if doc.exists]

def crear_rutinas():
    st.title("Crear nueva rutina")

    nombre_input = st.text_input("Escribe el nombre del cliente:")

    if nombre_input:
        coincidencias = buscar_usuario_por_nombre(nombre_input.title())
        nombres = sorted(set(u.get("nombre", "") for u in coincidencias))
        nombre_sel = st.selectbox("Selecciona de la lista:", nombres) if nombres else ""
        correo_auto = next((u.get("correo", "") for u in coincidencias if u.get("nombre") == nombre_sel), "")
    else:
        nombre_sel = ""
        correo_auto = ""

    correo = st.text_input("Correo del cliente:", value=correo_auto)

    fecha_inicio = st.date_input("Fecha de inicio de rutina:", value=datetime.today())
    semanas = st.number_input("Semanas de duración:", min_value=1, max_value=12, value=4)
    entrenador = st.text_input("Nombre del entrenador responsable:")

    st.markdown("---")
    st.subheader("Días de entrenamiento")

    dias = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]
    tabs = st.tabs(dias)

    columnas_tabla = [
        "Circuito", "Sección", "Ejercicio", "Series", "Repeticiones",
        "Peso", "Tiempo", "Velocidad", "RIR", "Tipo"
    ]

    progresion_activa = st.radio("Progresión activa", ["Progresión 1", "Progresión 2", "Progresión 3"], horizontal=True, index=0)

    for i, tab in enumerate(tabs):
        with tab:
            dia_key = f"rutina_dia_{i + 1}"
            if dia_key not in st.session_state:
                st.session_state[dia_key] = [{k: "" for k in columnas_tabla} for _ in range(8)]

            st.write(f"Ejercicios para {dias[i]}")
            agregar_fila = st.button(f"Agregar fila en {dias[i]}", key=f"add_row_{i}")
            if agregar_fila:
                st.session_state[dia_key].append({k: "" for k in columnas_tabla})

            for idx, fila in enumerate(st.session_state[dia_key]):
                st.markdown(f"##### Ejercicio {idx + 1} - {fila.get('Ejercicio', '')}")

                cols = st.columns(14)
                fila["Circuito"] = cols[0].selectbox("", ["A", "B", "C", "D", "E", "F", "G"],
                                                     index=["A", "B", "C", "D", "E", "F", "G"].index(fila["Circuito"]) if fila["Circuito"] else 0,
                                                     key=f"circ_{i}_{idx}", label_visibility="collapsed")
                fila["Sección"] = "Warm Up" if fila["Circuito"] in ["A", "B", "C"] else "Work Out"
                cols[1].text(fila["Sección"])
                fila["Ejercicio"] = cols[2].text_input("", value=fila["Ejercicio"], key=f"ej_{i}_{idx}", label_visibility="collapsed", placeholder="Ejercicio")
                fila["Series"] = cols[3].text_input("", value=fila["Series"], key=f"ser_{i}_{idx}", label_visibility="collapsed", placeholder="Series")
                fila["Repeticiones"] = cols[4].text_input("", value=fila["Repeticiones"], key=f"rep_{i}_{idx}", label_visibility="collapsed", placeholder="Reps")
                fila["Peso"] = cols[5].text_input("", value=fila["Peso"], key=f"peso_{i}_{idx}", label_visibility="collapsed", placeholder="Kg")
                fila["Tiempo"] = cols[6].text_input("", value=fila["Tiempo"], key=f"tiempo_{i}_{idx}", label_visibility="collapsed", placeholder="Seg")
                fila["Velocidad"] = cols[7].text_input("", value=fila["Velocidad"], key=f"vel_{i}_{idx}", label_visibility="collapsed", placeholder="Vel")
                fila["RIR"] = cols[8].text_input("", value=fila["RIR"], key=f"rir_{i}_{idx}", label_visibility="collapsed", placeholder="RIR")
                fila["Tipo"] = cols[13].text_input("", value=fila["Tipo"], key=f"tipo_{i}_{idx}", label_visibility="collapsed", placeholder="Tipo")

                for p in range(1, 4):
                    if progresion_activa == f"Progresión {p}":
                        fila[f"Variable_{p}"] = cols[9].selectbox("", ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"],
                                                                  index=0 if not fila.get(f"Variable_{p}") else ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"].index(fila[f"Variable_{p}"]),
                                                                  key=f"var{p}_{i}_{idx}", label_visibility="collapsed")
                        fila[f"Cantidad_{p}"] = cols[10].text_input("", value=fila.get(f"Cantidad_{p}", ""), key=f"cant{p}_{i}_{idx}", label_visibility="collapsed", placeholder=f"Cant{p}")
                        fila[f"Operacion_{p}"] = cols[11].selectbox("", ["", "multiplicacion", "division", "suma", "resta"],
                                                                      index=0 if not fila.get(f"Operacion_{p}") else ["", "multiplicacion", "division", "suma", "resta"].index(fila[f"Operacion_{p}"]),
                                                                      key=f"ope{p}_{i}_{idx}", label_visibility="collapsed")
                        fila[f"Semanas_{p}"] = cols[12].text_input("", value=fila.get(f"Semanas_{p}", ""), key=f"sem{p}_{i}_{idx}", label_visibility="collapsed", placeholder=f"Sem{p}")

    st.markdown("---")
    if st.button("Generar rutina completa"):
        guardar_rutina(nombre_sel, correo, entrenador, fecha_inicio, semanas, dias)
