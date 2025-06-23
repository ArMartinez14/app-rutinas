def actualizar_progresiones_individual(nombre, correo, ejercicio, circuito, bloque, fecha_actual_lunes, dia_numero, peso_alcanzado):
    from firebase_admin import firestore
    from datetime import datetime, timedelta

    db = firestore.client()

    # Normalización de texto
    correo_id = correo.replace("@", "_").replace(".", "_").lower()
    ejercicio_id = ejercicio.lower().replace(" ", "_")
    circuito_id = circuito.lower().replace(" ", "_") if circuito else ""
    bloque_id = bloque.lower().replace(" ", "_")
    dia_id = str(dia_numero)

    fecha_dt = datetime.strptime(fecha_actual_lunes, "%Y-%m-%d")
    fecha_normal = fecha_dt.strftime("%Y_%m_%d")
    fecha_siguiente = (fecha_dt + timedelta(weeks=1)).strftime("%Y_%m_%d")

    # Documento actual y siguiente
    doc_id_actual = f"{correo_id}_{fecha_normal}_{dia_id}_{circuito_id}_{ejercicio_id}"
    doc_id_siguiente = f"{correo_id}_{fecha_siguiente}_{dia_id}_{circuito_id}_{ejercicio_id}"

    doc_actual = db.collection("rutinas").document(doc_id_actual).get()
    if not doc_actual.exists:
        print("No se encontró documento actual.")
        return

    try:
        peso_planificado = float(doc_actual.to_dict().get("peso", 0))
        diferencia = round(peso_alcanzado - peso_planificado, 1)
    except:
        print("Error leyendo peso planificado.")
        return

    if diferencia == 0:
        return

    doc_siguiente_ref = db.collection("rutinas").document(doc_id_siguiente)
    doc_siguiente = doc_siguiente_ref.get()
    if not doc_siguiente.exists:
        print("Semana siguiente no existe.")
        return

    try:
        datos = doc_siguiente.to_dict()
        peso_original = float(datos.get("peso", 0))
        nuevo_peso = round(peso_original + diferencia, 1)
        doc_siguiente_ref.update({"peso": nuevo_peso})
        print(f"✅ Semana siguiente actualizada a {nuevo_peso} kg")
    except:
        print("Error actualizando semana siguiente.")