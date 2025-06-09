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

    # === Mostrar ejercicios de la semana seleccionada ===
    ejercicios_editables = []
    st.markdown("### 📝 Editar ejercicios de la semana")

    for doc in db.collection("rutinas").stream():
        if semana_sel in doc.id and doc.id.startswith(correo_normalizado):
            data = doc.to_dict()
            ejercicio_editado = {
                "doc_id": doc.id,
                "original": data.get("ejercicio", ""),
                "dia": data.get("dia", ""),
                "circuito": data.get("circuito", ""),
                "ejercicio": st.text_input(f"Ejercicio (día {data.get('dia')}, circuito {data.get('circuito')}):", value=data.get("ejercicio", ""), key=doc.id + "_ejercicio"),
                "series": st.number_input("Series", value=int(data.get("series", 0)), key=doc.id + "_series"),
                "reps": st.text_input("Reps", value=data.get("reps", ""), key=doc.id + "_reps"),
                "peso": st.text_input("Peso", value=data.get("peso", ""), key=doc.id + "_peso"),
                "rir": st.text_input("RIR", value=data.get("rir", ""), key=doc.id + "_rir")
            }
            ejercicios_editables.append(ejercicio_editado)
            st.markdown("---")

    if st.button("✅ Aplicar cambios a esta y futuras semanas"):
        fecha_sel = datetime.strptime(semana_sel, "%Y_%m_%d")
        total_actualizados = 0

        for cambio in ejercicios_editables:
            nombre_original = cambio["original"]
            for doc in db.collection("rutinas").stream():
                if doc.id.startswith(correo_normalizado) and nombre_original in doc.id:
                    partes = doc.id.split("_")
                    if len(partes) >= 6:
                        fecha_doc = datetime.strptime(f"{partes[3]}_{partes[4]}_{partes[5]}", "%Y_%m_%d")
                        if fecha_doc >= fecha_sel:
                            db.collection("rutinas").document(doc.id).update({
                                "ejercicio": cambio["ejercicio"],
                                "series": cambio["series"],
                                "reps": cambio["reps"],
                                "peso": cambio["peso"],
                                "rir": cambio["rir"]
                            })
                            total_actualizados += 1
        st.success(f"Cambios aplicados correctamente a {total_actualizados} ejercicios.")
