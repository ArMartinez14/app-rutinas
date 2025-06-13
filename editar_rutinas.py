import streamlit as st
from firebase_admin import credentials, firestore
from datetime import datetime
import firebase_admin
import json

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def editar_rutinas():
    st.title("✏️ Editar Rutina y Aplicar Cambios a Futuras Semanas")

    correo = st.text_input("Correo del cliente:")
    if not correo:
        return

    # === Obtener semanas disponibles ===
    docs = db.collection("rutinas_semanales") \
        .where("correo", "==", correo) \
        .stream()

    semanas_dict = {}
    for doc in docs:
        data = doc.to_dict()
        fecha_lunes = data.get("fecha_lunes")
        if fecha_lunes:
            semanas_dict[fecha_lunes] = doc.id

    semanas = sorted(semanas_dict.keys())
    semana_sel = st.selectbox("Selecciona la semana a editar:", semanas)
    if not semana_sel:
        return

    doc_id_semana = semanas_dict[semana_sel]
    doc_ref = db.collection("rutinas_semanales").document(doc_id_semana)
    doc_data = doc_ref.get().to_dict()
    rutina = doc_data.get("rutina", {})

    dias_disponibles = sorted(rutina.keys(), key=lambda x: int(x))
    dia_sel = st.selectbox("Selecciona el día a editar:", dias_disponibles, format_func=lambda x: f"Día {x}")
    if not dia_sel:
        return

    st.markdown(f"### 📝 Editar ejercicios del Día {dia_sel}")

    cols = st.columns([3, 1, 2, 2, 1])
    cols[0].markdown("**Ejercicio**")
    cols[1].markdown("**Series**")
    cols[2].markdown("**Reps**")
    cols[3].markdown("**Peso**")
    cols[4].markdown("**RIR**")

    ejercicios_editables = []
    dia_rutina = rutina.get(dia_sel, [])

    for idx, ejercicio in enumerate(dia_rutina):
        col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 1])
        ejercicio_editado = ejercicio.copy()
        ejercicio_editado["ejercicio"] = col1.text_input("", value=ejercicio.get("ejercicio", ""), key=f"ej_{idx}_nombre")
        ejercicio_editado["series"] = col2.number_input("", value=int(ejercicio.get("series", 0)), key=f"ej_{idx}_series")
        ejercicio_editado["repeticiones"] = int(col3.text_input("", value=str(ejercicio.get("repeticiones", ejercicio.get("reps", ""))), key=f"ej_{idx}_reps")) if col3.text_input("", value=str(ejercicio.get("repeticiones", ejercicio.get("reps", ""))), key=f"ej_{idx}_reps") else None
        ejercicio_editado["peso"] = col4.text_input("", value=str(ejercicio.get("peso", "")), key=f"ej_{idx}_peso") or None
        ejercicio_editado["rir"] = col5.text_input("", value=ejercicio.get("rir", ""), key=f"ej_{idx}_rir") or None
        ejercicios_editables.append(ejercicio_editado)

    if st.button("✅ Aplicar cambios a este día y futuras semanas", key=f"btn_guardar_cambios_{dia_sel}"):
        try:
            fecha_sel = datetime.strptime(semana_sel, "%Y-%m-%d")
        except ValueError:
            st.error(f"Formato de fecha inválido: {semana_sel}")
            return

        # Actualizar solo en semanas >= a la actual
        futuros = db.collection("rutinas_semanales") \
            .where("correo", "==", correo) \
            .stream()

        total_actualizados = 0

        for doc in futuros:
            data = doc.to_dict()
            fecha_doc_str = data.get("fecha_lunes", "")
            try:
                fecha_doc = datetime.strptime(fecha_doc_str, "%Y-%m-%d")
                if fecha_doc == fecha_sel or fecha_doc > fecha_sel:
                    rutina_futura = doc.to_dict().get("rutina", {})
                    if dia_sel in rutina_futura:
                        rutina_futura[dia_sel] = ejercicios_editables
                        db.collection("rutinas_semanales").document(doc.id).update({"rutina": rutina_futura})
                        total_actualizados += 1
            except:
                pass

        st.success(f"✅ Cambiado exitosamente en {total_actualizados} semana(s) (incluyendo la actual si corresponde).")
        st.info(f"🗓️ Semana modificada: {semana_sel}")

        # Recargar documento actualizado para reflejar cambios en pantalla
        if semana_sel in semanas_dict:
            doc_data = db.collection("rutinas_semanales").document(semanas_dict[semana_sel]).get().to_dict()
            rutina = doc_data.get("rutina", {})
            dia_rutina = rutina.get(dia_sel, [])
