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

def main(UpdatePaymentTimer: func.TimerRequest) -> None:
    logging.info("⏰ Ejecutando función UpdateDocuments")

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
        result = conn.execute(text("SELECT MAX(emission_date) FROM documentos"))
        last_payment_timestamp = result.scalar()

    if last_payment_timestamp is None:
        last_saved_datetime = datetime.now(timezone.utc) - timedelta(days=90)
    else:
        last_saved_datetime = pd.to_datetime(last_payment_timestamp, unit="s").normalize() + timedelta(days=1)

    start_ts = int(last_saved_datetime.timestamp())
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_ts = int(today.timestamp())

    if start_ts >= yesterday_ts:
        logging.info("⏳ No hay nuevos documentos para procesar.")
        return

    BASE_URL = "https://api.bsale.cl/v1/documents.json"
    params = {
        "emissiondaterange": f"[{start_ts},{yesterday_ts}]",
        "expand": "details",
        "limit": 50,
        "offset": 0
    }
    headers = { "access_token": ACCESS_TOKEN }

    documentos = []
    logging.info(f"🔄 Descargando documentos desde {start_ts} hasta {yesterday_ts}...")

    while True:
        res = requests.get(BASE_URL, headers=headers, params=params)
        if res.status_code != 200:
            logging.error(f"❌ Error en API: {res.status_code} - {res.text}")
            break

        items = res.json().get("items", [])
        if not items:
            break

        for doc in items:
            doc_data = {
                "document_id": doc.get("id"),
                "emission_date": doc.get("emissionDate"),
                "total_amount": doc.get("totalAmount"),
                "net_amount": doc.get("netAmount"),
                "tax_amount": doc.get("taxAmount"),
                "address": doc.get("address"),
                "municipality": doc.get("municipality"),
                "city": doc.get("city"),
                "state": doc.get("state"),
                "number": doc.get("number"),
                "client_id": doc.get("client", {}).get("id"),
                "document_type_id": doc.get("document_type", {}).get("id"),
                "user_id": doc.get("user", {}).get("id"),
                "details_url": doc.get("details", {}).get("href"),
                "seller_url": doc.get("sellers", {}).get("href")
            }

            if doc_data["seller_url"]:
                sres = requests.get(doc_data["seller_url"], headers=headers)
                if sres.status_code == 200:
                    sitems = sres.json().get("items", [])
                    doc_data["seller_id"] = sitems[0]["id"] if sitems else None
                else:
                    doc_data["seller_id"] = None

            documentos.append(doc_data)

        params["offset"] += params["limit"]

    if not documentos:
        logging.info("⚠️ No se encontraron nuevos documentos.")
        return

    df_docs = pd.DataFrame(documentos)
    df_docs["emission_date"] = df_docs["emission_date"].astype("int64")

    doc_blob_name = f"documentos/documentos_{start_ts}_to_{yesterday_ts}.csv"
    blob_client = container_client.get_blob_client(doc_blob_name)
    blob_client.upload_blob(df_docs.to_csv(index=False), overwrite=True)
    logging.info(f"📄 Documentos guardados en Blob: {doc_blob_name}")

    df_docs.to_sql("documentos", pg_engine, if_exists="append", index=False)
    logging.info(f"✅ {len(df_docs)} documentos insertados en PostgreSQL")
