from dotenv import load_dotenv
import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from azure.storage.blob import BlobServiceClient

# === Cargar variables de entorno desde .env ===
load_dotenv(dotenv_path=".env")

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
BSALE_ACCESS_TOKEN = os.environ["BSALE_ACCESS_TOKEN"]
AZURE_BLOB_CONN_STR = os.environ["AZURE_BLOB_CONN_STR"]
BLOB_CONTAINER = os.environ["BLOB_CONTAINER_NAME"]

# === Inicializar conexiones ===
pg_engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"
)
blob_service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONN_STR)
container_client = blob_service.get_container_client(BLOB_CONTAINER)

# === Obtener última fecha desde la tabla documentos ===
print("🔍 Obteniendo última fecha de documentos...")
with pg_engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(emission_date) FROM documentos"))
    last_saved_datetime = result.scalar()

if last_saved_datetime is None:
    last_saved_datetime = datetime.now(timezone.utc) - timedelta(days=90)
else:
    last_saved_datetime = pd.to_datetime(last_saved_datetime, unit="s").normalize() + timedelta(days=1)

# Usamos UTC para evitar problemas de zona horaria
yesterday = datetime.datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
start_ts = int(last_saved_datetime.timestamp())
end_ts = int(yesterday.timestamp())

print(f"🗕️ Descargando documentos desde {start_ts} hasta {end_ts}...")

# === Configuración de API Bsale ===
BASE_URL = "https://api.bsale.cl/v1/documents.json"
params = {
    "emissiondaterange": f"[{start_ts},{end_ts}]",
    "expand": "details",
    "limit": 50,
    "offset": 0
}
headers = { "access_token": BSALE_ACCESS_TOKEN }

documentos = []
while True:
    res = requests.get(BASE_URL, headers=headers, params=params)
    if res.status_code != 200:
        print(f"❌ Error en API: {res.status_code} - {res.text}")
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
    print("⚠️ No se encontraron nuevos documentos.")
    exit()

df_docs = pd.DataFrame(documentos)

# === Guardar documentos en Blob ===
doc_blob_name = f"documentos/documentos_{start_ts}_to_{end_ts}.csv"
blob_client = container_client.get_blob_client(doc_blob_name)
blob_client.upload_blob(df_docs.to_csv(index=False), overwrite=True)
print(f"📄 Documentos guardados en Blob: {doc_blob_name}")

# === Insertar documentos en PostgreSQL ===
df_docs["emission_date"] = df_docs["emission_date"].astype("int64")
df_docs.to_sql("documentos", pg_engine, if_exists="append", index=False)
print(f"✅ Documentos insertados en PostgreSQL: {len(df_docs)}")

# === Descargar detalles de cada documento ===
print("🔍 Descargando detalles de documentos...")
detalles = []

for row in df_docs.itertuples():
    if row.details_url:
        dres = requests.get(row.details_url, headers=headers)
        if dres.status_code == 200:
            for item in dres.json().get("items", []):
                detalles.append({
                    "document_id": row.document_id,
                    "line_number": item.get("lineNumber"),
                    "quantity": item.get("quantity"),
                    "net_unit_value": item.get("netUnitValue"),
                    "total_unit_value": item.get("totalUnitValue"),
                    "net_amount": item.get("netAmount"),
                    "tax_amount": item.get("taxAmount"),
                    "total_amount": item.get("totalAmount"),
                    "variant_id": item.get("variant", {}).get("id"),
                    "related_detail_id": item.get("relatedDetailId")
                })

if not detalles:
    print("⚠️ No se encontraron detalles.")
    exit()

df_detalles = pd.DataFrame(detalles)

# === Guardar detalles en Blob ===
details_blob_name = f"document_details/document_details_{start_ts}_to_{end_ts}.csv"
container_client.get_blob_client(details_blob_name).upload_blob(df_detalles.to_csv(index=False), overwrite=True)
print(f"📄 Detalles guardados en Blob: {details_blob_name}")

# === Insertar detalles en PostgreSQL ===
df_detalles.to_sql("document_details", pg_engine, if_exists="append", index=False)
print(f"✅ Detalles insertados en PostgreSQL: {len(df_detalles)}")

print("🌟 Proceso completo.")

