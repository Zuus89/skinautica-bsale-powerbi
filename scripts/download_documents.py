import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import time

# === Cargar token ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === Fecha objetivo ===
target_date = datetime(2025, 3, 17)  # Cambiar la fecha al 17 de marzo de 2025

# Convertir la fecha a timestamp UNIX (segundos desde 1970-01-01)
target_timestamp = int(time.mktime(target_date.timetuple()))

# === Configuración API ===
BASE_URL = "https://api.bsale.cl/v1/documents.json"

# Parámetros de la consulta con fechas en formato timestamp UNIX
params = {
    "emissiondate": target_timestamp,  # Fecha exacta en timestamp UNIX
    "expand": "details",  # Para expandir y obtener los detalles de cada documento
    "limit": 50,  # Limitar la cantidad de documentos obtenidos
    "offset": 0  # Paginación, ajusta si obtienes más de 50 documentos
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Download Documents ===
document_details = []
print(f"🔄 Downloading documents for {target_date.strftime('%d/%m/%Y')}...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    documents = data.get("items", [])
    
    if not documents:
        break

    for document in documents:
        # Extract basic information about the document
        document_data = {
            "document_id": document.get("id"),
            "emission_date": document.get("emissionDate"),
            "total_amount": document.get("totalAmount"),
            "net_amount": document.get("netAmount"),
            "tax_amount": document.get("taxAmount"),
            "address": document.get("address"),
            "municipality": document.get("municipality"),
            "city": document.get("city"),
            "state": document.get("state"),
            "number": document.get("number"),
            "client_id": document.get("client", {}).get("id"),
            "document_type_id": document.get("document_type", {}).get("id"),
            "user_id": document.get("user", {}).get("id"),
            "details_url": document.get("details", {}).get("href")  # Extract href for details
        }
        document_details.append(document_data)

    # Update the offset to fetch the next set of documents
    params["offset"] += params["limit"]

# === Save Data to CSV ===
if document_details:
    output_dir = "data/documentos/"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"documentos_2025-03-17.csv"
    filepath = os.path.join(output_dir, filename)

    df = pd.DataFrame(document_details)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} document records saved to '{filepath}'")

    # Print the first 5 rows for verification
    print("\nFirst 5 rows of the documents data:")
    print(df.head())
else:
    print(f"⚠️ No documents found for {target_date.strftime('%d/%m/%Y')}.")