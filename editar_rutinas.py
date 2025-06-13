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

    correo_normalizado = correo.replace("@", "_").replace(".", "_").lower()

    # === Obtener semanas disponibles ===
    docs = db.collection("rutinas_semanales") \
        .where("correo", "==", correo) \
        .stream()

    semanas_set = set()
    for doc in docs:
        data = doc.to_dict()
        fecha_lunes = data.get("fecha_lunes")
        if fecha_lunes:
            semanas_set.add(fecha_lunes)

    semanas = sorted(semanas_set)
    semana_sel = st.selectbox("Selecciona la semana a editar:", semanas)
    if not semana_sel:
        return

    # === Obtener ejercicios de esa semana ===
    docs = db.collection("rutinas_semanales") \
        .where("correo", "==", correo) \
        .where("fecha_lunes", "==", semana_sel) \
        .stream()

    ejercicios_por_dia = {}
    for doc in docs:
        data = doc.to_dict()
        dia = data.get("dia", "")
        if dia not in ejercicios_por_dia:
            ejercicios_por_dia[dia] = []
        ejercicios_por_dia[dia].append((doc.id, data))

    try:
        dias_disponibles = sorted(ejercicios_por_dia.keys(), key=lambda x: int(x))
    except ValueError:
        dias_disponibles = sorted(ejercicios_por_dia.keys())
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

    for doc_id, data in ejercicios_por_dia[dia_sel]:
        col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 1])
        ejercicio_editado = {
            "doc_id": doc_id,
            "original": data.get("ejercicio", ""),
            "dia": data.get("dia", ""),
            "circuito": data.get("circuito", ""),
            "ejercicio": col1.text_input("", value=data.get("ejercicio", ""), key=doc_id + "_ejercicio"),
            "series": col2.number_input("", value=int(data.get("series", 0)), key=doc_id + "_series"),
            "reps": col3.text_input("", value=data.get("reps", ""), key=doc_id + "_reps"),
            "peso": col4.text_input("", value=data.get("peso", ""), key=doc_id + "_peso"),
            "rir": col5.text_input("", value=data.get("rir", ""), key=doc_id + "_rir")
        }
        ejercicios_editables.append(ejercicio_editado)

    if st.button("✅ Aplicar cambios a este día y futuras semanas", key=f"btn_guardar_cambios_{dia_sel}"):
        try:
            fecha_sel = datetime.strptime(semana_sel, "%Y-%m-%d")
        except ValueError:
            st.error(f"Formato de fecha inválido: {semana_sel}")
            return

        total_actualizados = 0

        for cambio in ejercicios_editables:
            nombre_original = cambio["original"]
            dia_original = cambio["dia"]
            circuito_original = cambio["circuito"]

            futuros = db.collection("rutinas_semanales") \
                .where("correo", "==", correo) \
                .where("dia", "==", dia_original) \
                .where("ejercicio", "==", nombre_original) \
                .where("circuito", "==", circuito_original) \
                .stream()

            for doc in futuros:
                data = doc.to_dict()
                try:
                    fecha_doc = datetime.strptime(data.get("fecha_lunes", ""), "%Y-%m-%d")
                    if fecha_doc >= fecha_sel:
                        db.collection("rutinas_semanales").document(doc.id).update({
                            "ejercicio": cambio["ejercicio"],
                            "series": cambio["series"],
                            "reps": cambio["reps"],
                            "peso": cambio["peso"],
                            "rir": cambio["rir"]
                        })
                        total_actualizados += 1
                except:
                    pass

        st.success(f"Cambios aplicados correctamente a {total_actualizados} ejercicios.")
