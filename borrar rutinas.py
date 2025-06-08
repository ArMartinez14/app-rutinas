import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
import json

if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def borrar_rutinas():
    st.title("🗑️ Borrar Rutinas de un Cliente")

    correo_input = st.text_input("Ingresa el correo del cliente:")

    if correo_input:
        correo_normalizado = correo_input.replace("@", "_").replace(".", "_").lower()

        docs = db.collection("rutinas").stream()
        rutinas = []
        for doc in docs:
            if doc.id.startswith(correo_normalizado):
                data = doc.to_dict()
                rutinas.append({
                    "id": doc.id,
                    "cliente": data.get("cliente", ""),
                    "fecha": data.get("fecha", ""),
                    "dia": data.get("dia", ""),
                    "ejercicio": data.get("ejercicio", ""),
                    "circuito": data.get("circuito", ""),
                })

        if rutinas:
            etiquetas = [
                f"{r['fecha']} | Día {r['dia']} | {r['circuito']} - {r['ejercicio']}" for r in rutinas
            ]
            seleccionadas = st.multiselect("Selecciona las rutinas a eliminar:", etiquetas)

            if st.button("Eliminar seleccionadas"):
                for r, etiqueta in zip(rutinas, etiquetas):
                    if etiqueta in seleccionadas:
                        db.collection("rutinas").document(r["id"]).delete()
                st.success("Rutinas eliminadas correctamente.")
        else:
            st.warning("No se encontraron rutinas para ese correo.")
