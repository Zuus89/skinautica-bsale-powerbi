import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import os

# === Cargar el token de acceso ===
load_dotenv(dotenv_path=".env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === Configuración de la API de pagos ===
BASE_URL = "https://api.bsale.io/v1/payments.json"

# Parámetros para la consulta (filtrar por rango de fechas)
params = {
    "limit": 50,                   # Limitar la cantidad de resultados por solicitud (ajustar según sea necesario)
    "offset": 0                    # Paginación (ajustar si hay más de 50 resultados)
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Descargar los pagos ===
payments_data = []
print(f"🔄 Descargando pagos...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)

    # Verificación de la respuesta de la API
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    payments = data.get("items", [])

    if not payments:
        break

    for payment in payments:
        payment_data = {
            "payment_id": payment.get("id"),
            "payment_date": payment.get("recordDate"),
            "amount": payment.get("amount"),
            "payment_method": payment.get("payment_type", {}).get("id"),
            "document_id": payment.get("document", {}).get("id"),
            "client_id": payment.get("user", {}).get("id"),
            "state": payment.get("state", {}),
        }
        payments_data.append(payment_data)

    # Paginación: actualizamos el offset para obtener más resultados si hay más pagos
    params["offset"] += params["limit"]

# === Guardar los pagos en un archivo CSV ===
if payments_data:
    output_dir = "data/pagos/"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"pagos.csv"
    filepath = os.path.join(output_dir, filename)

    df = pd.DataFrame(payments_data)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} pagos guardados en '{filepath}'")

    # Imprimir las primeras 5 filas para verificación
    print("\nPrimeras 5 filas de la tabla de pagos:")
    print(df.head())

else:
    print(f"⚠️ No se encontraron pagos para el rango de fechas especificado.")
