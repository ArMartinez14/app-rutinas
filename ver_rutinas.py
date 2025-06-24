import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import json
from utils import actualizar_progresiones_individual

def ver_rutinas():
    # === INICIALIZAR FIREBASE SOLO UNA VEZ ===
    if not firebase_admin._apps:
        cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
        with open("/tmp/firebase.json", "w") as f:
            json.dump(cred_dict, f)
        cred = credentials.Certificate("/tmp/firebase.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # === Funciones utilitarias ===
    def obtener_fecha_lunes():
        hoy = datetime.now()
        lunes = hoy - timedelta(days=hoy.weekday())
        return lunes.strftime("%Y-%m-%d")

    def normalizar_correo(correo):
        return correo.strip().lower().replace("@", "_").replace(".", "_")

    def es_entrenador(rol):
        return rol.lower() in ["entrenador", "admin", "administrador"]

    def ordenar_circuito(ejercicio):
        orden = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
        return orden.get(ejercicio.get("circuito", ""), 99)

    @st.cache_data
    def cargar_rutinas_filtradas(correo, rol):
        if es_entrenador(rol):
            docs = db.collection("rutinas_semanales").stream()
        else:
            docs = db.collection("rutinas_semanales").where("correo", "==", correo).stream()
        return [doc.to_dict() for doc in docs]

    # === INPUT CORREO ===
    correo_input = st.text_input("🔑 Ingresa tu correo:", key="correo_input")
    if not correo_input:
        st.stop()

    correo_raw = correo_input.strip()
    correo = correo_raw.lower()
    correo_norm = normalizar_correo(correo_raw)

    # === Verificar usuario ===
    doc_user = db.collection("usuarios").document(correo).get()
    if not doc_user.exists:
        st.error("❌ Este correo no está registrado.")
        st.stop()

    datos_usuario = doc_user.to_dict()
    nombre = datos_usuario.get("nombre", "Usuario")
    rol = datos_usuario.get("rol", "desconocido")

    mostrar_info = st.checkbox("👤 Mostrar información personal", value=True)
    if mostrar_info:
        st.success(f"Bienvenido {nombre} ({rol})")

    # === Cargar rutinas ===
    rutinas = cargar_rutinas_filtradas(correo, rol)
    if not rutinas:
        st.warning("⚠️ No se encontraron rutinas.")
        st.stop()

    if mostrar_info:
        clientes = sorted(set(r["cliente"] for r in rutinas if "cliente" in r))
        cliente_input = st.text_input("👤 Escribe el nombre del cliente:", key="cliente_input")
        cliente_opciones = [c for c in clientes if cliente_input.lower() in c.lower()]
        cliente_sel = st.selectbox("Selecciona cliente:", cliente_opciones if cliente_opciones else clientes, key="cliente_sel")

        rutinas_cliente = [r for r in rutinas if r.get("cliente") == cliente_sel]
        semanas = sorted({r["fecha_lunes"] for r in rutinas_cliente}, reverse=True)
        semana_actual = obtener_fecha_lunes()
        semana_sel = st.selectbox("📆 Semana", semanas, index=semanas.index(semana_actual) if semana_actual in semanas else 0, key="semana_sel")
    else:
        rutinas_cliente = rutinas
        semanas = sorted({r["fecha_lunes"] for r in rutinas_cliente}, reverse=True)
        semana_sel = obtener_fecha_lunes()

    rutina_doc = next((r for r in rutinas_cliente if r["fecha_lunes"] == semana_sel), None)
    if not rutina_doc:
        st.warning("⚠️ No hay rutina para esa semana.")
        st.stop()

    dias_disponibles = sorted(rutina_doc["rutina"].keys(), key=int)
    dia_sel = st.selectbox("📅 Día", dias_disponibles, key="dia_sel")

    ejercicios = rutina_doc["rutina"][dia_sel]
    ejercicios.sort(key=ordenar_circuito)

    st.markdown(f"### Ejercicios del día {dia_sel}")

    st.markdown("""
        <style>
        .compact-input input { font-size: 12px !important; width: 100px !important; }
        .linea-blanca { border-bottom: 2px solid white; margin: 15px 0; }
        .ejercicio { font-size: 18px !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # === FOR para mostrar y modificar la lista DIRECTAMENTE ===
    ejercicios_por_circuito = {}
    for e in ejercicios:
        circuito = e.get("circuito", "Z").upper()
        ejercicios_por_circuito.setdefault(circuito, []).append(e)

    for circuito, lista in sorted(ejercicios_por_circuito.items()):
        if circuito == "A":
            st.subheader("Warm-Up")
        elif circuito == "D":
            st.subheader("Workout")

        st.markdown(f"### Circuito {circuito}")
        st.markdown("<div class='bloque'>", unsafe_allow_html=True)

        for idx, e in enumerate(lista):
            ejercicio = e.get("ejercicio", f"Ejercicio {idx+1}")
            series = e.get("series", "")
            reps = e.get("repeticiones", "")
            peso = e.get("peso", "")
            ejercicio_id = f"{circuito}_{ejercicio}_{idx}".lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "")

            st.markdown(
                f"<div class='ejercicio'>{ejercicio} &nbsp; <span style='font-size:16px; font-weight:normal;'>{series}x{reps} · {peso}kg</span></div>",
                unsafe_allow_html=True
            )

            mostrar = st.checkbox(f"Editar ejercicio {idx+1}", key=f"edit_{circuito}_{idx}")

            if mostrar:
                col1, col2 = st.columns([3, 1])
                with col1:
                    e["peso_alcanzado"] = st.text_input("", value=e.get("peso_alcanzado", ""), placeholder="Peso", key=f"peso_{ejercicio_id}", label_visibility="collapsed")
                    e["comentario"] = st.text_input("", value=e.get("comentario", ""), placeholder="Comentario", key=f"coment_{ejercicio_id}", label_visibility="collapsed")
                with col2:
                    e["rir"] = st.text_input("", value=e.get("rir", ""), placeholder="RIR", key=f"rir_{ejercicio_id}", label_visibility="collapsed")

            if e.get("video"):
                st.video(e["video"])

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='linea-blanca'></div>", unsafe_allow_html=True)

    # === BOTÓN GUARDAR ===
    # === BOTÓN GUARDAR CAMBIOS DEL DÍA ===
    if st.button("💾 Guardar cambios del día (agregar peso_alcanzado si falta)", key=f"guardar_{dia_sel}_{semana_sel}"):
        fecha_norm = semana_sel.replace("-", "_")
        doc_id = f"{correo_norm}_{fecha_norm}"

        try:
            doc_ref = db.collection("rutinas_semanales").document(doc_id)
            doc = doc_ref.get()

            if not doc.exists:
                st.error(f"❌ No existe el doc {doc_id}")
                st.stop()

            data = doc.to_dict()
            rutina = data.get("rutina", {})
            dia_sel = str(dia_sel)
            ejercicios_originales = rutina.get(dia_sel, [])

            if not ejercicios_originales:
                st.warning(f"⚠️ No hay ejercicios para día {dia_sel}.")
                st.stop()

            # ✅ Reconstruir lista: agregar peso_alcanzado si falta, y sobrescribir con los inputs si existen
            ejercicios_actualizados = []
            for idx, e in enumerate(ejercicios_originales):
                nuevo = e.copy()
                # Si NO tiene peso_alcanzado, agregarlo en blanco
                if "peso_alcanzado" not in nuevo:
                    nuevo["peso_alcanzado"] = ""
                # Si existe input de UI, actualizarlo
                nuevo["peso_alcanzado"] = st.session_state.get(f"peso_alcanzado_{idx}", nuevo["peso_alcanzado"])
                nuevo["rir"] = st.session_state.get(f"rir_{idx}", nuevo.get("rir", ""))
                nuevo["comentario"] = st.session_state.get(f"comentario_{idx}", nuevo.get("comentario", ""))
                ejercicios_actualizados.append(nuevo)

            # ✅ Mostrar JSON para verificar
            st.write("🚨 LISTA FINAL A SUBIR 🚨")
            st.json(ejercicios_actualizados)

            # ✅ Guardar usando .set(..., merge=True)
            doc_ref.set({f"rutina.{dia_sel}": ejercicios_actualizados}, merge=True)
            st.success(f"✅ Día {dia_sel} actualizado: ahora todos tienen peso_alcanzado.")

            # === Progresión y delta ===
            semanas_futuras = sorted([s for s in semanas if s > semana_sel])

            for e in ejercicios_actualizados:
                if e.get("peso_alcanzado"):
                    actualizar_progresiones_individual(
                        nombre=data.get("cliente", ""),
                        correo=correo_raw,
                        ejercicio=e["ejercicio"],
                        circuito=e.get("circuito", ""),
                        bloque=e.get("bloque", e.get("seccion", "")),
                        fecha_actual_lunes=semana_sel,
                        dia_numero=int(dia_sel),
                        peso_alcanzado=float(e["peso_alcanzado"])
                    )

                    try:
                        peso_alcanzado = float(e["peso_alcanzado"])
                        peso_actual = float(e.get("peso", 0))
                        delta = peso_alcanzado - peso_actual
                        if delta == 0:
                            continue

                        nombre_ejercicio = e["ejercicio"]
                        circuito = e.get("circuito", "")
                        bloque = e.get("bloque", e.get("seccion", ""))
                        peso_base = peso_actual

                        for s in semanas_futuras:
                            peso_base += delta
                            fecha_norm_futura = s.replace("-", "_")
                            doc_id_futuro = f"{correo_norm}_{fecha_norm_futura}"
                            doc_ref_futuro = db.collection("rutinas_semanales").document(doc_id_futuro)
                            doc_futuro = doc_ref_futuro.get()

                            if doc_futuro.exists:
                                data_fut = doc_futuro.to_dict()
                                rutina_fut = data_fut.get("rutina", {})
                                ejercicios_fut = rutina_fut.get(dia_sel, [])

                                for ef in ejercicios_fut:
                                    if (
                                        ef.get("ejercicio") == nombre_ejercicio and
                                        ef.get("circuito") == circuito and
                                        (ef.get("bloque") == bloque or ef.get("seccion") == bloque)
                                    ):
                                        ef["peso"] = round(peso_base, 2)

                                doc_ref_futuro.update({f"rutina.{dia_sel}": ejercicios_fut})

                    except Exception as inner_error:
                        st.warning(f"⚠️ Error aplicando delta: {inner_error}")

        except Exception as error:
            st.error("❌ Error guardando (Firestore).")
            st.exception(error)