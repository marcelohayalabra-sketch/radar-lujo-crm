import os
import time
from datetime import datetime
import scraper
import db

PRECIO_MINIMO = int(os.getenv("PRECIO_MINIMO", "1300000"))
INTERVAL_SECONDS = 15 * 60  # 15 minutos

def main():
    db.init_db()
    print("Runner iniciado. Escaneando cada 15 minutos...")

    while True:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando escaneo...")

            # 1. Ejecutar el scraper
            propiedades = scraper.obtener_datos_lujo(
                precio_min=PRECIO_MINIMO,
                limit=25
            )

            # 2. Guardar en radar_lujo.db usando db.py
            scan_id, resumen = db.run_scan(propiedades)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Escaneo OK.")
            print(f"  → Nuevas: {resumen['created']} | Actualizadas: {resumen['updated']} | Total: {resumen['total']}")
            print(f"  → Scan ID: {scan_id}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()