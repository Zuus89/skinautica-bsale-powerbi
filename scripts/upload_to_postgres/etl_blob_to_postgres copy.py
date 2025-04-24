import os
import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from sqlalchemy import create_engine
import io

# Cargar variables de entorno
load_dotenv()

# Conexión Azure Blob
blob_service = BlobServiceClient.from_connection_string(os.getenv("AZURE_BLOB_CONN_STR"))
container_client = blob_service.get_container_client(os.getenv("BLOB_CONTAINER_NAME"))

# Conexión PostgreSQL
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}?sslmode=require"
)

# Lista de archivos que queremos cargar
archivos_a_cargar = {
    "document_details/document_details.csv",
    "documentos/documentos.csv",
}

# Procesar solo los archivos seleccionados
for blob in container_client.list_blobs():
    if blob.name in archivos_a_cargar:
        print(f"📥 Descargando: {blob.name}")
        blob_client = container_client.get_blob_client(blob.name)
        content = blob_client.download_blob().readall()
        df = pd.read_csv(io.BytesIO(content))

        table_name = os.path.splitext(os.path.basename(blob.name))[0].lower().replace("-", "_").replace(" ", "_")
        print(f"🛠️ Cargando en PostgreSQL: {table_name}")
        
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"✅ Tabla {table_name} cargada con éxito.\n")

print("🎉 Proceso completo.")
