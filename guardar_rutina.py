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
            nombre_normalizado = normalizar_texto(nombre_sel.title())

            for i, dia_nombre in enumerate(dias):
                dia_key = f"rutina_dia_{i + 1}"
                ejercicios = st.session_state.get(dia_key, [])
                numero_dia = str(i + 1)

                for ejercicio in ejercicios:
                    ejercicio_mod = ejercicio.copy()

                    # Buscar progresiones múltiples: progresion_1_variable, progresion_2_variable, etc.
                    for n in range(1, 6):  # Permitimos hasta 5 progresiones por ejercicio
                        variable_key = f"progresion_{n}_variable"
                        cantidad_key = f"progresion_{n}_cantidad"
                        operacion_key = f"progresion_{n}_operacion"
                        semanas_key = f"progresion_{n}_semanas"

                        variable = ejercicio.get(variable_key, "").strip().lower()
                        cantidad = ejercicio.get(cantidad_key, "")
                        operacion = ejercicio.get(operacion_key, "").strip().lower()
                        semanas_txt = ejercicio.get(semanas_key, "")

                        try:
                            semanas_aplicar = [int(s.strip()) for s in semanas_txt.split(",") if s.strip().isdigit()]
                        except:
                            semanas_aplicar = []

                        if variable and operacion and cantidad:
                            valor_base = ejercicio_mod.get(variable, "")
                            if valor_base:
                                valor_actual = valor_base
                                for s in range(2, semana + 2):
                                    if s in semanas_aplicar:
                                        valor_actual = aplicar_progresion(valor_actual, float(cantidad), operacion)
                                ejercicio_mod[variable] = valor_actual

                    doc_id = f"{correo_normalizado}_{fecha_normalizada}_{numero_dia}_{ejercicio['circuito']}_{ejercicio['ejercicio']}".lower().replace(" ", "_")

                    data = {
                        "cliente": nombre_normalizado,
                        "correo": correo,
                        "semana": str(semana + 1),
                        "fecha_lunes": fecha_str,
                        "dia": numero_dia,
                        "bloque": ejercicio_mod["sección"],
                        "circuito": ejercicio_mod["circuito"],
                        "ejercicio": ejercicio_mod["ejercicio"],
                        "series": ejercicio_mod["series"],
                        "repeticiones": ejercicio_mod["repeticiones"],
                        "peso": ejercicio_mod["peso"],
                        "tiempo": ejercicio_mod["tiempo"],
                        "velocidad": ejercicio_mod["velocidad"],
                        "rir": ejercicio_mod["rir"],
                        "tipo": ejercicio_mod["tipo"],
                        "entrenador": entrenador
                    }

                    db.collection("rutinas").document(doc_id).set(data)

        st.success(f"✅ Rutina generada correctamente para {semanas} semanas.")

    except Exception as e:
        st.error(f"❌ Error al guardar la rutina: {e}")
