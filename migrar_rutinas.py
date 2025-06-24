import firebase_admin
from firebase_admin import credentials, firestore
import json

# === INICIALIZAR FIREBASE ===
if not firebase_admin._apps:
    # Usa tus credenciales desde archivo local o desde secrets
    with open("credenciales-firebase.json", "r") as f:
        cred_dict = json.load(f)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def normalizar_correo(correo):
    return correo.replace("@", "_").replace(".", "_")

def normalizar_fecha(fecha):
    return fecha.replace("-", "_")

def migrar_rutinas():
    print("🔄 Cargando documentos de 'rutinas'...")
    docs = db.collection("rutinas").stream()
    
    agrupadas = {}

    for doc in docs:
        data = doc.to_dict()
        correo = data.get("correo")
        fecha_lunes = data.get("fecha_lunes")
        dia = data.get("dia")
        
        if not all([correo, fecha_lunes, dia]):
            continue  # Saltar si faltan datos

        clave = f"{correo}_{fecha_lunes}"
        if clave not in agrupadas:
            agrupadas[clave] = {
                "correo": correo,
                "cliente": data.get("cliente", ""),
                "fecha_lunes": fecha_lunes,
                "rutina": {}
            }

        # Agregar al día correspondiente
        dia_str = str(dia)
        if dia_str not in agrupadas[clave]["rutina"]:
            agrupadas[clave]["rutina"][dia_str] = []

        # Remover campos innecesarios
        ejercicio = {k: v for k, v in data.items() if k not in ["correo", "cliente", "fecha_lunes", "dia"]}

        agrupadas[clave]["rutina"][dia_str].append(ejercicio)

    print(f"📦 Se agruparon {len(agrupadas)} documentos de rutina semanales.")

    for clave, data in agrupadas.items():
        correo_norm = normalizar_correo(data["correo"])
        fecha_norm = normalizar_fecha(data["fecha_lunes"])
        doc_id = f"{correo_norm}_{fecha_norm}"

        doc_ref = db.collection("rutinas_semanales").document(doc_id)
        if doc_ref.get().exists:
            print(f"⚠️ Ya existe: {doc_id} (omitido)")
            continue

        doc_ref.set(data)
        print(f"✅ Migrado: {doc_id}")

    print("🚀 Migración completada.")

# Ejecutar
migrar_rutinas()
