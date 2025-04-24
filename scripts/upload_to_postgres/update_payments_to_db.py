import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

# === Cargar variables de entorno ===
load_dotenv(dotenv_path=".env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")
AZURE_BLOB_CONN_STR = os.getenv("AZURE_BLOB_CONN_STR")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER_NAME")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# === Inicializar conexiones ===
engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"
)
blob_service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONN_STR)
container_client = blob_service.get_container_client(BLOB_CONTAINER)

# === Obtener la fecha máxima de payment_date en la base ===
with engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(payment_date) FROM pagos"))
    last_payment_timestamp = result.scalar()

if last_payment_timestamp is None:
    last_saved_datetime = datetime.now(timezone.utc) - timedelta(days=90)
else:
    last_saved_datetime = pd.to_datetime(last_payment_timestamp, unit="s").normalize() + timedelta(days=1)

start_ts = int(last_saved_datetime.timestamp())

# Calcular el timestamp de ayer (UTC a las 00:00)
today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
yesterday_ts = int(today.timestamp())

# === Validar rango de fechas ===
if start_ts >= yesterday_ts:
    print("⚠️ No hay nuevos pagos para descargar: el rango de fechas es inválido.")
    exit()

# === Configuración API ===
BASE_URL = "https://api.bsale.cl/v1/payments.json"
params = {
    "recorddaterange": f"[{start_ts},{yesterday_ts}]",
    "limit": 50,
    "offset": 0
}
headers = {"access_token": ACCESS_TOKEN}

# === Descarga de pagos ===
payments_data = []
print(f"🔄 Descargando pagos desde {start_ts} hasta {yesterday_ts}...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    items = response.json().get("items", [])
    if not items:
        break

    for payment in items:
        payments_data.append({
            "payment_id": payment.get("id"),
            "payment_date": payment.get("recordDate"),
            "amount": payment.get("amount"),
            "payment_method": payment.get("payment_type", {}).get("id"),
            "document_id": payment.get("document", {}).get("id"),
            "client_id": payment.get("user", {}).get("id"),
            "state": payment.get("state", {})
        })

    params["offset"] += params["limit"]

# === Guardar CSV en Blob y PostgreSQL ===
if payments_data:
    df = pd.DataFrame(payments_data)
    df["payment_date"] = df["payment_date"].astype("int64")

    # Guardar CSV en Blob
    blob_path = f"pagos/payments_{start_ts}_to_{yesterday_ts}.csv"
    container_client.get_blob_client(blob_path).upload_blob(df.to_csv(index=False), overwrite=True)
    print(f"📄 Pagos guardados en Blob Storage: {blob_path}")

    # Insertar en PostgreSQL
    df.to_sql("pagos", engine, if_exists="append", index=False)
    print(f"✅ {len(df)} pagos insertados en la base de datos.")
else:
    print("⚠️ No se encontraron pagos en el rango especificado.")
