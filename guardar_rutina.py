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

                    # Aplicar progresiones múltiples (1 a 5)
                    for variable_objetivo in ["peso", "repeticiones", "rir", "tiempo", "velocidad"]:
                        valor_original = ejercicio.get(variable_objetivo, "")
                        if not valor_original:
                            continue  # ignorar si no hay valor

                        valor_actual = valor_original

                        for n in range(1, 6):
                            var = ejercicio.get(f"progresion_{n}_variable", "").strip().lower()
                            cantidad = ejercicio.get(f"progresion_{n}_cantidad", "")
                            operacion = ejercicio.get(f"progresion_{n}_operacion", "").strip().lower()
                            semanas_txt = ejercicio.get(f"progresion_{n}_semanas", "")

                            if var != variable_objetivo or not cantidad or not operacion:
                                continue

                            try:
                                semanas_aplicar = [int(s.strip()) for s in semanas_txt.split(",") if s.strip().isdigit()]
                            except:
                                semanas_aplicar = []

                            for s in range(2, semana + 2):  # semana + 1 es semana actual (indexada desde 0)
                                if s in semanas_aplicar:
                                    valor_actual = aplicar_progresion(valor_actual, float(cantidad), operacion)

                        ejercicio_mod[variable_objetivo] = valor_actual

                    # === GUARDAR EN FIRESTORE ===
                    doc_id = f"{correo_normalizado}_{fecha_normalizada}_{numero_dia}_{ejercicio.get('Circuito', ejercicio.get('circuito', ''))}_{ejercicio.get('Ejercicio', ejercicio.get('ejercicio', ''))}".lower().replace(" ", "_")


                    data = {
                        "cliente": nombre_normalizado,
                        "correo": correo,
                        "semana": str(semana + 1),
                        "fecha_lunes": fecha_str,
                        "dia": numero_dia,
                        "bloque": ejercicio_mod.get("Sección", ""),
                        "circuito": ejercicio_mod.get("Circuito", ""),
                        "ejercicio": ejercicio_mod.get("Ejercicio", ""),
                        "series": ejercicio_mod.get("Series", ""),
                        "repeticiones": ejercicio_mod.get("Repeticiones", ""),
                        "peso": ejercicio_mod.get("Peso", ""),
                        "tiempo": ejercicio_mod.get("Tiempo", ""),
                        "velocidad": ejercicio_mod.get("Velocidad", ""),
                        "rir": ejercicio_mod.get("Rir", ""),
                        "tipo": ejercicio_mod.get("Tipo", ""),
                        "entrenador": entrenador
                    }

                    db.collection("rutinas").document(doc_id).set(data)

        st.success(f"✅ Rutina generada correctamente para {semanas} semanas.")

    except Exception as e:
        st.error(f"❌ Error al guardar la rutina: {e}")
