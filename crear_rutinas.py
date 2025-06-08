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
        "Circuito", "Ejercicio", "Series", "Repeticiones",
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

                prog_opciones = ["Progresión 1", "Progresión 2", "Progresión 3"]
                fila_key_prog = f"progresion_seleccionada_{i}_{idx}"
                if fila_key_prog not in st.session_state:
                    st.session_state[fila_key_prog] = prog_opciones[0]
                fila_prog = st.radio("Progresión activa", prog_opciones, key=fila_key_prog, horizontal=True)

                cols = st.columns(13)
                fila["Circuito"] = cols[0].selectbox("", ["A", "B", "C", "D", "E", "F", "G"],
                    index=["A", "B", "C", "D", "E", "F", "G"].index(fila["Circuito"]) if fila["Circuito"] else 0,
                    key=f"circ_{i}_{idx}", label_visibility="collapsed")
                fila["Ejercicio"] = cols[1].text_input("", value=fila["Ejercicio"], key=f"ej_{i}_{idx}", label_visibility="collapsed", placeholder="Ejercicio")
                fila["Series"] = cols[2].text_input("", value=fila["Series"], key=f"ser_{i}_{idx}", label_visibility="collapsed", placeholder="S")
                fila["Repeticiones"] = cols[3].text_input("", value=fila["Repeticiones"], key=f"rep_{i}_{idx}", label_visibility="collapsed", placeholder="Reps")
                fila["Peso"] = cols[4].text_input("", value=fila["Peso"], key=f"peso_{i}_{idx}", label_visibility="collapsed", placeholder="Kg")
                fila["Tiempo"] = cols[5].text_input("", value=fila["Tiempo"], key=f"tiempo_{i}_{idx}", label_visibility="collapsed", placeholder="Seg")
                fila["Velocidad"] = cols[6].text_input("", value=fila["Velocidad"], key=f"vel_{i}_{idx}", label_visibility="collapsed", placeholder="Vel")
                fila["RIR"] = cols[7].text_input("", value=fila["RIR"], key=f"rir_{i}_{idx}", label_visibility="collapsed", placeholder="RIR")
                fila["Tipo"] = cols[8].text_input("", value=fila["Tipo"], key=f"tipo_{i}_{idx}", label_visibility="collapsed", placeholder="Tipo")

                for p in range(1, 4):
                    if fila_prog == f"Progresión {p}":
                        fila[f"Variable_{p}"] = cols[9].selectbox("", ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"],
                            index=0 if not fila.get(f"Variable_{p}") else ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"].index(fila[f"Variable_{p}"]),
                            key=f"var{p}_{i}_{idx}", label_visibility="collapsed")
                        fila[f"Cantidad_{p}"] = cols[10].text_input("", value=fila.get(f"Cantidad_{p}", ""), key=f"cant{p}_{i}_{idx}", label_visibility="collapsed", placeholder=f"Cant{p}")
                        fila[f"Operacion_{p}"] = cols[11].selectbox("", ["", "multiplicacion", "division", "suma", "resta"],
                            index=0 if not fila.get(f"Operacion_{p}") else ["", "multiplicacion", "division", "suma", "resta"].index(fila[f"Operacion_{p}"]),
                            key=f"ope{p}_{i}_{idx}", label_visibility="collapsed")
                        fila[f"Semanas_{p}"] = cols[12].text_input("", value=fila.get(f"Semanas_{p}", ""), key=f"sem{p}_{i}_{idx}", label_visibility="collapsed", placeholder=f"Sem{p}")

    st.markdown("---")
    if st.button("Previsualizar rutina"):
        st.subheader("Previsualización de rutina con progresiones")
        for semana_idx in range(1, int(semanas)+1):
            with st.expander(f"Semana {semana_idx}"):
                for i, dia in enumerate(dias):
                    dia_key = f"rutina_dia_{i+1}"
                    ejercicios = st.session_state.get(dia_key, [])
                    st.markdown(f"**{dia}**")
                    tabla = []
                    for ejercicio in ejercicios:
                        ejercicio_mod = ejercicio.copy()
                        circuito = ejercicio.get("Circuito", "")
                        ejercicio_mod["Sección"] = "Warm Up" if circuito in ["A", "B", "C"] else "Work Out"

                        for prog_idx in range(1, 4):
                            variable = ejercicio.get(f"Variable_{prog_idx}", "").strip().lower()
                            cantidad = ejercicio.get(f"Cantidad_{prog_idx}", "")
                            operacion = ejercicio.get(f"Operacion_{prog_idx}", "").strip().lower()
                            semanas_txt = ejercicio.get(f"Semanas_{prog_idx}", "")
                            try:
                                semanas_aplicar = [int(s.strip()) for s in semanas_txt.split(",") if s.strip().isdigit()]
                            except:
                                semanas_aplicar = []

                            if variable and operacion and cantidad:
                                valor_base = ejercicio_mod.get(variable.capitalize(), "")
                                if valor_base:
                                    valor_actual = valor_base
                                    for s in range(2, semana_idx + 1):
                                        if s in semanas_aplicar:
                                            try:
                                                valor_actual = aplicar_progresion(valor_actual, float(cantidad), operacion)
                                            except:
                                                pass
                                    ejercicio_mod[variable.capitalize()] = valor_actual

                        tabla.append({
                            "bloque": ejercicio_mod["Sección"],
                            "circuito": ejercicio_mod["Circuito"],
                            "ejercicio": ejercicio_mod["Ejercicio"],
                            "series": ejercicio_mod["Series"],
                            "repeticiones": ejercicio_mod["Repeticiones"],
                            "peso": ejercicio_mod["Peso"],
                            "tiempo": ejercicio_mod["Tiempo"],
                            "velocidad": ejercicio_mod["Velocidad"],
                            "rir": ejercicio_mod["RIR"],
                            "tipo": ejercicio_mod["Tipo"]
                        })
                    st.dataframe(tabla, use_container_width=True)

    st.markdown("---")
    if st.button("Generar rutina completa"):
        guardar_rutina(nombre_sel, correo, entrenador, fecha_inicio, semanas, dias)
