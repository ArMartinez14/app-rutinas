
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

st.set_page_config(page_title="🔥 TEST FIREBASE 🔥")

# === Inicializar Firebase de forma segura ===
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = get_db()

st.title("🔍 Verificador de Credenciales Firebase")

# Botón de prueba
if st.button("TEST CONEXIÓN FIRESTORE"):
    try:
        docs = db.collection("usuarios").limit(1).get()
        for doc in docs:
            st.write("✅ Documento encontrado:")
            st.json(doc.to_dict())
        st.success("🎉 Conexión Firestore correcta, credenciales funcionando.")
    except Exception as e:
        st.error(f"❌ ERROR: {e}")
