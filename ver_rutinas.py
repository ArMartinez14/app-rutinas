def ver_rutinas():
    import streamlit as st
    import firebase_admin
    from firebase_admin import credentials, firestore
    from datetime import datetime, timedelta
    import json

    if not firebase_admin._apps:
        cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
        cred = credentials.Certificate(cred_dict)
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
        @media screen and (max-width: 768px) {
            .desktop-view { display: none !important; }
            .mobile-view { display: block !important; }
        }
        @media screen and (min-width: 769px) {
            .desktop-view { display: block !important; }
            .mobile-view { display: none !important; }
        }
        @media screen and (max-width: 768px) {
            .stButton>button {
                padding: 0.25rem 0.75rem !important;
                font-size: 12px !important;
            }
            .stMarkdown, .stTextInput, .stSelectbox, .stTextArea {
                font-size: 13px !important;
            }
            .block-container {
                padding: 0.5rem !important;
            }
            .compact-input input {
                width: 38px !important;
                font-size: 11px !important;
                padding: 2px !important;
            }
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
        @media screen and (max-width: 768px) {
            .desktop-view { display: none !important; }
            .mobile-view { display: block !important; }
        }
        @media screen and (min-width: 769px) {
            .desktop-view { display: block !important; }
            .mobile-view { display: none !important; }
        }
        @media screen and (max-width: 768px) {
            .stButton>button {
                padding: 0.25rem 0.75rem !important;
                font-size: 12px !important;
            }
            .stMarkdown, .stTextInput, .stSelectbox, .stTextArea {
                font-size: 13px !important;
            }
            .block-container {
                padding: 0.5rem !important;
            }
            .compact-input input {
                width: 38px !important;
                font-size: 11px !important;
                padding: 2px !important;
            }
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
        </style>
    """, unsafe_allow_html=True)

    logo_base64 = st.secrets["LOGO_BASE64"]
    st.markdown(f"<div style='text-align: center; margin-bottom: 1rem;'><img src='data:image/png;base64,{logo_base64.strip()}' style='max-height:45px;' /></div>", unsafe_allow_html=True)

    correo = st.text_input("\U0001F511 Ingresa tu correo:")

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
        cliente_input = st.text_input("\U0001F464 Escribe el nombre del cliente:", key="cliente")
        cliente_opciones = [c for c in clientes if cliente_input.lower() in c.lower()]
        cliente_sel = st.selectbox("O selecciona de la lista:", cliente_opciones if cliente_opciones else clientes)

        rutinas_cliente = [r for r in rutinas_list if r.get("cliente") == cliente_sel]
        semanas = sorted({r["fecha_lunes"] for r in rutinas_cliente}, reverse=True)

        semana_actual = obtener_fecha_lunes()
        semana_sel = st.selectbox("\U0001F4C6 Selecciona la semana", semanas, index=semanas.index(semana_actual) if semana_actual in semanas else 0, key="semana")

        rutinas = [r for r in rutinas_cliente if r["fecha_lunes"] == semana_sel]

        if not rutinas:
            st.warning("⚠️ No hay rutinas registradas para esta semana.")
            st.stop()

        dias = sorted(set(r["dia"] for r in rutinas), key=lambda x: int(x))
        dia_sel = st.selectbox("\U0001F4C5 Selecciona el día", dias, key="dia")

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
                st.markdown("<hr style='border: 0; height: 4px; background: #666; margin: 1.2rem 0 1.2rem 0;'>", unsafe_allow_html=True)
            prev_circuito = circuito

            col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 3, 1, 1, 1, 1], gap="small")
            col1.write("")
            col2.markdown(f"<div style='text-align:center'>{circuito}</div>", unsafe_allow_html=True)
            col3.markdown(f"<div style='text-align:center'>{e['ejercicio']}</div>", unsafe_allow_html=True)
            col4.markdown(f"<p style='font-size:16px; color:white;'><b>{e.get('series', '')}</b></p>", unsafe_allow_html=True)
            col5.markdown(f"<p style='font-size:16px; color:white;'><b>{e.get('repeticiones', '')}</b></p>", unsafe_allow_html=True)
            if peso_presente:
                col6.markdown(f"<p style='font-size:16px; color:white;'><b>{e.get('peso') if e.get('peso') else ''}</b></p>", unsafe_allow_html=True)
            else:
                col6.empty()

            if col7.button(f"Editar", key=f"editar_{idx}"):
                st.session_state.ejercicio_idx = idx

            if "ejercicio_idx" in st.session_state and st.session_state.ejercicio_idx == idx:

                num_series = e.get("series") or 0
                registro_series = e.get("registro_series", [{}]*num_series)

                header_cols = st.columns([0.6, 0.6, 0.6])
                header_cols[0].markdown("**Serie**")
                header_cols[1].markdown("**Reps**")
                header_cols[2].markdown("**Peso (kg)**")

                nuevas_series = []
                for i in range(num_series):
                    col1, col2, col3 = st.columns([0.6, 0.6, 0.6])
                    col1.markdown(f"<div style='text-align:center; vertical-align:middle'>{i + 1}</div>", unsafe_allow_html=True)
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

                correo_normalizado = e["correo"].replace("@", "_").replace(".", "_")
                fecha_normalizada = e["fecha_lunes"].replace("-", "_")
                doc_id = f"{correo_normalizado}_{fecha_normalizada}_{e['dia']}_{e['circuito']}_{e['ejercicio']}".lower().replace(" ", "_")
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
