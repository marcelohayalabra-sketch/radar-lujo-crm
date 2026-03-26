import requests
import time
import pandas as pd

# ==============================
# CONFIGURACIÓN
# ==============================
API_TOKEN = "PEGA_AQUI_TU_TOKEN_REAL"
ACTOR_ID = "lukass~idealista-scraper"

# Puedes cambiar estos valores
DISTRICT = "Madrid"
MAX_ITEMS = 20
END_PAGE = 50

# ==============================
# FUNCIONES
# ==============================
def lanzar_actor():
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={API_TOKEN}"

    input_data = {
        "district": DISTRICT,
        "maxItems": MAX_ITEMS,
        "endPage": END_PAGE,
        "startUrl": [],
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        },
        "bedrooms": [],
        "bathrooms": [],
        "homeType": [],
        "condition": [],
        "propertyStatus": [],
        "floorHeights": [],
        "features": []
    }

    response = requests.post(url, json=input_data)
    response.raise_for_status()

    data = response.json()
    run_id = data["data"]["id"]
    print(f"Run lanzado correctamente. ID: {run_id}")
    return run_id


def esperar_resultado(run_id):
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={API_TOKEN}"

    while True:
        response = requests.get(status_url)
        response.raise_for_status()

        data = response.json()["data"]
        status = data["status"]
        print(f"Estado actual: {status}")

        if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            return data

        time.sleep(5)


def descargar_resultados(dataset_id):
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={API_TOKEN}"
    response = requests.get(dataset_url)
    response.raise_for_status()
    return response.json()


def guardar_excel(items, nombre_archivo="idealista_resultados.xlsx"):
    if not items:
        print("No hay resultados para guardar en Excel.")
        return

    df = pd.json_normalize(items)
    df.to_excel(nombre_archivo, index=False)
    print(f"Excel guardado correctamente: {nombre_archivo}")


def guardar_csv(items, nombre_archivo="idealista_resultados.csv"):
    if not items:
        print("No hay resultados para guardar en CSV.")
        return

    df = pd.json_normalize(items)
    df.to_csv(nombre_archivo, index=False, encoding="