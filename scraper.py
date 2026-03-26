from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import random
import re
import time
from typing import Dict, List, Optional, Tuple


# ============================================================
# CONFIG
# ============================================================
DEBUG = os.getenv("DEBUG_SCRAPER", "0") == "1"   # DEBUG_SCRAPER=1 guarda screenshot+html
HEADLESS = os.getenv("HEADLESS", "1") == "1"     # HEADLESS=0 para ver el navegador

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]


# ============================================================
# HELPERS
# ============================================================
def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def _extract_int(text: str) -> Optional[int]:
    """Extrae entero de '1.350.000 €' o '180 m²'."""
    if not text:
        return None
    m = re.search(r"(\d[\d\.]*)", text)
    if not m:
        return None
    try:
        return int(m.group(1).replace(".", ""))
    except Exception:
        return None

def _extract_m2_and_rooms(features_text: str) -> Tuple[Optional[int], Optional[int]]:
    m2 = None
    rooms = None

    m = re.search(r"(\d[\d\.]*)\s*m²", features_text or "", flags=re.IGNORECASE)
    if m:
        try:
            m2 = int(m.group(1).replace(".", ""))
        except Exception:
            m2 = None

    m = re.search(r"(\d+)\s*(hab\.|habitaciones?)", features_text or "", flags=re.IGNORECASE)
    if m:
        try:
            rooms = int(m.group(1))
        except Exception:
            rooms = None

    return m2, rooms

def _extract_floor(features_text: str) -> str:
    if not features_text:
        return "N/A"
    t = (features_text or "").lower()

    patterns = [
        r"planta\s+([0-9]{1,2}ª?)",
        r"planta\s+(baja)",
        r"planta\s+(principal)",
        r"(entreplanta)",
        r"(ático)",
        r"(sótano)",
    ]
    for pat in patterns:
        m = re.search(pat, t, flags=re.IGNORECASE)
        if m:
            return _clean_text(m.group(0)).capitalize()

    return "N/A"

def _extract_state(features_text: str) -> str:
    if not features_text:
        return "N/A"
    t = (features_text or "").lower()

    if "obra nueva" in t or "nuevo desarrollo" in t:
        return "Obra nueva"
    if "a estrenar" in t:
        return "A estrenar"
    if "reformado" in t or "reforma integral" in t:
        return "Reformado"
    if "buen estado" in t:
        return "Buen estado"
    if "segunda mano" in t:
        return "Segunda mano"

    return "N/A"

def _guess_intermediary(advertiser_text: str, advertiser_block: str = "") -> str:
    t = (advertiser_text or "").lower()
    b = (advertiser_block or "").lower()

    if "particular" in t or "particular" in b:
        return "Particular"
    if "profesional" in t or "inmobiliaria" in t or "agencia" in t:
        return "Agencia"
    if "profesional" in b or "inmobiliaria" in b or "agencia" in b:
        return "Agencia"

    return "N/A"

def _polite_sleep(min_s=1.2, max_s=3.2):
    time.sleep(random.uniform(min_s, max_s))

def _block_heavy_resources(route):
    req = route.request
    if req.resource_type in ("image", "font", "media"):
        return route.abort()
    return route.continue_()

def _safe_text(page, selectors: List[str], timeout_ms: int = 4000) -> str:
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() == 0:
                continue
            loc.wait_for(state="visible", timeout=timeout_ms)
            txt = _clean_text(loc.inner_text(timeout=timeout_ms))
            if txt:
                return txt
        except Exception:
            continue
    return ""

def _save_debug(page, prefix: str):
    """Guarda screenshot + HTML para entender qué carga Idealista."""
    try:
        png = f"{prefix}.png"
        html = f"{prefix}.html"
        page.screenshot(path=png, full_page=True)
        with open(html, "w", encoding="utf-8") as f:
            f.write(page.content())
        try:
            title = page.title()
        except Exception:
            title = "N/A"
        print(f"DEBUG guardado: {png} {html}")
        print(f"TITLE: {title}")
        print(f"URL real: {page.url}")
    except Exception as e:
        print(f"No pude guardar DEBUG: {e}")

def _force_debug(page, prefix: str):
    """Guarda debug aunque DEBUG esté apagado (para diagnóstico)."""
    _save_debug(page, prefix)


# ============================================================
# SCRAPER
# ============================================================
def obtener_datos_lujo(precio_min: int = 1300000, limit: int = 15) -> List[Dict]:
    """
    Radar Idealista (Madrid) por ZONAS con precio mínimo.
    Devuelve lista de dicts con:
      id, enlace, direccion, planta, m2, habitaciones, precio, telefono, intermediario, estado, tipo, zona
    """
    propiedades: List[Dict] = []

    zonas_url = {
        "Aravaca": f"https://www.idealista.com/venta-viviendas/madrid/moncloa/aravaca/con-precio-min_{precio_min}/ordenar-por_publicado-desc/",
        "Pozuelo": f"https://www.idealista.com/venta-viviendas/pozuelo-de-alarcon-madrid/con-precio-min_{precio_min}/ordenar-por_publicado-desc/",
        "Majadahonda": f"https://www.idealista.com/venta-viviendas/majadahonda-madrid/con-precio-min_{precio_min}/ordenar-por_publicado-desc/",
        "El Viso": f"https://www.idealista.com/venta-viviendas/madrid/chamartin/el-viso/con-precio-min_{precio_min}/ordenar-por_publicado-desc/",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)

        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            locale="es-ES",
            viewport={"width": 1366, "height": 768},
        )

        context.route("**/*", _block_heavy_resources)

        page = context.new_page()
        page.set_default_timeout(20000)

        detail = context.new_page()
        detail.set_default_timeout(20000)

        try:
            for zona, url_base in zonas_url.items():
                if len(propiedades) >= int(limit):
                    break

                print(f"\n=== ZONA: {zona} ===")
                print(f"URL: {url_base}")

                try:
                    page.goto(url_base, wait_until="load", timeout=60000)
                    page.wait_for_timeout(1500)

                    # Cookies (intento robusto)
                    cookie_selectors = [
                        "#didomi-notice-agree-button",
                        "button#didomi-notice-agree-button",
                        "button:has-text('Aceptar')",
                        "button:has-text('Estoy de acuerdo')",
                        "button:has-text('Aceptar y continuar')",
                    ]
                    for sel in cookie_selectors:
                        try:
                            btn = page.locator(sel).first
                            if btn.count() > 0:
                                btn.click(timeout=2500)
                                page.wait_for_timeout(700)
                                break
                        except Exception:
                            pass

                    page.wait_for_selector("body", timeout=15000)

                    # Para diagnosticar redirecciones (bloqueos/captcha)
                    try:
                        print("TITLE:", page.title())
                    except Exception:
                        print("TITLE: (no disponible)")
                    print("URL REAL:", page.url)

                    # Selectores de cards (más robustos)
                    possible_items = [
                        "article.item",
                        "article[data-adid]",
                        ".item[data-adid]",
                        "div.item",
                        "article",  # fallback
                    ]

                    anuncios_locator = None
                    for sel in possible_items:
                        try:
                            loc = page.locator(sel)
                            # no esperamos por selector aquí; a veces existe pero tarda
                            if loc.count() > 0:
                                anuncios_locator = loc
                                break
                        except Exception:
                            continue

                    # Si no pillamos nada, intentamos un wait específico para el selector más probable
                    if anuncios_locator is None or anuncios_locator.count() == 0:
                        try:
                            page.wait_for_selector("article.item, article[data-adid], .item[data-adid]", timeout=12000)
                            anuncios_locator = page.locator("article.item, article[data-adid], .item[data-adid]")
                        except Exception:
                            anuncios_locator = None

                    if anuncios_locator is None or anuncios_locator.count() == 0:
                        print(f"[{zona}] No se encontraron anuncios (posible bloqueo / captcha / HTML distinto).")
                        # Guardamos debug SIEMPRE para que tú lo abras y lo veamos
                        _force_debug(page, f"debug_listado_{zona.replace(' ', '_')}")
                        continue

                    remaining = int(limit) - len(propiedades)
                    total = min(anuncios_locator.count(), remaining)
                    print(f"[{zona}] Cards detectadas: {anuncios_locator.count()} | Voy a procesar: {total}")

                    for i in range(total):
                        try:
                            card = anuncios_locator.nth(i)

                            # ID anuncio
                            ad_id = ""
                            for attr in ("data-adid", "data-adId"):
                                try:
                                    ad_id = card.get_attribute(attr) or ""
                                    if ad_id:
                                        break
                                except Exception:
                                    pass

                            # Link anuncio
                            href = ""
                            link_selectors = [
                                "a.item-link",
                                ".item-link",
                                "a[href*='/inmueble/']",
                                "a[href*='/venta-viviendas/']",
                                "a[href^='/inmueble/']",
                            ]
                            for link_sel in link_selectors:
                                try:
                                    a = card.locator(link_sel).first
                                    if a.count() > 0:
                                        href = a.get_attribute("href") or ""
                                        if href:
                                            break
                                except Exception:
                                    continue

                            if not href:
                                continue

                            enlace = "https://www.idealista.com" + href if href.startswith("/") else href

                            # Precio tarjeta
                            precio_txt = ""
                            price_selectors = [
                                ".item-price",
                                "span.item-price",
                                ".price",
                                "[class*='price']",
                            ]
                            for ps in price_selectors:
                                try:
                                    p_loc = card.locator(ps).first
                                    if p_loc.count() > 0:
                                        precio_txt = _clean_text(p_loc.inner_text())
                                        if precio_txt:
                                            break
                                except Exception:
                                    continue

                            precio_val = _extract_int(precio_txt)
                            if precio_val is None:
                                continue

                            # DETALLE
                            try:
                                detail.goto(enlace, wait_until="load", timeout=60000)
                            except PlaywrightTimeoutError:
                                _polite_sleep(2.0, 4.0)
                                detail.goto(enlace, wait_until="load", timeout=60000)

                            detail.wait_for_timeout(1200)

                            direccion = _safe_text(detail, [
                                ".main-info__title-main",
                                ".main-info__title",
                                "h1",
                                "[class*='main-info'] h1",
                            ])

                            features_text = ""
                            try:
                                lis = detail.locator(
                                    ".details-property-feature-one li, "
                                    ".details-property_features li, "
                                    ".details-property-feature-one"
                                )
                                if lis.count() > 0:
                                    parts = []
                                    for k in range(min(lis.count(), 70)):
                                        t = _clean_text(lis.nth(k).inner_text())
                                        if t and len(t) >= 2:
                                            parts.append(t)
                                    features_text = " | ".join(parts[:40])
                            except Exception:
                                pass

                            if not features_text:
                                try:
                                    features_text = detail.inner_text("main", timeout=2500)
                                except Exception:
                                    features_text = ""

                            m2, hab = _extract_m2_and_rooms(features_text)
                            planta = _extract_floor(features_text)
                            estado = _extract_state(features_text)

                            advertiser_text = _safe_text(detail, [
                                ".advertiser-name",
                                ".advertiser-data__name",
                                ".professional-name",
                                "[class*='advertiser'] [class*='name']",
                            ], timeout_ms=3000)

                            advertiser_block = _safe_text(detail, [
                                ".advertiser-data",
                                ".advertiser-info",
                                "[class*='advertiser']",
                            ], timeout_ms=3000)

                            intermediario = _guess_intermediary(advertiser_text, advertiser_block)

                            telefono = "Ver en web"

                            info = {
                                "id": ad_id or enlace,
                                "enlace": enlace,
                                "direccion": direccion or "N/A",
                                "tipo": "Vivienda",
                                "planta": planta,
                                "m2": int(m2 or 0),
                                "habitaciones": int(hab or 0),
                                "precio": float(precio_val),
                                "telefono": telefono,
                                "intermediario": intermediario,
                                "estado": estado,
                                "zona": zona,
                            }

                            propiedades.append(info)
                            _polite_sleep(1.4, 3.4)

                        except Exception as e:
                            print(f"[{zona}] Error en anuncio index={i}: {e}")
                            if DEBUG:
                                _save_debug(page, f"debug_error_listado_{zona}_{i}")
                                _save_debug(detail, f"debug_error_detalle_{zona}_{i}")
                            _polite_sleep(1.0, 2.0)
                            continue

                except Exception as e:
                    print(f"[{zona}] Error general zona: {e}")
                    _force_debug(page, f"debug_error_general_{zona.replace(' ', '_')}")
                    continue

        finally:
            try:
                detail.close()
            except Exception:
                pass
            try:
                context.close()
            except Exception:
                pass
            browser.close()

    return propiedades


if __name__ == "__main__":
    datos = obtener_datos_lujo(precio_min=1300000, limit=10)
    for d in datos:
        print(d["zona"], d["precio"], d["direccion"], d["enlace"])



