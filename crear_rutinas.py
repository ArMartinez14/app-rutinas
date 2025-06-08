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

def crear_rutinas():
    st.title("Crear nueva rutina")

    docs = db.collection("usuarios").stream()
    usuarios = [doc.to_dict() for doc in docs if doc.exists]
    nombres = sorted(set(u.get("nombre", "") for u in usuarios))

    nombre_input = st.text_input("Escribe el nombre del cliente:")
    coincidencias = [n for n in nombres if nombre_input.lower() in n.lower()]
    nombre_sel = st.selectbox("Selecciona de la lista:", coincidencias) if coincidencias else ""

    correo_auto = next((u.get("correo", "") for u in usuarios if u.get("nombre") == nombre_sel), "")
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

    for i, tab in enumerate(tabs):
        with tab:
            dia_key = f"rutina_dia_{i+1}"
            if dia_key not in st.session_state:
                st.session_state[dia_key] = [{k: "" for k in columnas_tabla} for _ in range(8)]

            st.write(f"Ejercicios para {dias[i]}")
            agregar_fila = st.button(f"Agregar fila en {dias[i]}", key=f"add_row_{i}")
            if agregar_fila:
                st.session_state[dia_key].append({k: "" for k in columnas_tabla})

            for idx, fila in enumerate(st.session_state[dia_key]):
                st.markdown(f"##### Ejercicio {idx+1} - {fila.get('Ejercicio', '')}")

                # === FILA BASE ===
                cols = st.columns(10)
                fila["Circuito"] = cols[0].selectbox("", ["A", "B", "C", "D", "E", "F", "G"],
                    index=["A", "B", "C", "D", "E", "F", "G"].index(fila["Circuito"]) if fila["Circuito"] else 0,
                    key=f"circ_{i}_{idx}", label_visibility="collapsed")
                fila["Sección"] = "Warm Up" if fila["Circuito"] in ["A", "B", "C"] else "Work Out"
                cols[1].markdown(f"<div style='padding-top: 0.75em'><b>{fila['Sección']}</b></div>", unsafe_allow_html=True)
                fila["Ejercicio"] = cols[2].text_input("", value=fila["Ejercicio"], key=f"ej_{i}_{idx}", label_visibility="collapsed", placeholder="Ejercicio")
                fila["Series"] = cols[3].text_input("", value=fila["Series"], key=f"ser_{i}_{idx}", label_visibility="collapsed", placeholder="S")
                fila["Repeticiones"] = cols[4].text_input("", value=fila["Repeticiones"], key=f"rep_{i}_{idx}", label_visibility="collapsed", placeholder="Reps")
                fila["Peso"] = cols[5].text_input("", value=fila["Peso"], key=f"peso_{i}_{idx}", label_visibility="collapsed", placeholder="Kg")
                fila["Tiempo"] = cols[6].text_input("", value=fila["Tiempo"], key=f"tiempo_{i}_{idx}", label_visibility="collapsed", placeholder="Seg")
                fila["Velocidad"] = cols[7].text_input("", value=fila["Velocidad"], key=f"vel_{i}_{idx}", label_visibility="collapsed", placeholder="Vel")
                fila["RIR"] = cols[8].text_input("", value=fila["RIR"], key=f"rir_{i}_{idx}", label_visibility="collapsed", placeholder="RIR")
                fila["Tipo"] = cols[9].text_input("", value=fila["Tipo"], key=f"tipo_{i}_{idx}", label_visibility="collapsed", placeholder="Tipo")

                # === PESTAÑAS DE PROGRESIÓN ===
                st.markdown("**Progresiones**")
                prog_tabs = st.tabs(["Progresión 1", "Progresión 2", "Progresión 3"])
                for p_index, prog_tab in enumerate(prog_tabs, start=1):
                    with prog_tab:
                        prog_cols = st.columns([1, 1, 1, 1.5])
                        key_sufijo = f"_{p_index}"

                        variable_key = f"Variable{key_sufijo}"
                        cantidad_key = f"Cantidad{key_sufijo}"
                        operacion_key = f"Operacion{key_sufijo}"
                        semanas_key = f"Semanas{key_sufijo}"

                        fila[variable_key] = prog_cols[0].selectbox(
                            "Variable", ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"],
                            index=0 if not fila.get(variable_key) else ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"].index(fila[variable_key]),
                            key=f"var_{i}_{idx}_{p_index}", label_visibility="collapsed"
                        )
                        fila[cantidad_key] = prog_cols[1].text_input("", value=fila.get(cantidad_key, ""), key=f"cant_{i}_{idx}_{p_index}", label_visibility="collapsed", placeholder="Cant.")
                        fila[operacion_key] = prog_cols[2].selectbox(
                            "", ["", "multiplicacion", "division", "suma", "resta"],
                            index=0 if not fila.get(operacion_key) else ["", "multiplicacion", "division", "suma", "resta"].index(fila[operacion_key]),
                            key=f"ope_{i}_{idx}_{p_index}", label_visibility="collapsed"
                        )
                        fila[semanas_key] = prog_cols[3].text_input("", value=fila.get(semanas_key, ""), key=f"sem_{i}_{idx}_{p_index}", label_visibility="collapsed", placeholder="Semanas")

    st.markdown("---")
    if st.button("Generar rutina completa"):
        guardar_rutina(nombre_sel, correo, entrenador, fecha_inicio, semanas, dias)