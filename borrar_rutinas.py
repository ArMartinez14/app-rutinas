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
        # === 1️⃣ Normalizar igual que en crear/editar ===
        correo_normalizado = correo_input.replace("@", "_").replace(".", "_").lower()

        # === 2️⃣ Buscar en la colección correcta ===
        docs = db.collection("rutinas_semanales").stream()
        semanas = {}

        for doc in docs:
            doc_id = doc.id

            if doc_id.startswith(correo_normalizado):
                partes = doc_id.split("_")

                # === 3️⃣ Tomar SIEMPRE las últimas 3 partes como fecha ===
                if len(partes) >= 4:
                    fecha_semana = "_".join(partes[-3:])  # Ej: "2024_06_17"
                    if fecha_semana not in semanas:
                        semanas[fecha_semana] = []
                    semanas[fecha_semana].append(doc.id)

        if not semanas:
            st.warning("No se encontraron rutinas para ese correo.")
            return

        semanas_ordenadas = sorted(semanas.keys(), reverse=True)

        st.markdown("### Selecciona las semanas que deseas eliminar:")
        semanas_seleccionadas = []
        for semana in semanas_ordenadas:
            if st.checkbox(f"Semana {semana}", key=semana):
                semanas_seleccionadas.append(semana)

        if semanas_seleccionadas and st.button("🗑️ Eliminar semanas seleccionadas"):
            for semana in semanas_seleccionadas:
                for doc_id in semanas[semana]:
                    db.collection("rutinas_semanales").document(doc_id).delete()
            st.success("✅ Se eliminaron las semanas seleccionadas correctamente.")
