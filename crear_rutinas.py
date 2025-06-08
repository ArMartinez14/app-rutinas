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

                # === FILA BASE CON PROGRESIONES INCLUIDAS ===
                cols = st.columns(17)
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

                # Progresión 1
                fila["Variable_1"] = cols[10].selectbox("", ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"],
                    index=0 if not fila.get("Variable_1") else ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"].index(fila["Variable_1"]),
                    key=f"var1_{i}_{idx}", label_visibility="collapsed")
                fila["Cantidad_1"] = cols[11].text_input("", value=fila.get("Cantidad_1", ""), key=f"cant1_{i}_{idx}", label_visibility="collapsed", placeholder="Cant1")
                fila["Operacion_1"] = cols[12].selectbox("", ["", "multiplicacion", "division", "suma", "resta"],
                    index=0 if not fila.get("Operacion_1") else ["", "multiplicacion", "division", "suma", "resta"].index(fila["Operacion_1"]),
                    key=f"ope1_{i}_{idx}", label_visibility="collapsed")
                fila["Semanas_1"] = cols[13].text_input("", value=fila.get("Semanas_1", ""), key=f"sem1_{i}_{idx}", label_visibility="collapsed", placeholder="Sem1")

                # Progresión 2
                fila["Variable_2"] = cols[14].selectbox("", ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"],
                    index=0 if not fila.get("Variable_2") else ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"].index(fila["Variable_2"]),
                    key=f"var2_{i}_{idx}", label_visibility="collapsed")
                fila["Cantidad_2"] = cols[15].text_input("", value=fila.get("Cantidad_2", ""), key=f"cant2_{i}_{idx}", label_visibility="collapsed", placeholder="Cant2")
                fila["Operacion_2"] = cols[16].selectbox("", ["", "multiplicacion", "division", "suma", "resta"],
                    index=0 if not fila.get("Operacion_2") else ["", "multiplicacion", "division", "suma", "resta"].index(fila["Operacion_2"]),
                    key=f"ope2_{i}_{idx}", label_visibility="collapsed")
                fila["Semanas_2"] = cols[16].text_input("", value=fila.get("Semanas_2", ""), key=f"sem2_{i}_{idx}", label_visibility="collapsed", placeholder="Sem2")

    st.markdown("---")
    if st.button("Generar rutina completa"):
        guardar_rutina(nombre_sel, correo, entrenador, fecha_inicio, semanas, dias)
