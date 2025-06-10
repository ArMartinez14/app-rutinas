def ver_rutinas():
    import streamlit as st
    import firebase_admin
    from firebase_admin import credentials, firestore
    from datetime import datetime, timedelta
    import json
    import os
    import re

    if not firebase_admin._apps:
        cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
        with open("/tmp/firebase.json", "w") as f:
            json.dump(cred_dict, f)
        cred = credentials.Certificate("/tmp/firebase.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    def obtener_fecha_lunes():
        hoy = datetime.now()
        lunes = hoy - timedelta(days=hoy.weekday())
        return lunes.strftime("%Y-%m-%d")

    def es_entrenador(rol):
        return rol.lower() in ["entrenador", "admin", "administrador"]

    def ordenar_circuito(ejercicio):
        orden = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
        return orden.get(ejercicio.get("circuito", ""), 99)

    st.markdown("""
        <style>
        .stMarkdown, .stTextInput, .stSelectbox, .stTextArea {
            font-size: 13px !important;
        }
        .compact-input input {
            width: 30px !important;
            font-size: 11px !important;
            padding: 2px !important;
        }
        .tabla-rutina td, .tabla-rutina th {
            padding: 4px 8px;
            border: 1px solid #444;
        }
        .tabla-rutina tr:nth-child(even) {
            background-color: #1a1a1a;
        }
        .tabla-sep {
            height: 8px;
        }
        .tabla-rutina .dato {
            font-size: 15px !important;
            color: white !important;
        }
        .tabla-rutina .dato span.none {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    correo = st.text_input("🔑 Ingresa tu correo:")
    if not correo:
        st.stop()

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
    cliente_input = st.text_input("👤 Escribe el nombre del cliente:")
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

    ejercicios = [r for r in rutinas if r["dia"] == dia_sel]

    if ejercicios:
        semana_ciclo = ejercicios[0].get("semana_ciclo", "")
        if semana_ciclo:
            st.markdown(f"### {semana_ciclo}")

    ejercicios.sort(key=ordenar_circuito)

    st.markdown("### Tabla de ejercicios")
    peso_presente = any(e.get("peso") for e in ejercicios)

    secciones_vistas = set()
    prev_circuito = None

    for idx, e in enumerate(ejercicios):
        circuito = e.get("circuito", "Z").upper()
        seccion = "Warm-up" if circuito in ["A", "B", "C"] else "Workout"

        if seccion not in secciones_vistas:
            st.markdown(f"#### {seccion}")
            secciones_vistas.add(seccion)

        if prev_circuito and prev_circuito != circuito:
            st.markdown("<hr style='border: 0; height: 4px; background: #666; margin: 1.2rem 0;'>", unsafe_allow_html=True)
        prev_circuito = circuito

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 3, 1, 1, 1, 1], gap="small")
        col1.write("")
        col2.markdown(f"<div style='text-align:center'>{circuito}</div>", unsafe_allow_html=True)
        col3.markdown(f"<div style='text-align:center'>{e['ejercicio']}</div>", unsafe_allow_html=True)
        col4.markdown(f"<p style='font-size:16px; color:white; text-align:center'><b>{e.get('series', '')}</b></p>", unsafe_allow_html=True)
        col5.markdown(f"<p style='font-size:16px; color:white; text-align:center'><b>{e.get('repeticiones', '')}</b></p>", unsafe_allow_html=True)
        col6.markdown(f"<p style='font-size:16px; color:white; text-align:center'><b>{e.get('peso') if e.get('peso') else ''}</b></p>", unsafe_allow_html=True)

        ejercicio_key = re.sub(r'\W+', '_', e['ejercicio'].lower())

        if col7.button(f"Editar", key=f"editar_{ejercicio_key}_{idx}"):
            st.session_state.ejercicio_idx = idx

        if st.session_state.get("ejercicio_idx") == idx:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("Peso Alcanzado", unsafe_allow_html=True)
                st.markdown("<div class='compact-input'>", unsafe_allow_html=True)
                peso_alcanzado = st.text_input(
                    label="Peso Alcanzado",
                    value=e.get("peso_alcanzado", ""),
                    key=f"peso_alcanzado_{ejercicio_key}_{idx}",
                    label_visibility="collapsed"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("RIR", unsafe_allow_html=True)
                st.markdown("<div class='compact-input'>", unsafe_allow_html=True)
                rir = st.text_input(
                    label="RIR",
                    value=e.get("rir", ""),
                    key=f"rir_{ejercicio_key}_{idx}",
                    label_visibility="collapsed"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            comentario_input = st.text_input(
                "Comentario",
                value=e.get("comentario", ""),
                key=f"coment_{ejercicio_key}_{idx}"
            )

            if e.get("video"):
                st.video(e["video"])

            correo_normalizado = e["correo"].replace("@", "_").replace(".", "_")
            fecha_normalizada = e["fecha_lunes"].replace("-", "_")
            doc_id = f"{correo_normalizado}_{fecha_normalizada}_{e['dia']}_{e['circuito']}_{e['ejercicio']}".lower().replace(
                " ", "_")
            doc_ref = db.collection("rutinas").document(doc_id)

            if st.button(f"💾 Guardar cambios - {e['ejercicio']}", key=f"guardar_{ejercicio_key}_{idx}"):
                try:
                    # Guardar campos actualizados en el documento actual
                    doc_ref.update({
                        "peso_alcanzado": peso_alcanzado,
                        "rir": rir,
                        "comentario": comentario_input
                    })
                    st.success("✅ Registro actualizado exitosamente.")

                    # Ejecutar función de actualización de progresión solo si hay dato
                    if peso_alcanzado not in [None, ""]:
                        actualizar_progresiones_individual(
                            nombre=e["cliente"],
                            correo=e["correo"],
                            ejercicio=e["ejercicio"],
                            circuito=e.get("circuito", ""),  # puede venir como 'D'
                            bloque=e.get("bloque", e.get("seccion", "")),  # puede venir como 'Work Out'
                            fecha_actual_lunes=e["fecha_lunes"],  # formato correcto 'YYYY-MM-DD'
                            dia_numero=int(e["dia"]),  # está como string tipo "2"
                            peso_alcanzado=float(peso_alcanzado)
                        )
                        st.info("📈 Peso actualizado en semana siguiente.")

                except Exception as error:
                    st.error("❌ No se pudo guardar. Es posible que el documento no exista con ese ID.")
                    st.exception(error)
