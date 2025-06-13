def ver_rutinas():
    import streamlit as st
    import firebase_admin
    from firebase_admin import credentials, firestore
    from datetime import datetime, timedelta
    import json, os, re
    from utils import actualizar_progresiones_individual

    # === INICIALIZAR FIREBASE ===
    if not firebase_admin._apps:
        cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
        with open("/tmp/firebase.json", "w") as f:
            json.dump(cred_dict, f)
        cred = credentials.Certificate("/tmp/firebase.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # === FUNCIONES AUXILIARES ===
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

    # === ENTRADA DE CORREO ===
    correo_input = st.text_input("🔑 Ingresa tu correo:", key="correo_input")
    if not correo_input:
        st.stop()

    correo = correo_input.strip().lower()
    doc_user = db.collection("usuarios").document(correo).get()
    if not doc_user.exists:
        st.error("❌ Este correo no está registrado.")
        st.stop()

    datos_usuario = doc_user.to_dict()
    nombre = datos_usuario.get("nombre", "Usuario")
    rol = datos_usuario.get("rol", "desconocido")
    st.success(f"Bienvenido {nombre} ({rol})")

    # === CARGAR RUTINAS (caché) ===
    rutinas = cargar_rutinas_filtradas(correo, rol)
    if not rutinas:
        st.warning("⚠️ No se encontraron rutinas.")
        st.stop()

    # === SELECCIÓN DE CLIENTE ===
    clientes = sorted(set(r["cliente"] for r in rutinas if "cliente" in r))
    cliente_input = st.text_input("👤 Escribe el nombre del cliente:", key="cliente_input")
    cliente_opciones = [c for c in clientes if cliente_input.lower() in c.lower()]
    cliente_sel = st.selectbox("Selecciona cliente:", cliente_opciones if cliente_opciones else clientes, key="cliente_sel")

    # === SELECCIÓN DE SEMANA ===
    rutinas_cliente = [r for r in rutinas if r.get("cliente") == cliente_sel]
    semanas = sorted({r["fecha_lunes"] for r in rutinas_cliente}, reverse=True)
    semana_actual = obtener_fecha_lunes()
    semana_sel = st.selectbox("📆 Semana", semanas, index=semanas.index(semana_actual) if semana_actual in semanas else 0, key="semana_sel")

    rutina_doc = next((r for r in rutinas_cliente if r["fecha_lunes"] == semana_sel), None)
    if not rutina_doc:
        st.warning("⚠️ No hay rutina para esa semana.")
        st.stop()

    # === SELECCIÓN DE DÍA ===
    dias_disponibles = sorted(rutina_doc["rutina"].keys(), key=int)
    dia_sel = st.selectbox("📅 Día", dias_disponibles, key="dia_sel")

    ejercicios = rutina_doc["rutina"][dia_sel]
    ejercicios.sort(key=ordenar_circuito)

    st.markdown(f"### Ejercicios del día {dia_sel}")

    # === MOSTRAR Y EDITAR EJERCICIOS ===
    for idx, e in enumerate(ejercicios):
        circuito = e.get("circuito", "Z").upper()
        ejercicio = e.get("ejercicio", f"Ejercicio {idx+1}")
        series = e.get("series", "")
        reps = e.get("repeticiones", "")
        peso = e.get("peso", "")
        detalles = f"{series}x{reps}" if series and reps else ""
        detalles += f" · {peso}kg" if peso else ""

        # Clave única por ejercicio
        ejercicio_id = f"{circuito}_{ejercicio}_{idx}".lower().replace(" ", "_").replace("(", "").replace(")", "")

    # Mostrar encabezado como botón
    if f"mostrar_inputs_{ejercicio_id}" not in st.session_state:
        st.session_state[f"mostrar_inputs_{ejercicio_id}"] = False

    if st.button(f"**{circuito} - {ejercicio}** {detalles}", key=f"btn_{ejercicio_id}"):
        st.session_state[f"mostrar_inputs_{ejercicio_id}"] = not st.session_state[f"mostrar_inputs_{ejercicio_id}"]

    if st.session_state[f"mostrar_inputs_{ejercicio_id}"]:
        col1, col2 = st.columns(2)
        with col1:
            e["peso_alcanzado"] = st.text_input(
                "", value=e.get("peso_alcanzado", ""), placeholder="Peso Alcanzado", key=f"peso_{ejercicio_id}",
                label_visibility="collapsed"
            )
        with col2:
            e["rir"] = st.text_input(
                "", value=e.get("rir", ""), placeholder="RIR", key=f"rir_{ejercicio_id}",
                label_visibility="collapsed"
            )
        e["comentario"] = st.text_input(
            "", value=e.get("comentario", ""), placeholder="Comentario", key=f"coment_{ejercicio_id}",
            label_visibility="collapsed"
        )

    if e.get("video"):
        st.video(e["video"])



    # === GUARDAR CAMBIOS DEL DÍA ===
    if st.button("💾 Guardar cambios del día"):
        correo_norm = normalizar_correo(correo)
        fecha_norm = semana_sel.replace("-", "_")
        doc_id = f"{correo_norm}_{fecha_norm}"

        try:
            db.collection("rutinas_semanales").document(doc_id).update({
                f"rutina.{dia_sel}": ejercicios
            })
            st.success("✅ Día actualizado correctamente.")

            for e in ejercicios:
                if e.get("peso_alcanzado"):
                    actualizar_progresiones_individual(
                        nombre=rutina_doc.get("cliente", ""),
                        correo=correo,
                        ejercicio=e["ejercicio"],
                        circuito=e.get("circuito", ""),
                        bloque=e.get("bloque", e.get("seccion", "")),
                        fecha_actual_lunes=semana_sel,
                        dia_numero=int(dia_sel),
                        peso_alcanzado=float(e["peso_alcanzado"])
                    )

        except Exception as error:
            st.error("❌ Error al guardar.")
            st.exception(error)
