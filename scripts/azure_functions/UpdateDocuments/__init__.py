import logging
import os
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from azure.storage.blob import BlobServiceClient
import azure.functions as func
from dotenv import load_dotenv

load_dotenv(".env")

def main(UpdateDocumentTimer: func.TimerRequest) -> None:
    logging.info("⏰ Ejecutando función UpdatePayments")

    ACCESS_TOKEN = os.environ["BSALE_ACCESS_TOKEN"]
    AZURE_BLOB_CONN_STR = os.environ["AZURE_BLOB_CONN_STR"]
    BLOB_CONTAINER = os.environ["BLOB_CONTAINER_NAME"]
    POSTGRES_HOST = os.environ["POSTGRES_HOST"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

    pg_engine = create_engine(
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"
    )
    blob_service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONN_STR)
    container_client = blob_service.get_container_client(BLOB_CONTAINER)

    with pg_engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(payment_date) FROM pagos"))
        last_payment_timestamp = result.scalar()

    if last_payment_timestamp is None:
        last_saved_datetime = datetime.now(timezone.utc) - timedelta(days=90)
    else:
        last_saved_datetime = pd.to_datetime(last_payment_timestamp, unit="s").normalize() + timedelta(days=1)

    start_ts = int(last_saved_datetime.timestamp())
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_ts = int(today.timestamp())

    if start_ts >= yesterday_ts:
        logging.info("⚠️ No hay nuevos pagos para procesar.")
        return

    BASE_URL = "https://api.bsale.cl/v1/payments.json"
    params = {
        "recorddaterange": f"[{start_ts},{yesterday_ts}]",
        "limit": 50,
        "offset": 0
    }
    headers = {"access_token": ACCESS_TOKEN}

    pagos = []
    logging.info(f"🔄 Descargando pagos desde {start_ts} hasta {yesterday_ts}...")

    while True:
        res = requests.get(BASE_URL, headers=headers, params=params)
        if res.status_code != 200:
            logging.error(f"❌ Error en API: {res.status_code} - {res.text}")
            break

        items = res.json().get("items", [])
        if not items:
            break

        for pay in items:
            pagos.append({
                "payment_id": pay.get("id"),
                "payment_date": pay.get("recordDate"),
                "amount": pay.get("amount"),
                "payment_method": pay.get("payment_type", {}).get("id"),
                "document_id": pay.get("document", {}).get("id"),
                "client_id": pay.get("user", {}).get("id"),
                "state": pay.get("state", {})
            })

        params["offset"] += params["limit"]

    if not pagos:
        logging.info("⚠️ No se encontraron pagos.")
        return

    df = pd.DataFrame(pagos)
    df["payment_date"] = df["payment_date"].astype("int64")

    blob_path = f"pagos/payments_{start_ts}_to_{yesterday_ts}.csv"
    blob_client = container_client.get_blob_client(blob_path)
    blob_client.upload_blob(df.to_csv(index=False), overwrite=True)
    logging.info(f"📄 Pagos guardados en Blob Storage: {blob_path}")

    df.to_sql("pagos", pg_engine, if_exists="append", index=False)
    logging.info(f"✅ {len(df)} pagos insertados en la base de datos.")
