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
            return valor_inicial  # semana base

        if semana % periodo != 0:
            return valor_inicial

        if operacion == "suma":
            return str(float(valor_inicial) + incremento)
        elif operacion == "multiplicacion":
            return str(float(valor_inicial) * incremento)
        else:
            return valor_inicial
    except:
        return valor_inicial

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
        "Peso", "Velocidad", "RIR", "Progresión", "Tipo"
    ]

    for i, tab in enumerate(tabs):
        with tab:
            dia_key = f"rutina_dia_{i+1}"
            if dia_key not in st.session_state:
                st.session_state[dia_key] = []

            st.write(f"Ejercicios para {dias[i]}")

            agregar_fila = st.button(f"Agregar fila en {dias[i]}", key=f"add_row_{i}")
            if agregar_fila:
                st.session_state[dia_key].append({k: "" for k in columnas_tabla})

            for idx, fila in enumerate(st.session_state[dia_key]):
                cols = st.columns(len(columnas_tabla))

                fila["Circuito"] = cols[0].selectbox("Circuito", ["A", "B", "C", "D", "E", "F", "G"],
                                                    index=["A", "B", "C", "D", "E", "F", "G"].index(fila["Circuito"]) if fila["Circuito"] else 0,
                                                    key=f"circ_{i}_{idx}")
                fila["Sección"] = "Warm Up" if fila["Circuito"] in ["A", "B", "C"] else "Work Out"
                cols[1].markdown(f"**{fila['Sección']}**")

                fila["Ejercicio"] = cols[2].text_input("Ejercicio", value=fila["Ejercicio"], key=f"ej_{i}_{idx}")
                fila["Series"] = cols[3].number_input("Series", min_value=1, max_value=10, value=int(fila["Series"] or 3), key=f"ser_{i}_{idx}")
                fila["Repeticiones"] = cols[4].text_input("Reps", value=fila["Repeticiones"], key=f"rep_{i}_{idx}")
                fila["Peso"] = cols[5].text_input("Peso", value=fila["Peso"], key=f"peso_{i}_{idx}")
                fila["Velocidad"] = cols[6].text_input("Velocidad", value=fila["Velocidad"], key=f"vel_{i}_{idx}")
                fila["RIR"] = cols[7].text_input("RIR", value=fila["RIR"], key=f"rir_{i}_{idx}")
                fila["Progresión"] = cols[8].text_input("Progresión", value=fila["Progresión"], key=f"prog_{i}_{idx}")
                fila["Tipo"] = cols[9].text_input("Tipo", value=fila["Tipo"], key=f"tipo_{i}_{idx}")

    st.markdown("---")

    if st.button("Previsualizar rutina"):
        for semana in range(int(semanas)):
            fecha_semana = fecha_inicio + timedelta(weeks=semana)
            fecha_str = fecha_semana.strftime("%Y-%m-%d")
            st.subheader(f"Semana {semana+1} ({fecha_str})")
            for i in range(len(dias)):
                dia_nombre = dias[i]
                dia_key = f"rutina_dia_{i+1}"
                ejercicios = st.session_state.get(dia_key, [])

                st.markdown(f"**{dia_nombre}**")
                data = []
                for ejercicio in ejercicios:
                    ejercicio_mod = ejercicio.copy()
                    nombre_prog = ejercicio["Progresión"].strip()
                    if nombre_prog:
                        doc_prog = db.collection("progresiones").document(nombre_prog).get()
                        if doc_prog.exists:
                            prog = doc_prog.to_dict()
                            variable = prog.get("variable", "").lower()
                            incremento = float(prog.get("incremento", 0))
                            operacion = prog.get("operacion", "").lower()
                            periodo = int(prog.get("periodo", 1))
                            if variable in ejercicio_mod:
                                valor_base = ejercicio[variable].strip()
                                ejercicio_mod[variable] = aplicar_progresion(valor_base, semana, incremento, operacion, periodo)

                    data.append({
                        "Circuito": ejercicio_mod["Circuito"],
                        "Ejercicio": ejercicio_mod["Ejercicio"],
                        "Series": ejercicio_mod["Series"],
                        "Repeticiones": ejercicio_mod["Repeticiones"],
                        "Peso": ejercicio_mod["Peso"],
                        "Velocidad": ejercicio_mod["Velocidad"],
                        "RIR": ejercicio_mod["RIR"],
                        "Tipo": ejercicio_mod["Tipo"]
                    })
                if data:
                    st.dataframe(data, use_container_width=True)

    st.markdown("---")
