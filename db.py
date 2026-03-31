import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional

DB_PATH = "radar_lujo.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS listings (
                id TEXT PRIMARY KEY,
                enlace TEXT,
                direccion TEXT,
                zona TEXT,
                m2 INTEGER,
                habitaciones INTEGER,
                intermediario TEXT,
                estado TEXT,
                planta TEXT,
                first_seen TEXT,
                last_seen TEXT,
                last_price REAL,
                last_scan_id TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT,
                scan_time TEXT,
                listing_id TEXT,
                enlace TEXT,
                direccion TEXT,
                zona TEXT,
                m2 INTEGER,
                habitaciones INTEGER,
                intermediario TEXT,
                estado TEXT,
                planta TEXT,
                precio REAL
            )
            """
        )

        cur.execute("CREATE INDEX IF NOT EXISTS idx_history_listing_id ON history(listing_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_history_scan_id ON history(scan_id)")

        conn.commit()


def run_scan(listings: List[Dict]) -> Tuple[str, Dict[str, int]]:
    scan_time = datetime.now().isoformat(timespec="seconds")
    scan_id = f"scan_{scan_time.replace(':','').replace('-','').replace('T','_')}"

    created = 0
    updated = 0

    with _conn() as conn:
        cur = conn.cursor()

        for item in listings:
            listing_id = str(item.get("id"))
            enlace = item.get("enlace", "")
            direccion = item.get("direccion", "")
            zona = item.get("zona", "")
            precio = float(item.get("precio", 0) or 0)
            m2 = int(item.get("m2", 0) or 0)
            habitaciones = int(item.get("habitaciones", 0) or 0)
            intermediario = item.get("intermediario", "N/A")
            estado = item.get("estado", "N/A")
            planta = item.get("planta", "N/A")

            cur.execute("SELECT id FROM listings WHERE id = ?", (listing_id,))
            exists = cur.fetchone()

            if not exists:
                created += 1
                cur.execute(
                    """
                    INSERT INTO listings (
                        id, enlace, direccion, zona, m2, habitaciones,
                        intermediario, estado, planta,
                        first_seen, last_seen, last_price, last_scan_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        listing_id, enlace, direccion, zona, m2, habitaciones,
                        intermediario, estado, planta,
                        scan_time, scan_time, precio, scan_id
                    )
                )
            else:
                updated += 1
                cur.execute(
                    """
                    UPDATE listings
                    SET enlace=?, direccion=?, zona=?, m2=?, habitaciones=?,
                        intermediario=?, estado=?, planta=?,
                        last_seen=?, last_price=?, last_scan_id=?
                    WHERE id=?
                    """,
                    (
                        enlace, direccion, zona, m2, habitaciones,
                        intermediario, estado, planta,
                        scan_time, precio, scan_id, listing_id
                    )
                )

            cur.execute(
                """
                INSERT INTO history (
                    scan_id, scan_time,
                    listing_id, enlace, direccion, zona, m2, habitaciones,
                    intermediario, estado, planta, precio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id, scan_time,
                    listing_id, enlace, direccion, zona, m2, habitaciones,
                    intermediario, estado, planta, precio
                )
            )

        conn.commit()

    return scan_id, {"created": created, "updated": updated, "total": len(listings)}


def get_changes_for_scan(scan_id: str) -> Dict[str, List[Dict]]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT scan_time FROM history WHERE scan_id = ? LIMIT 1", (scan_id,))
        row = cur.fetchone()
        if not row:
            return {"nuevos": [], "bajadas": [], "estancados": []}

        scan_time = row["scan_time"]

        cur.execute(
            """
            SELECT *
            FROM listings
            WHERE first_seen = ?
            ORDER BY last_price DESC
            """,
            (scan_time,)
        )
        nuevos = [dict(r) for r in cur.fetchall()]

        cur.execute(
            """
            SELECT listing_id, precio, zona, direccion, enlace, scan_time
            FROM history
            WHERE scan_id = ?
            """,
            (scan_id,)
        )
        current_rows = cur.fetchall()

        bajadas: List[Dict] = []
        for r in current_rows:
            listing_id = r["listing_id"]
            precio_actual = float(r["precio"])

            cur.execute(
                """
                SELECT precio
                FROM history
                WHERE listing_id = ?
                  AND scan_time < ?
                ORDER BY scan_time DESC
                LIMIT 1
                """,
                (listing_id, scan_time)
            )
            prev = cur.fetchone()
            if not prev:
                continue

            precio_anterior = float(prev["precio"])
            if precio_actual < precio_anterior:
                bajadas.append(
                    {
                        "id": listing_id,
                        "zona": r["zona"],
                        "direccion": r["direccion"],
                        "enlace": r["enlace"],
                        "precio_anterior": precio_anterior,
                        "precio_actual": precio_actual,
                        "bajada_abs": precio_anterior - precio_actual,
                        "bajada_pct": ((precio_anterior - precio_actual) / precio_anterior * 100.0) if precio_anterior > 0 else 0.0,
                    }
                )

        bajadas.sort(key=lambda x: x["bajada_abs"], reverse=True)

        cur.execute(
            """
            SELECT id, zona, direccion, enlace, first_seen, last_seen, last_price
            FROM listings
            """
        )
        estancados: List[Dict] = []
        for r in cur.fetchall():
            first_seen = r["first_seen"]
            if not first_seen:
                continue
            try:
                dt_first = datetime.fromisoformat(first_seen)
                days = (datetime.now() - dt_first).days
            except Exception:
                continue

            estancados.append(
                {
                    "id": r["id"],
                    "zona": r["zona"],
                    "direccion": r["direccion"],
                    "enlace": r["enlace"],
                    "first_seen": r["first_seen"],
                    "last_seen": r["last_seen"],
                    "last_price": float(r["last_price"] or 0),
                    "days_on_market": int(days),
                }
            )

        estancados.sort(key=lambda x: x["days_on_market"], reverse=True)

        return {"nuevos": nuevos, "bajadas": bajadas, "estancados": estancados}


def get_latest_listings(limit: int = 500) -> List[Dict]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM listings
            ORDER BY last_seen DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(r) for r in cur.fetchall()]


# ============================================================
# SCORING (CONFIGURABLE)
# ============================================================
def _median(values: List[float]) -> Optional[float]:
    if not values:
        return None
    values = sorted(values)
    n = len(values)
    mid = n // 2
    if n % 2 == 1:
        return float(values[mid])
    return float((values[mid - 1] + values[mid]) / 2.0)


def get_zone_median_price_per_m2() -> Dict[str, float]:
    listings = get_latest_listings(limit=5000)
    zone_values: Dict[str, List[float]] = {}

    for it in listings:
        zona = it.get("zona", "N/A")
        price = float(it.get("last_price") or 0)
        m2 = int(it.get("m2") or 0)
        if zona and price > 0 and m2 > 0:
            zone_values.setdefault(zona, []).append(price / m2)

    medians: Dict[str, float] = {}
    for zona, vals in zone_values.items():
        m = _median(vals)
        if m is not None:
            medians[zona] = float(m)

    return medians


def get_previous_price(listing_id: str, before_scan_time: str) -> Optional[float]:
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT precio
            FROM history
            WHERE listing_id = ?
              AND scan_time < ?
            ORDER BY scan_time DESC
            LIMIT 1
            """,
            (listing_id, before_scan_time)
        )
        r = cur.fetchone()
        if not r:
            return None
        return float(r["precio"])


def compute_score_for_listing(listing: Dict, zone_medians: Dict[str, float], rules: Dict) -> Dict:
    """
    rules esperadas:
      umbral_verde, umbral_amarillo
      bonus_particular
      dias_1, dias_2, dias_3 + puntos_dias_1/2/3
      drop_1, drop_2, drop_3 + puntos_drop_1/2/3
      ratio_1, ratio_2, ratio_3 + puntos_ratio_1/2/3
    """
    score = 0

    zona = listing.get("zona", "N/A")
    price = float(listing.get("last_price") or 0)
    m2 = int(listing.get("m2") or 0)
    intermediario = (listing.get("intermediario") or "N/A").lower()
    first_seen = listing.get("first_seen")
    last_seen = listing.get("last_seen")

    # 1) Particular
    if "particular" in intermediario:
        score += int(rules["bonus_particular"])

    # 2) Días en mercado
    days_on_market = 0
    if first_seen:
        try:
            dt_first = datetime.fromisoformat(first_seen)
            days_on_market = (datetime.now() - dt_first).days
        except Exception:
            days_on_market = 0

    if days_on_market >= int(rules["dias_3"]):
        score += int(rules["puntos_dias_3"])
    elif days_on_market >= int(rules["dias_2"]):
        score += int(rules["puntos_dias_2"])
    elif days_on_market >= int(rules["dias_1"]):
        score += int(rules["puntos_dias_1"])

    # 3) Bajada de precio reciente
    price_drop_pct = 0.0
    if last_seen:
        prev_price = get_previous_price(listing["id"], last_seen)
        if prev_price and prev_price > 0 and price > 0 and price < prev_price:
            drop_pct = (prev_price - price) / prev_price * 100.0
            price_drop_pct = drop_pct

            if drop_pct >= float(rules["drop_3"]):
                score += int(rules["puntos_drop_3"])
            elif drop_pct >= float(rules["drop_2"]):
                score += int(rules["puntos_drop_2"])
            elif drop_pct >= float(rules["drop_1"]):
                score += int(rules["puntos_drop_1"])

    # 4) Precio/m² vs mediana zona
    ppm2 = 0.0
    ratio = None
    if price > 0 and m2 > 0:
        ppm2 = price / m2
        med = zone_medians.get(zona)
        if med and med > 0:
            ratio = ppm2 / med  # <1 es “más barato que mediana”
            if ratio <= float(rules["ratio_3"]):
                score += int(rules["puntos_ratio_3"])
            elif ratio <= float(rules["ratio_2"]):
                score += int(rules["puntos_ratio_2"])
            elif ratio <= float(rules["ratio_1"]):
                score += int(rules["puntos_ratio_1"])

    score = max(0, min(100, score))

    # Semáforo según umbrales configurables
    if score >= int(rules["umbral_verde"]):
        semaforo = "🟢 Oportunidad"
    elif score >= int(rules["umbral_amarillo"]):
        semaforo = "🟡 Vigilar"
    else:
        semaforo = "🔴 Normal"

    out = dict(listing)
    out["score"] = score
    out["semaforo"] = semaforo
    out["days_on_market"] = int(days_on_market)
    out["precio_m2"] = float(ppm2)
    out["bajada_pct_reciente"] = float(price_drop_pct)
    out["ratio_vs_mediana_zona"] = float(ratio) if ratio is not None else 0.0
    return out


def get_scored_inventory(limit: int, rules: Dict) -> List[Dict]:
    zone_medians = get_zone_median_price_per_m2()
    base = get_latest_listings(limit=limit)
    scored = [compute_score_for_listing(it, zone_medians, rules) for it in base]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def make_call_list(scored: List[Dict]) -> List[Dict]:
    """
    Devuelve una tabla “limpia” para llamar/captar.
    """
    out: List[Dict] = []
    for x in scored:
        out.append({
            "Semáforo": x.get("semaforo"),
            "Score": x.get("score"),
            "Zona": x.get("zona"),
            "Precio (€)": int(float(x.get("last_price") or 0)),
            "m²": int(x.get("m2") or 0),
            "€/m²": int(float(x.get("precio_m2") or 0)),
            "Bajada %": round(float(x.get("bajada_pct_reciente") or 0), 2),
            "Días": int(x.get("days_on_market") or 0),
            "Intermediario": x.get("intermediario"),
            "Dirección": x.get("direccion"),
            "Enlace": x.get("enlace"),
        })
    return out
