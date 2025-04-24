import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from collections import defaultdict

# Cargar credenciales
load_dotenv(dotenv_path=".env")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/graphql.json"

headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# Template de consulta paginada con filtro por fecha
def build_query(cursor=None):
    cursor_clause = f', after: "{cursor}"' if cursor else ""
    return f"""
    {{
      orders(first: 100{cursor_clause}, query: "created_at:>=2023-01-01") {{
        pageInfo {{
          hasNextPage
          endCursor
        }}
        edges {{
          node {{
            createdAt
            cancelReason
            test
            currentTotalPriceSet {{
              shopMoney {{
                amount
                currencyCode
              }}
            }}
          }}
        }}
      }}
    }}
    """

# Inicializar estructuras
ventas_por_dia = defaultdict(float)
ordenes_por_dia = defaultdict(int)

# Obtener todas las órdenes con paginación
has_next_page = True
cursor = None
total_ordenes = 0

while has_next_page:
    query = build_query(cursor)
    response = requests.post(url, headers=headers, json={"query": query})
    res_data = response.json()

    if "errors" in res_data:
        print("❌ Error en consulta GraphQL:")
        print(json.dumps(res_data, indent=2))
        break

    orders_data = res_data["data"]["orders"]
    for order in orders_data["edges"]:
        nodo = order["node"]

        if nodo["test"] or nodo["cancelReason"] is not None:
            continue

        monto_venta = float(nodo["currentTotalPriceSet"]["shopMoney"]["amount"])
        if monto_venta == 0:
            continue

        created_utc = datetime.fromisoformat(nodo["createdAt"].replace("Z", "")).replace(tzinfo=ZoneInfo("UTC"))
        created_cl = created_utc.astimezone(ZoneInfo("America/Santiago"))
        fecha_solo = created_cl.date()

        ventas_por_dia[fecha_solo] += monto_venta
        ordenes_por_dia[fecha_solo] += 1
        total_ordenes += 1

    # Avanzar a la siguiente página
    has_next_page = orders_data["pageInfo"]["hasNextPage"]
    cursor = orders_data["pageInfo"]["endCursor"]

print(f"\n📦 Total de órdenes procesadas: {total_ordenes}")

# Crear DataFrame
data = [
    {
        "Fecha (CL)": fecha,
        "Total Ventas ($)": round(ventas_por_dia[fecha], 2),
        "Cantidad de Órdenes": ordenes_por_dia[fecha]
    }
    for fecha in sorted(ventas_por_dia)
]

df = pd.DataFrame(data)

print("\n📊 Ventas reales por día (desde 2023-01-01):")
print(df)

# Crear carpeta data/shopify_sales si no existe
output_dir = os.path.join("data", "shopify_sales")
os.makedirs(output_dir, exist_ok=True)

# Guardar CSV
csv_path = os.path.join(output_dir, "ventas_shopify.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print(f"\n✅ CSV guardado en: {csv_path}")
