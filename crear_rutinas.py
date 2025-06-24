import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime
import json
from guardar_rutina import guardar_rutina
from utils import aplicar_progresion, normalizar_texto

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def crear_rutinas():
    st.title("📝 Crear Nueva Rutina")

    # === NUEVO: Seleccionar rutina base desde la colección 'rutinas_semanales' ===
    st.markdown("---")
    st.subheader("📋 Usar como base una rutina existente")

    # ⚡️ Buscar nombres de rutinas en 'rutinas_semanales'
    rutinas_docs = db.collection("rutinas_semanales").stream()
    nombres_rutinas = sorted(set(doc.to_dict().get("nombre", "") for doc in rutinas_docs if doc.exists and doc.to_dict().get("nombre", "")))

    nombre_rutina_base = st.selectbox("Selecciona cliente con rutina:", [""] + nombres_rutinas)

    if st.button("📥 Cargar esta rutina como base"):
        if nombre_rutina_base:
            # Buscar en la colección correcta
            doc_ref = db.collection("rutinas_semanales").where("nombre", "==", nombre_rutina_base).limit(1).get()
            if doc_ref:
                rutina_base = doc_ref[0].to_dict()
                dias = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]
                columnas_tabla = [
                    "Circuito", "Sección", "Ejercicio", "Series", "Repeticiones",
                    "Peso", "Tiempo", "Velocidad", "RIR", "Tipo"
                ]
                for i, dia_nombre in enumerate(dias):
                    dia_key = f"rutina_dia_{i + 1}"
                    ejercicios = rutina_base.get(f"dia_{i + 1}", []) or rutina_base.get(f"dia{i + 1}", [])
                    st.session_state[dia_key] = ejercicios if ejercicios else [{k: "" for k in columnas_tabla} for _ in range(8)]

                # Autocompletar nombre y correo
                st.session_state["nombre_sel"] = rutina_base.get("nombre", "")
                st.session_state["correo_sel"] = rutina_base.get("correo", "")

                st.success(f"✅ Rutina de {nombre_rutina_base} cargada como base.")
            else:
                st.warning("No se encontró la rutina seleccionada en 'rutinas_semanales'.")

    st.markdown("---")

    # === Cargar usuarios ===
    docs = db.collection("usuarios").stream()
    usuarios = [doc.to_dict() for doc in docs if doc.exists]
    nombres = sorted(set(u.get("nombre", "") for u in usuarios))

    nombre_input = st.text_input("Escribe el nombre del cliente:", value=st.session_state.get("nombre_sel", ""))
    coincidencias = [n for n in nombres if nombre_input.lower() in n.lower()]
    nombre_sel = st.selectbox("Selecciona de la lista:", coincidencias) if coincidencias else ""

    correo_auto = next((u.get("correo", "") for u in usuarios if u.get("nombre") == nombre_sel), "")
    correo = st.text_input("Correo del cliente:", value=st.session_state.get("correo_sel", correo_auto))

    fecha_inicio = st.date_input("Fecha de inicio de rutina:", value=datetime.today())
    semanas = st.number_input("Semanas de duración:", min_value=1, max_value=12, value=4)
    entrenador = st.text_input("Nombre del entrenador responsable:")

    st.markdown("---")
    st.subheader("📆 Días de entrenamiento")

    dias = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]
    tabs = st.tabs(dias)

    columnas_tabla = [
        "Circuito", "Sección", "Ejercicio", "Series", "Repeticiones",
        "Peso", "Tiempo", "Velocidad", "RIR", "Tipo"
    ]

    progresion_activa = st.radio(
        "Progresión activa",
        ["Progresión 1", "Progresión 2", "Progresión 3"],
        horizontal=True, index=0
    )

    for i, tab in enumerate(tabs):
        with tab:
            dia_key = f"rutina_dia_{i + 1}"
            if dia_key not in st.session_state:
                st.session_state[dia_key] = [{k: "" for k in columnas_tabla} for _ in range(8)]

            st.write(f"Ejercicios para {dias[i]}")
            if st.button(f"Agregar fila en {dias[i]}", key=f"add_row_{i}"):
                st.session_state[dia_key].append({k: "" for k in columnas_tabla})

            for idx, fila in enumerate(st.session_state[dia_key]):
                st.markdown(f"##### Ejercicio {idx + 1}")

                cols = st.columns(14)
                fila["Circuito"] = cols[0].selectbox(
                    "", ["A", "B", "C", "D", "E", "F", "G"],
                    index=["A", "B", "C", "D", "E", "F", "G"].index(fila["Circuito"]) if fila["Circuito"] else 0,
                    key=f"circ_{i}_{idx}", label_visibility="collapsed"
                )

                fila["Sección"] = "Warm Up" if fila["Circuito"] in ["A", "B", "C"] else "Work Out"
                cols[1].text(fila["Sección"])
                fila["Ejercicio"] = cols[2].text_input(
                    "", value=fila["Ejercicio"], key=f"ej_{i}_{idx}",
                    label_visibility="collapsed", placeholder="Ejercicio"
                )
                fila["Series"] = cols[3].text_input(
                    "", value=fila["Series"], key=f"ser_{i}_{idx}",
                    label_visibility="collapsed", placeholder="Series"
                )
                fila["Repeticiones"] = cols[4].text_input(
                    "", value=fila["Repeticiones"], key=f"rep_{i}_{idx}",
                    label_visibility="collapsed", placeholder="Reps"
                )
                fila["Peso"] = cols[5].text_input(
                    "", value=fila["Peso"], key=f"peso_{i}_{idx}",
                    label_visibility="collapsed", placeholder="Kg"
                )
                fila["Tiempo"] = cols[6].text_input(
                    "", value=fila["Tiempo"], key=f"tiempo_{i}_{idx}",
                    label_visibility="collapsed", placeholder="Seg"
                )
                fila["Velocidad"] = cols[7].text_input(
                    "", value=fila["Velocidad"], key=f"vel_{i}_{idx}",
                    label_visibility="collapsed", placeholder="Vel"
                )
                fila["RIR"] = cols[8].text_input(
                    "", value=fila["RIR"], key=f"rir_{i}_{idx}",
                    label_visibility="collapsed", placeholder="RIR"
                )
                fila["Tipo"] = cols[13].text_input(
                    "", value=fila["Tipo"], key=f"tipo_{i}_{idx}",
                    label_visibility="collapsed", placeholder="Tipo"
                )

                for p in range(1, 4):
                    if progresion_activa == f"Progresión {p}":
                        fila[f"progresion_{p}_variable"] = cols[9].selectbox(
                            "",
                            ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"],
                            index=0 if not fila.get(f"progresion_{p}_variable") else
                            ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"].index(
                                fila[f"progresion_{p}_variable"]
                            ),
                            key=f"var{p}_{i}_{idx}",
                            label_visibility="collapsed"
                        )
                        fila[f"progresion_{p}_cantidad"] = cols[10].text_input(
                            "", value=fila.get(f"progresion_{p}_cantidad", ""),
                            key=f"cant{p}_{i}_{idx}",
                            label_visibility="collapsed",
                            placeholder=f"Cant{p}"
                        )
                        fila[f"progresion_{p}_operacion"] = cols[11].selectbox(
                            "", ["", "multiplicacion", "division", "suma", "resta"],
                            index=0 if not fila.get(f"progresion_{p}_operacion") else
                            ["", "multiplicacion", "division", "suma", "resta"].index(
                                fila[f"progresion_{p}_operacion"]
                            ),
                            key=f"ope{p}_{i}_{idx}",
                            label_visibility="collapsed"
                        )
                        fila[f"progresion_{p}_semanas"] = cols[12].text_input(
                            "", value=fila.get(f"progresion_{p}_semanas", ""),
                            key=f"sem{p}_{i}_{idx}",
                            label_visibility="collapsed",
                            placeholder=f"Sem{p}"
                        )

    st.markdown("---")

    if st.button("🔍 Previsualizar rutina"):
        st.session_state["mostrar_preview"] = True

    if st.session_state.get("mostrar_preview", False):
        st.subheader("📅 Previsualización de todas las semanas con progresiones aplicadas")

        for semana_idx in range(1, int(semanas) + 1):
            with st.expander(f"Semana {semana_idx}"):
                for i, dia_nombre in enumerate(dias):
                    dia_key = f"rutina_dia_{i + 1}"
                    ejercicios = st.session_state.get(dia_key, [])
                    if not ejercicios:
                        continue

                    st.write(f"**{dia_nombre}**")

                    tabla = []
                    for ejercicio in ejercicios:
                        ejercicio_mod = ejercicio.copy()

                        circuito = ejercicio.get("Circuito", "")
                        ejercicio_mod["Sección"] = "Warm Up" if circuito in ["A", "B", "C"] else "Work Out"

                        for p in range(1, 4):
                            variable = ejercicio.get(f"progresion_{p}_variable", "").strip().lower()
                            cantidad = ejercicio.get(f"progresion_{p}_cantidad", "")
                            operacion = ejercicio.get(f"progresion_{p}_operacion", "").strip().lower()
                            semanas_txt = ejercicio.get(f"progresion_{p}_semanas", "")

                            if variable and operacion and cantidad:
                                valor_base = ejercicio_mod.get(variable.capitalize(), "")
                                if valor_base:
                                    valor_actual = valor_base
                                    try:
                                        semanas_aplicar = [int(s.strip()) for s in semanas_txt.split(",") if s.strip().isdigit()]
                                    except:
                                        semanas_aplicar = []
                                    try:
                                        cantidad_float = float(cantidad)
                                    except (ValueError, TypeError):
                                        cantidad_float = 0

                                    for s in range(2, semana_idx + 1):
                                        if s in semanas_aplicar:
                                            valor_actual = aplicar_progresion(valor_actual, cantidad_float, operacion)
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

    if st.button("✅ Generar rutina completa"):
        guardar_rutina(nombre_sel, correo, entrenador, fecha_inicio, semanas, dias)
        st.success("✅ Rutina guardada correctamente.")
