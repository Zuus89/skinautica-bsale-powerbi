import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Cargar el token de acceso ===
load_dotenv(dotenv_path=".env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === Configuración de la API de Tipos de Pago ===
BASE_URL = "https://api.bsale.io/v1/payment_types.json"

# Parámetros de la consulta (sin filtros para obtener todos los tipos de pago)
params = {
    "limit": 50,  # Limitar la cantidad de resultados por solicitud (ajustar según sea necesario)
    "offset": 0    # Paginación (ajustar si hay más de 50 resultados)
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Descargar los Tipos de Pago ===
payment_methods_data = []
print(f"🔄 Downloading payment methods...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)

    # Verificación de la respuesta de la API
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    payment_methods = data.get("items", [])

    if not payment_methods:
        break

    for payment_method in payment_methods:
        payment_method_data = {
            "payment_type_id": payment_method.get("id"),
            "name": payment_method.get("name"),
            "is_creditnote": payment_method.get("isCreditNote"),
            "isClientCredit": payment_method.get("isClientCredit"),
            "isCash": payment_method.get("isCash"),
            "state": payment_method.get("state"),
        }
        payment_methods_data.append(payment_method_data)

    # Paginación: actualizamos el offset para obtener más resultados si hay más tipos de pago
    params["offset"] += params["limit"]

# === Guardar los Tipos de Pago en un archivo CSV ===
if payment_methods_data:
    output_dir = "data/tipos_de_pago/"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"tipos_de_pago.csv"
    filepath = os.path.join(output_dir, filename)

    df = pd.DataFrame(payment_methods_data)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} payment methods saved to '{filepath}'")

    # Imprimir las primeras 5 filas para verificación
    print("\nFirst 5 rows of the payment methods data:")
    print(df.head())

else:
    print(f"⚠️ No payment methods found.")
