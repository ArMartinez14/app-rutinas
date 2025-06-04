from firebase_admin import firestore
from datetime import timedelta
from utils import aplicar_progresion, normalizar_texto
import streamlit as st

def guardar_rutina(nombre_sel, correo, entrenador, fecha_inicio, semanas, dias):
    db = firestore.client()

    try:
        for semana in range(int(semanas)):
            fecha_semana = fecha_inicio + timedelta(weeks=semana)
            fecha_str = fecha_semana.strftime("%Y-%m-%d")
            fecha_normalizada = fecha_semana.strftime("%Y_%m_%d")
            correo_normalizado = correo.replace("@", "_").replace(".", "_")
            nombre_normalizado = normalizar_texto(nombre_sel)

            for i, dia_nombre in enumerate(dias):
                dia_key = f"rutina_dia_{i + 1}"
                ejercicios = st.session_state.get(dia_key, [])

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

                    if variable and operacion and cantidad:
                        valor_base = ejercicio.get(variable.capitalize(), "")
                        if valor_base:
                            valor_actual = valor_base
                            for s in range(2, semana + 2):
                                if s in semanas_aplicar:
                                    valor_actual = aplicar_progresion(valor_actual, float(cantidad), operacion)
                            ejercicio_mod[variable.capitalize()] = valor_actual

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
                        "tiempo": ejercicio_mod["Tiempo"],
                        "velocidad": ejercicio_mod["Velocidad"],
                        "rir": ejercicio_mod["RIR"],
                        "tipo": ejercicio_mod["Tipo"],
                        "entrenador": entrenador
                    }

                    db.collection("rutinas").document(doc_id).set(data)

        st.success(f"✅ Rutina generada correctamente para {semanas} semanas.")

    except Exception as e:
        st.error(f"❌ Error al guardar la rutina: {e}")
