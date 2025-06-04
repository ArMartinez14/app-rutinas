import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime, timedelta
import unicodedata
import json

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# === FUNCION DE PROGRESIÓN ===
def aplicar_progresion(valor_inicial, incremento, operacion):
    try:
        if operacion == "suma":
            return str(float(valor_inicial) + incremento)
        elif operacion == "resta":
            return str(float(valor_inicial) - incremento)
        elif operacion == "multiplicacion":
            return str(float(valor_inicial) * incremento)
        elif operacion == "division":
            return str(float(valor_inicial) / incremento)
        else:
            return valor_inicial
    except:
        return valor_inicial

# === FUNCION PARA NORMALIZAR TEXTO ===
def normalizar_texto(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


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
        "Peso", "Tiempo", "Velocidad", "RIR", "Tipo",
        "Variable", "Cantidad", "Operación", "Semanas"
    ]

    encabezados = [
        "Circuito", "Sección", "Ejercicio", "Series", "Repeticiones",
        "Peso", "Tiempo", "Velocidad", "RIR", "Tipo",
        "Variable", "Cantidad", "Operación", "Semanas"
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

            st.markdown("<b>Progresión</b>", unsafe_allow_html=True)
            header_cols = st.columns(len(encabezados))
            for col, header in zip(header_cols, encabezados):
                col.markdown(f"**{header}**")

            for idx, fila in enumerate(st.session_state[dia_key]):
                cols = st.columns(len(columnas_tabla))

                fila["Circuito"] = cols[0].selectbox("", ["A", "B", "C", "D", "E", "F", "G"],
                                                    index=["A", "B", "C", "D", "E", "F", "G"].index(fila["Circuito"]) if fila["Circuito"] else 0,
                                                    key=f"circ_{i}_{idx}")
                fila["Sección"] = "Warm Up" if fila["Circuito"] in ["A", "B", "C"] else "Work Out"
                cols[1].markdown(f"{fila['Sección']}")

                fila["Ejercicio"] = cols[2].text_input("", value=fila["Ejercicio"], key=f"ej_{i}_{idx}")
                fila["Series"] = cols[3].text_input("", value=fila["Series"], key=f"ser_{i}_{idx}")
                fila["Repeticiones"] = cols[4].text_input("", value=fila["Repeticiones"], key=f"rep_{i}_{idx}")
                fila["Peso"] = cols[5].text_input("", value=fila["Peso"], key=f"peso_{i}_{idx}")
                fila["Tiempo"] = cols[6].text_input("", value=fila["Tiempo"], key=f"tiempo_{i}_{idx}")
                fila["Velocidad"] = cols[7].text_input("", value=fila["Velocidad"], key=f"vel_{i}_{idx}")
                fila["RIR"] = cols[8].text_input("", value=fila["RIR"], key=f"rir_{i}_{idx}")
                fila["Tipo"] = cols[9].text_input("", value=fila["Tipo"], key=f"tipo_{i}_{idx}")

                fila["Variable"] = cols[10].selectbox(
                    "",
                    ["", "peso", "velocidad", "tiempo", "rir", "series", "repeticiones"],
                    index=0 if not fila["Variable"] else ["", "peso", "velocidad", "tiempo", "rir", "series",
                                                          "repeticiones"].index(fila["Variable"]),
                    key=f"var_{i}_{idx}"
                )

                fila["Cantidad"] = cols[11].text_input("", value=fila["Cantidad"], key=f"cant_{i}_{idx}")
                fila["Operación"] = cols[12].selectbox("", ["", "multiplicacion", "division", "suma", "resta"], index=0 if not fila["Operación"] else ["", "multiplicacion", "division", "suma", "resta"].index(fila["Operación"]), key=f"ope_{i}_{idx}")
                fila["Semanas"] = cols[13].text_input("", value=fila["Semanas"], key=f"sem_{i}_{idx}")

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
                        variable = ejercicio.get("Variable", "").strip().lower()
                        cantidad = ejercicio.get("Cantidad", "")
                        operacion = ejercicio.get("Operación", "").strip().lower()
                        semanas_txt = ejercicio.get("Semanas", "")
                        try:
                            semanas_aplicar = [int(s.strip()) for s in semanas_txt.split(",") if s.strip().isdigit()]
                        except:
                            semanas_aplicar = []

                        if variable and operacion and cantidad and semana_idx in semanas_aplicar:
                            valor_base = ejercicio.get(variable.capitalize(), "")
                            if valor_base:
                                ejercicio_mod[variable.capitalize()] = aplicar_progresion(valor_base, float(cantidad), operacion)

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
        st.info("La lógica para guardar con la nueva estructura está lista para conectarse. ¿Deseas que la configuremos?")
