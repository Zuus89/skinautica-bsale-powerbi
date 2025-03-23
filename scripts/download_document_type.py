import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Cargar token ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === Configuración API ===
BASE_URL = "https://api.bsale.cl/v1/document_types.json"

headers = {
    "access_token": ACCESS_TOKEN
}

# === Descargar los tipos de documentos ===
document_types = []

print(f"🔄 Descargando tipos de documentos...")

# Realizamos la solicitud GET a la API
response = requests.get(BASE_URL, headers=headers)

# Verificación de la respuesta
if response.status_code == 200:
    data = response.json()
    document_types = data.get("items", [])
    
    if document_types:
        print(f"✅ {len(document_types)} tipos de documentos encontrados.")
    else:
        print(f"⚠️ No se encontraron tipos de documentos.")
else:
    print(f"❌ Error al obtener tipos de documentos: {response.status_code} - {response.text}")

# === Guardar CSV ===
if document_types:
    output_dir = "data/document_types/"
    os.makedirs(output_dir, exist_ok=True)

    filename = "document_types.csv"
    filepath = os.path.join(output_dir, filename)

    # Crear un DataFrame con los tipos de documentos
    df = pd.DataFrame(document_types)

    # Guardar el DataFrame en un archivo CSV
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} tipos de documentos guardados en '{filepath}'")

    # Imprimir las primeras 5 filas del DataFrame
    print("\nPrimeras 5 filas del DataFrame:")
    print(df.head())  # Muestra las primeras 5 filas del DataFrame
else:
    print(f"⚠️ No se encontraron tipos de documentos.")
