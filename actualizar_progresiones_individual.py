from firebase_admin import firestore
from datetime import datetime, timedelta

def actualizar_progresiones_individual(nombre, correo, ejercicio, circuito, bloque, fecha_actual_lunes, dia_numero, peso_alcanzado):
    db = firestore.client()

    # Normalizar datos
    correo_id = correo.replace("@", "_").replace(".", "_").lower()
    nombre_id = nombre.lower().replace(" ", "_")
    ejercicio_id = ejercicio.lower().replace(" ", "_")
    circuito_id = circuito.lower().replace(" ", "_") if circuito else ""
    bloque_id = bloque.lower().replace(" ", "_")
    dia_id = str(dia_numero)

    # Fecha actual y siguiente semana
    fecha_lunes_dt = datetime.strptime(fecha_actual_lunes, "%Y-%m-%d")
    fecha_siguiente_lunes = fecha_lunes_dt + timedelta(weeks=1)
    fecha_normal = fecha_lunes_dt.strftime("%Y_%m_%d")
    fecha_siguiente_normal = fecha_siguiente_lunes.strftime("%Y_%m_%d")

    # ID del documento actual
    doc_id_actual = f"{correo_id}_{fecha_normal}_{dia_id}_{circuito_id}_{ejercicio_id}"
    doc_actual_ref = db.collection("rutinas").document(doc_id_actual)

    # Leer el documento actual
    doc_actual = doc_actual_ref.get()
    if not doc_actual.exists:
        print("No se encontró el documento de la semana actual.")
        return

    datos_actuales = doc_actual.to_dict()
    try:
        peso_planificado = float(datos_actuales.get("peso", 0))
        diferencia = round(peso_alcanzado - peso_planificado, 1)
    except:
        print("Error al leer el peso planificado.")
        return

    if diferencia == 0:
        print("No hay diferencia, no se actualiza.")
        return

    # ID del documento de la siguiente semana
    doc_id_siguiente = f"{correo_id}_{fecha_siguiente_normal}_{dia_id}_{circuito_id}_{ejercicio_id}"
    doc_siguiente_ref = db.collection("rutinas").document(doc_id_siguiente)

    doc_siguiente = doc_siguiente_ref.get()
    if not doc_siguiente.exists:
        print("No se encontró la semana siguiente, no se actualiza.")
        return

    datos_siguientes = doc_siguiente.to_dict()
    try:
        peso_original = float(datos_siguientes.get("peso", 0))
        nuevo_peso = round(peso_original + diferencia, 1)
        doc_siguiente_ref.update({"peso": nuevo_peso})
        print(f"Peso actualizado a {nuevo_peso} en semana siguiente.")
    except:
        print("No se pudo actualizar el peso en la semana siguiente.")
