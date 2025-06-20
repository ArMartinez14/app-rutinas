import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from collections import defaultdict
import json

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# === FUNCIONES AUXILIARES ===
def obtener_fecha_lunes():
    hoy = datetime.now()
    lunes = hoy - timedelta(days=hoy.weekday())
    return lunes.strftime("%Y-%m-%d")

def es_entrenador(rol):
    return rol.lower() in ["entrenador", "admin", "administrador"]

def ordenar_circuito(ejercicio):
    orden = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
    return orden.get(ejercicio.get("circuito", ""), 99)

# === ESTILOS PERSONALIZADOS ===
st.set_page_config(page_title="Rutinas Semanales", layout="centered")
st.markdown("""
    <style>
    body, .stApp {
        background-color: #000000;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white;
    }
    .block-container {
        padding: 1rem;
    }
    .titulo-bloque {
        background-color: #8B0000;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 1.3rem;
        margin-top: 1rem;
    }
    .circuito {
        color: #ff4d4d;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    .compact-input input {
        height: 22px !important;
        font-size: 11px !important;
        padding: 2px 4px !important;
        width: 42px !important;
    }
    </style>
""", unsafe_allow_html=True)

logo_base64 = st.secrets["LOGO_BASE64"]
st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 1rem;'>
        <img src="data:image/png;base64,{logo_base64.strip()}" style="max-height:45px;" />
    </div>
    """,
    unsafe_allow_html=True
)

correo = st.text_input("🔑 Ingresa tu correo:")

if correo:
    correo = correo.strip().lower()
    doc_user = db.collection("usuarios").document(correo).get()
    if not doc_user.exists:
        st.error("❌ Este correo no está registrado.")
        st.stop()

    datos_usuario = doc_user.to_dict()
    nombre = datos_usuario.get("nombre", "Usuario")
    rol = datos_usuario.get("rol", "desconocido")

    st.success(f"Bienvenido {nombre} ({rol})")

    if es_entrenador(rol):
        todas_rutinas = db.collection("rutinas").stream()
    else:
        todas_rutinas = db.collection("rutinas").where("correo", "==", correo).stream()

    rutinas_list = [r.to_dict() for r in todas_rutinas]

    if not rutinas_list:
        st.warning("⚠️ No se encontraron rutinas registradas.")
        st.stop()

    clientes = sorted(set(r["cliente"] for r in rutinas_list if "cliente" in r))
    cliente_input = st.text_input("👤 Escribe el nombre del cliente:", key="cliente")
    cliente_opciones = [c for c in clientes if cliente_input.lower() in c.lower()]
    cliente_sel = st.selectbox("O selecciona de la lista:", cliente_opciones if cliente_opciones else clientes)

    rutinas_cliente = [r for r in rutinas_list if r.get("cliente") == cliente_sel]
    semanas = sorted({r["fecha_lunes"] for r in rutinas_cliente}, reverse=True)

    semana_actual = obtener_fecha_lunes()
    semana_sel = st.selectbox("📆 Selecciona la semana", semanas, index=semanas.index(semana_actual) if semana_actual in semanas else 0, key="semana")

    rutinas = [r for r in rutinas_cliente if r["fecha_lunes"] == semana_sel]

    if not rutinas:
        st.warning("⚠️ No hay rutinas registradas para esta semana.")
        st.stop()

    dias = sorted(set(r["dia"] for r in rutinas), key=lambda x: int(x))
    dia_sel = st.selectbox("📅 Selecciona el día", dias, key="dia")

    if st.button("👀 Ver rutina"):
        st.session_state.mostrar_rutina = True

    if st.session_state.get("mostrar_rutina"):
        ejercicios = [r for r in rutinas if r["dia"] == dia_sel]

        if ejercicios:
            semana_ciclo = ejercicios[0].get("semana_ciclo", "")
            if semana_ciclo:
                st.markdown(f"### {semana_ciclo}")

        ejercicios.sort(key=ordenar_circuito)
        bloques = defaultdict(list)
        for e in ejercicios:
            bloques[e["bloque"]].append(e)

        for bloque in ["Warm-up", "Workout"]:
            if bloque in bloques:
                st.markdown(f"<div class='titulo-bloque'>{bloque}</div>", unsafe_allow_html=True)
                circuitos = defaultdict(list)
                for e in bloques[bloque]:
                    circuito = e.get("circuito", "Z")
                    circuitos[circuito].append(e)

                for circuito in sorted(circuitos.keys()):
                    st.markdown(f"<div class='circuito'>Circuito {circuito}</div>", unsafe_allow_html=True)
                    for e in circuitos[circuito]:
                        with st.expander(f"{e['ejercicio']}"):
                            st.markdown(f"**🎯 Objetivo:** {e.get('series', 0)} × {e.get('repeticiones', 0)} reps @ {e.get('peso', 0)} kg")
                            num_series = e.get("series") or 0
                            registro_series = e.get("registro_series", [{}]*num_series)

                            header_cols = st.columns([1, 1, 1])
                            header_cols[0].markdown("**Serie**")
                            header_cols[1].markdown("**Reps**")
                            header_cols[2].markdown("**Peso (kg)**")

                            nuevas_series = []
                            for i in range(num_series):
                                col1, col2, col3 = st.columns([1, 1, 1])
                                col1.markdown(f"{i + 1}")
                                with col2:
                                    st.markdown("<div class='compact-input'>", unsafe_allow_html=True)
                                    reps_input = st.text_input("Reps", value=registro_series[i].get("reps", ""), key=f"reps_{e['ejercicio']}_{i}", label_visibility="collapsed")
                                    st.markdown("</div>", unsafe_allow_html=True)
                                with col3:
                                    st.markdown("<div class='compact-input'>", unsafe_allow_html=True)
                                    peso_input = st.text_input("Peso", value=registro_series[i].get("peso", ""), key=f"peso_{e['ejercicio']}_{i}", label_visibility="collapsed")
                                    st.markdown("</div>", unsafe_allow_html=True)
                                nuevas_series.append({"reps": reps_input, "peso": peso_input})

                            comentario_input = st.text_input("📝 Comentario", value=e.get("comentario", ""), key=f"coment_{e['ejercicio']}")

                            if e.get("video"):
                                st.video(e["video"])

                            # 🛠️ Normalizar correo y fecha
                            correo_normalizado = e["correo"].replace("@", "_").replace(".", "_")
                            fecha_normalizada = e["fecha_lunes"].replace("-", "_")

                            # 🔐 Crear ID del documento
                            doc_id = f"{correo_normalizado}_{fecha_normalizada}_{e['dia']}_{e['circuito']}_{e['ejercicio']}".lower().replace(
                                " ", "_")
                            doc_ref = db.collection("rutinas").document(doc_id)

                            if st.button(f"💾 Guardar cambios - {e['ejercicio']}", key=f"guardar_{e['ejercicio']}"):
                                try:
                                    doc_ref.update({
                                        "registro_series": nuevas_series,
                                        "comentario": comentario_input
                                    })
                                    st.success("✅ Registro actualizado exitosamente.")
                                except Exception as error:
                                    st.error("❌ No se pudo guardar. Es posible que el documento no exista con ese ID.")
                                    st.exception(error)
