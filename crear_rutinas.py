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
def aplicar_progresion(valor_inicial, semana, incremento, operacion, periodo):
    try:
        if semana == 1:
            return valor_inicial  # semana base

        if (semana - 1) % periodo != 0:
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
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').title()

# === FUNCION PRINCIPAL ===
def crear_rutinas():
    st.title("Crear nueva rutina")

    # === DATOS CLIENTE ===
    nombre_sel = st.text_input("Nombre del cliente")
    correo = st.text_input("Correo del cliente")
    entrenador = st.text_input("Entrenador responsable")

    dias = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]
    semanas = st.number_input("¿Cuántas semanas quieres generar?", min_value=1, step=1)
    fecha_inicio = st.date_input("Fecha de inicio (lunes)")

    for i in range(len(dias)):
        dia_key = f"rutina_dia_{i+1}"
        if dia_key not in st.session_state:
            st.session_state[dia_key] = []

        st.markdown(f"## {dias[i]}")
        num_ejercicios = st.number_input(f"Cantidad de ejercicios para {dias[i]}", min_value=0, step=1, key=f"num_ej_{i}")

        for j in range(num_ejercicios):
            with st.expander(f"Ejercicio {j+1} - {dias[i]}"):
                ejercicio = st.text_input("Ejercicio", key=f"ejercicio_{i}_{j}")
                series = st.text_input("Series", key=f"series_{i}_{j}")
                repeticiones = st.text_input("Repeticiones", key=f"reps_{i}_{j}")
                peso = st.text_input("Peso", key=f"peso_{i}_{j}")
                velocidad = st.text_input("Velocidad", key=f"velocidad_{i}_{j}")
                rir = st.text_input("RIR", key=f"rir_{i}_{j}")
                tipo = st.text_input("Tipo", key=f"tipo_{i}_{j}")
                circuito = st.text_input("Circuito", key=f"circuito_{i}_{j}")
                seccion = st.text_input("Sección", key=f"seccion_{i}_{j}")

                # 📈 PROGRESIÓN INDIVIDUAL
                st.markdown("### Progresión personalizada")
                col1, col2 = st.columns(2)
                with col1:
                    variable = st.selectbox("Variable a modificar", ["peso", "repeticiones", "rir", "series"], key=f"prog_variable_{i}_{j}")
                    operacion = st.selectbox("Operación", ["suma", "multiplicacion"], key=f"prog_operacion_{i}_{j}")
                with col2:
                    cantidad = st.number_input("Cantidad de cambio", key=f"prog_cantidad_{i}_{j}")
                    semanas_aplicar = st.multiselect("Semanas a aplicar", [2, 3, 4, 5, 6], key=f"prog_semanas_{i}_{j}")

                st.session_state[dia_key].append({
                    "Ejercicio": ejercicio,
                    "Series": series,
                    "Repeticiones": repeticiones,
                    "Peso": peso,
                    "Velocidad": velocidad,
                    "RIR": rir,
                    "Tipo": tipo,
                    "Circuito": circuito,
                    "Sección": seccion,
                    "progresion": {
                        "variable": variable,
                        "cantidad": cantidad,
                        "operacion": operacion,
                        "semanas": semanas_aplicar
                    }
                })

    # === BOTÓN PARA GUARDAR ===
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
                    dia_key = f"rutina_dia_{i+1}"
                    ejercicios = st.session_state.get(dia_key, [])

                    for ejercicio in ejercicios:
                        ejercicio_mod = ejercicio.copy()

                        prog = ejercicio.get("progresion", {})
                        variable = prog.get("variable", "").strip().lower()
                        cantidad = prog.get("cantidad", 0)
                        operacion = prog.get("operacion", "").strip().lower()
                        semanas_aplicar = prog.get("semanas", [])

                        if variable and (semana + 1) in semanas_aplicar:
                            valor_base = ejercicio.get(variable, "").strip()
                            if valor_base:
                                ejercicio_mod[variable] = aplicar_progresion(valor_base, semana + 1, float(cantidad), operacion, 1)

                        doc_id = f"{correo_normalizado}_{fecha_normalizada}_{dia_nombre}_{ejercicio['Circuito']}_{ejercicio['Ejercicio']}".lower().replace(" ", "_")

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
                            "progresion": ejercicio_mod.get("progresion", {}),
                            "tipo": ejercicio_mod["Tipo"],
                            "entrenador": entrenador
                        }

                        db.collection("rutinas").document(doc_id).set(data)

            st.success(f"✅ Rutina generada correctamente para {semanas} semanas.")
        except Exception as e:
            st.error(f"❌ Error al guardar la rutina: {e}")
