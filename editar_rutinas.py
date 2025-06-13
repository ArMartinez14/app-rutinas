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

    # === Buscar semanas disponibles para ese cliente ===
    docs = db.collection("rutinas").stream()
    semanas = set()
    ejercicios_por_dia = {}

    for doc in docs:
        doc_id = doc.id
        if doc_id.startswith(correo_normalizado):
            partes = doc_id.split("_")
            if len(partes) >= 6:
                fecha = f"{partes[3]}_{partes[4]}_{partes[5]}"
                semanas.add(fecha)

    semanas = sorted(semanas)
    semana_sel = st.selectbox("Selecciona la semana a editar:", semanas)

    if not semana_sel:
        return

    # === Agrupar ejercicios por día ===
    for doc in db.collection("rutinas").stream():
        if semana_sel in doc.id and doc.id.startswith(correo_normalizado):
            data = doc.to_dict()
            dia = data.get("dia", "")
            if dia not in ejercicios_por_dia:
                ejercicios_por_dia[dia] = []
            ejercicios_por_dia[dia].append((doc.id, data))

    dias_disponibles = sorted(ejercicios_por_dia.keys(), key=lambda x: int(x))
    dia_sel = st.selectbox("Selecciona el día a editar:", dias_disponibles, format_func=lambda x: f"Día {x}")

    st.markdown(f"### 📝 Editar ejercicios del Día {dia_sel}")

    # Encabezado
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

        if st.button("✅ Aplicar cambios a este día y futuras semanas", key="btn_guardar_cambios"):

            try:
                fecha_sel = datetime.strptime(semana_sel, "%Y-%m-%d")  # CAMBIO AQUÍ
            except ValueError:
                st.error(f"Formato de fecha inválido: {semana_sel}")
                return

        total_actualizados = 0

        for cambio in ejercicios_editables:
            nombre_original = cambio["original"]
            dia_original = cambio["dia"]
            circuito_original = cambio["circuito"]

            for doc in db.collection("rutinas").stream():
                data = doc.to_dict()
                if (
                        data.get("correo", "").replace("@", "_").replace(".", "_").lower() == correo_normalizado and
                        data.get("ejercicio", "") == nombre_original and
                        data.get("dia", "") == dia_original and
                        data.get("circuito", "") == circuito_original
                ):
                    fecha_doc_str = data.get("fecha_lunes", "")
                    try:
                        fecha_doc = datetime.strptime(fecha_doc_str, "%Y-%m-%d")
                        if fecha_doc >= fecha_sel:
                            db.collection("rutinas").document(doc.id).update({
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
