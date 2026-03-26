import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# ============================================================
# CONFIG ZONAS / SIMULACIÓN (TEMPORAL)
# ============================================================
ZONAS = ["Aravaca", "Pozuelo", "Majadahonda", "El Viso"]

# Esto simula “ID estable” para anuncios (cuando tengas API será el id real)
BASE_IDS = {
    "Aravaca": 100000,
    "Pozuelo": 200000,
    "Majadahonda": 300000,
    "El Viso": 400000,
}


def _fake_address(zona: str) -> str:
    calles = ["Calle", "Avenida", "Paseo", "Plaza"]
    nombres = ["Príncipe", "Castellana", "Velázquez", "Serrano", "Aravaca", "Europa", "Rosales", "Acacias"]
    return f"{random.choice(calles)} {random.choice(nombres)} {random.randint(1, 199)}, {zona}"


def _fake_intermediario() -> str:
    # Aproximación: en lujo suele haber agencia, pero dejamos % de particular
    return "Particular" if random.random() < 0.18 else "Agencia"


def _fake_estado() -> str:
    return random.choice(["Buen estado", "Reformado", "Segunda mano", "Obra nueva", "N/A"])


def _fake_planta() -> str:
    return random.choice(["N/A", "Planta baja", "Planta 1ª", "Planta 2ª", "Ático"])


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ============================================================
# API “UNIFICADA” (TU APP SOLO LLAMA A ESTO)
# ============================================================
def fetch_listings(precio_min: int = 1200000, limit: int = 15, zonas: Optional[List[str]] = None) -> List[Dict]:
    """
    Devuelve una lista de anuncios NORMALIZADOS.
    Hoy devuelve datos simulados.
    Cuando llegue la API de Idealista, esta función se reemplaza por llamadas reales,
    pero el resto del sistema no cambia.

    Campos mínimos recomendados:
      id (str), enlace (str), direccion (str), zona (str),
      precio (float), m2 (int), habitaciones (int),
      intermediario ('Particular'/'Agencia'), estado (str), planta (str),
      fetched_at (str ISO)
    """
    zonas = zonas or ZONAS

    results: List[Dict] = []
    fetched_at = _now_iso()

    # Simulamos un “mercado” con anuncios que se repiten entre escaneos y a veces bajan
    # Para que puedas probar: “bajadas” y “antigüedad”
    for zona in zonas:
        base = BASE_IDS.get(zona, 900000)
        for i in range(limit // max(1, len(zonas)) + 2):
            ad_num = base + i
            precio = random.randint(precio_min, precio_min + 2500000)

            # Simula bajadas de precio aleatorias
            if random.random() < 0.25:
                precio = int(precio * random.uniform(0.90, 0.98))

            m2 = random.randint(120, 650)
            hab = random.randint(3, 7)

            results.append({
                "id": str(ad_num),
                "enlace": f"https://example.com/inmueble/{ad_num}",
                "direccion": _fake_address(zona),
                "zona": zona,
                "precio": float(precio),
                "m2": int(m2),
                "habitaciones": int(hab),
                "intermediario": _fake_intermediario(),
                "estado": _fake_estado(),
                "planta": _fake_planta(),
                "fetched_at": fetched_at,
            })

    # Orden por precio desc (solo para que sea “bonito” en UI)
    results.sort(key=lambda x: x["precio"], reverse=True)

    return results[:limit]


if __name__ == "__main__":
    # Prueba rápida
    data = fetch_listings(precio_min=1300000, limit=10)
    for d in data:
        print(d["zona"], d["precio"], d["intermediario"], d["direccion"], d["enlace"])
