import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
import json

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def borrar_rutinas():
    st.title("🗑️ Borrar Rutinas por Semana")

    correo_input = st.text_input("Ingresa el correo del cliente:")

    if correo_input:
        correo_normalizado = correo_input.replace("@", "_").replace(".", "_").lower()

        docs = db.collection("rutinas").stream()
        semanas = {}

        for doc in docs:
            doc_id = doc.id
            if doc_id.startswith(correo_normalizado):
                partes = doc_id.split("_")
                if len(partes) >= 4:
                    fecha_semana = f"{partes[1]}_{partes[2]}_{partes[3]}"
                    if fecha_semana not in semanas:
                        semanas[fecha_semana] = []
                    semanas[fecha_semana].append(doc.id)

        if not semanas:
            st.warning("No se encontraron rutinas para ese correo.")
            return

        semanas_ordenadas = sorted(semanas.keys(), reverse=True)
        semana_sel = st.selectbox("Selecciona la semana que deseas eliminar:", semanas_ordenadas)

        if st.button("Eliminar rutina completa de la semana"):
            for doc_id in semanas[semana_sel]:
                db.collection("rutinas").document(doc_id).delete()
            st.success(f"Rutinas de la semana {semana_sel} eliminadas correctamente.")
