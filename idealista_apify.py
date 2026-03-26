import requests
import time
import pandas as pd
import os

# ==============================
# CONFIGURACIÓN
# ==============================
API_TOKEN = os.getenv("API_TOKEN")  # 🔐 Seguro para Streamlit
ACTOR_ID = "lukass~idealista-scraper"

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
    return run_id


def esperar_resultado(run_id):
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={API_TOKEN}"

    while True:
        response = requests.get(status_url)
        response.raise_for_status()

        data = response.json()["data"]
        status = data["status"]

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
        return None

    df = pd.json_normalize(items)
    df.to_excel(nombre_archivo, index=False)
    return nombre_archivo


def guardar_csv(items, nombre_archivo="idealista_resultados.csv"):
    if not items:
        return None

    df = pd.json_normalize(items)
    df.to_csv(nombre_archivo, index=False, encoding="utf-8")
    return nombre_archivo


# ==============================
# FUNCIÓN PRINCIPAL
# ==============================
def obtener_datos():
    run_id = lanzar_actor()
    resultado = esperar_resultado(run_id)

    if resultado["status"] != "SUCCEEDED":
        return None

    dataset_id = resultado["defaultDatasetId"]
    items = descargar_resultados(dataset_id)

    return items
