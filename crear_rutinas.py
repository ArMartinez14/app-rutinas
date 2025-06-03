import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime, timedelta
import unicodedata

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_CREDENTIALS"])
    firebase_admin.initialize_app(cred)

db = firestore.client()


# === FUNCION DE PROGRESIÓN ===
def aplicar_progresion(valor_inicial, semana, incremento, operacion, periodo):
    try:
        if semana == 0:
            return valor_inicial  # semana base sin progresión

        veces = semana // periodo
        resultado = float(valor_inicial)

        for _ in range(veces):
            if operacion == "suma":
                resultado += incremento
            elif operacion == "multiplicacion":
                resultado *= incremento

        return str(round(resultado, 2))
    except:
        return valor_inicial


# === FUNCION DE PROGRESIÓN PERSONALIZADA ===
def aplicar_progresion_personalizada(valor_base, cantidad, operacion):
    try:
        valor_base = float(valor_base)
        cantidad = float(cantidad)
        if operacion == "sumar":
            return str(round(valor_base + cantidad, 2))
        elif operacion == "restar":
            return str(round(valor_base - cantidad, 2))
        elif operacion == "multiplicar":
            return str(round(valor_base * cantidad, 2))
        elif operacion == "dividir":
            return str(round(valor_base / cantidad, 2))
        else:
            return str(valor_base)
    except:
        return str(valor_base)


# === FUNCION PARA NORMALIZAR TEXTO ===
def normalizar_texto(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


def crear_rutinas():
    st.title("Crear nueva rutina")

    # === OBTENER USUARIOS DESDE FIRESTORE ===
    docs = db.collection("usuarios").stream()
    usuarios = [doc.to_dict() for doc in docs if doc.exists]
    nombres = sorted(set(u.get("nombre", "") for u in usuarios))

    # === INPUT DE NOMBRE CON SUGERENCIAS ===
    nombre_input = st.text_input("Escribe el nombre del cliente:")
    coincidencias = [n for n in nombres if nombre_input.lower() in n.lower()]
    nombre_sel = st.selectbox("Selecciona de la lista:", coincidencias) if coincidencias else ""

    # === AUTOCOMPLETAR CORREO ===
    correo_auto = next((u.get("correo", "") for u in usuarios if u.get("nombre") == nombre_sel), "")
    correo = st.text_input("Correo del cliente:", value=correo_auto)

    # === OTROS CAMPOS ===
    fecha_inicio = st.date_input("Fecha de inicio de rutina:", value=datetime.today())
    semanas = st.number_input("Semanas de duración:", min_value=1, max_value=12, value=4)
    entrenador = st.text_input("Nombre del entrenador responsable:")

    st.markdown("---")
    st.subheader("Días de entrenamiento")

    dias = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]
    tabs = st.tabs(dias)

    columnas_tabla = [
        "Circuito", "Sección", "Ejercicio", "Series", "Repeticiones",
        "Peso", "Velocidad", "RIR", "Tipo"
    ]

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
                cols = st.columns(len(columnas_tabla))

                fila["Circuito"] = cols[0].selectbox("Circuito", ["A", "B", "C", "D", "E", "F", "G"],
                                                     index=["A", "B", "C", "D", "E", "F", "G"].index(
                                                         fila["Circuito"]) if fila["Circuito"] else 0,
                                                     key=f"circ_{i}_{idx}")
                fila["Sección"] = "Warm Up" if fila["Circuito"] in ["A", "B", "C"] else "Work Out"
                cols[1].markdown(f"**{fila['Sección']}**")

                fila["Ejercicio"] = cols[2].text_input("Ejercicio", value=fila["Ejercicio"], key=f"ej_{i}_{idx}")
                fila["Series"] = cols[3].number_input("Series", min_value=1, max_value=10,
                                                      value=int(fila["Series"] or 3), key=f"ser_{i}_{idx}")
                fila["Repeticiones"] = cols[4].text_input("Reps", value=fila["Repeticiones"], key=f"rep_{i}_{idx}")
                fila["Peso"] = cols[5].text_input("Peso", value=fila["Peso"], key=f"peso_{i}_{idx}")
                fila["Velocidad"] = cols[6].text_input("Velocidad", value=fila["Velocidad"], key=f"vel_{i}_{idx}")
                fila["RIR"] = cols[7].text_input("RIR", value=fila["RIR"], key=f"rir_{i}_{idx}")
                fila["Tipo"] = cols[8].text_input("Tipo", value=fila["Tipo"], key=f"tipo_{i}_{idx}")

            # BLOQUE DE PROGRESIÓN PERSONALIZADA - SOLO PARA LA PRIMERA FILA COMO DEMO
            if idx == 0:
                st.markdown("**Progresión personalizada:**")
                colp1, colp2, colp3 = st.columns(3)
                variable_sel = colp1.selectbox("Variable a modificar", ["peso", "velocidad", "repeticiones"],
                                               key=f"var_mod_{i}_{idx}")
                cantidad_sel = colp2.text_input("Cantidad", key=f"cant_mod_{i}_{idx}")
                operacion_sel = colp3.selectbox("Operación", ["sumar", "restar", "multiplicar", "dividir"],
                                                key=f"op_mod_{i}_{idx}")

                semanas_disp = [f"Semana {s}" for s in range(2, int(semanas) + 1)]
                st.markdown("**Semanas a aplicar**")
                col_check = st.columns(len(semanas_disp) + 1)
                aplicar_todas = col_check[0].checkbox("Todas", key=f"todas_sem_{i}_{idx}")
                semanas_sel = []
                for j, semana in enumerate(semanas_disp):
                    check = col_check[j + 1].checkbox(semana, key=f"sem_{semana}_{i}_{idx}", value=aplicar_todas)
                    if check:
                        semanas_sel.append(j + 2)

                fila["progresion_custom"] = {
                    "variable": variable_sel,
                    "cantidad": cantidad_sel,
                    "operacion": operacion_sel,
                    "semanas": semanas_sel
                }


st.markdown("---")

if st.button("Previsualizar rutina"):
    semana_tabs = st.tabs([f"Semana {i + 1}" for i in range(int(semanas))])

    for semana_idx, tab_semana in enumerate(semana_tabs):
        with tab_semana:
            fecha_semana = fecha_inicio + timedelta(weeks=semana_idx)
            fecha_str = fecha_semana.strftime("%Y-%m-%d")
            st.caption(f"Inicio de semana: {fecha_str}")

            dia_tabs = st.tabs(dias)
            for i, tab_dia in enumerate(dia_tabs):
                with tab_dia:
                    dia_nombre = dias[i]
                    dia_key = f"rutina_dia_{i + 1}"
                    ejercicios = st.session_state.get(dia_key, [])

                    data = []
                    for ejercicio in ejercicios:
                        ejercicio_mod = ejercicio.copy()

                        data.append({
                            "bloque": ejercicio_mod["Sección"],
                            "circuito": ejercicio_mod["Circuito"],
                            "ejercicio": ejercicio_mod["Ejercicio"],
                            "series": ejercicio_mod["Series"],
                            "repeticiones": ejercicio_mod["Repeticiones"],
                            "peso": ejercicio_mod["Peso"],
                            "velocidad": ejercicio_mod["Velocidad"],
                            "rir": ejercicio_mod["RIR"],
                            "tipo": ejercicio_mod["Tipo"]
                        })

                    if data:
                        st.dataframe(data, use_container_width=True)

st.markdown("---")

if st.button("Generar rutina completa"):
    if not nombre_sel or not correo or not entrenador:
        st.warning("Faltan datos obligatorios: nombre, correo o entrenador.")
        return

    try:
        for semana in range(int(semanas)):
            fecha_semana = fecha_inicio + timedelta(weeks=semana)
            fecha_str = fecha_semana.strftime("%Y-%m-%d")
            fecha_normalizada = fecha_semana.strftime("%Y_%m_%d")
            correo_normalizado = correo.replace("@", "_").replace(".", "_")
            nombre_normalizado = normalizar_texto(nombre_sel)

            for i in range(len(dias)):
                dia_nombre = dias[i]
                dia_key = f"rutina_dia_{i + 1}"
                ejercicios = st.session_state.get(dia_key, [])

                for ejercicio in ejercicios:
                    ejercicio_mod = ejercicio.copy()

                    doc_id = f"{correo_normalizado}_{fecha_normalizada}_{dia_nombre}_{ejercicio['Circuito']}_{ejercicio['Ejercicio']}".lower().replace(
                        " ", "_")

                    data = {
                        "cliente": nombre_normalizado,
                        "correo": correo,
                        "semana": str(semana + 1),
                        "fecha_lunes": fecha_str,
                        "dia": dia_nombre.split(" ")[-1],
                        "bloque": ejercicio_mod["Sección"],
                        "circuito": ejercicio_mod["Circuito"],
                        "ejercicio": ejercicio_mod["Ejercicio"],
                        "series": ejercicio_mod["Series"],
                        "repeticiones": ejercicio_mod["Repeticiones"],
                        "peso": ejercicio_mod["Peso"],
                        "velocidad": ejercicio_mod["Velocidad"],
                        "rir": ejercicio_mod["RIR"],
                        "tipo": ejercicio_mod["Tipo"],
                        "entrenador": entrenador
                    }

                    db.collection("rutinas").document(doc_id).set(data)

        st.success(f"✅ Rutina generada correctamente para {semanas} semanas.")
    except Exception as e:
        st.error(f"❌ Error al guardar la rutina: {e}")
