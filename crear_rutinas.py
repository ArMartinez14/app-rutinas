import streamlit as st
from datetime import date


def crear_rutinas():
    st.title("🛠️ Crear nueva rutina")

    with st.form("form_rutina"):
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("👤 Nombre del cliente")
            correo = st.text_input("📧 Correo electrónico")
            entrenador = st.text_input("🏋️ Entrenador responsable")

        with col2:
            fecha_inicio = st.date_input("📅 Fecha de inicio", value=date.today())
            semanas = st.number_input("🔁 Semanas a repetir", min_value=1, max_value=12, value=4, step=1)

        st.markdown("---")
        st.info("💡 Próximamente aquí irán los campos para cargar ejercicios por día, con sus progresiones si corresponde.")

        submitted = st.form_submit_button("✅ Crear rutina")

        if submitted:
            st.success("📦 Datos listos para ser procesados (falta implementación del guardado en Firestore o Google Sheets).")
