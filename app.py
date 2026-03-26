import re
import sqlite3
import math
from datetime import datetime, timedelta, date
from typing import Optional

import pandas as pd
import streamlit as st

import idealista_apify
import db as radar_db

DB_PATH = "radar_lujo.db"
st.set_page_config(page_title="InmoLuxury · CRM Privado", layout="wide", page_icon="💎")

# =========================
# Estilos de lujo
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Montserrat:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #FAF8F4;
}

/* Ocultar elementos por defecto de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Topbar */
.topbar {
    background: #1C1C1C;
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 58px;
    border-bottom: 1px solid #C9A84C;
    margin: -1rem -1rem 2rem -1rem;
}
.logo {
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #C9A84C;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.logo span { color: #fff; }
.welcome {
    font-family: 'Cormorant Garamond', serif;
    font-size: 16px;
    color: #C9A84C;
    font-style: italic;
    letter-spacing: 1px;
}
.topbar-right {
    font-size: 11px;
    color: #666;
    letter-spacing: 1px;
}

/* Fondo general */
.stApp { background-color: #FAF8F4; }
.block-container { padding-top: 0 !important; background-color: #FAF8F4; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #fff;
    border-bottom: 1px solid #E8E2D6;
    gap: 0;
    padding: 0 8px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #999;
    padding: 14px 20px;
    border-bottom: 2px solid transparent;
    background: transparent;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    color: #1C1C1C !important;
    border-bottom: 2px solid #C9A84C !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* Sección título */
.section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #C9A84C;
    margin-bottom: 16px;
    font-weight: 500;
}

/* Tarjetas de stats */
.stat-card {
    background: #fff;
    border: 1px solid #E8E2D6;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: left;
}
.stat-label {
    font-size: 10px;
    color: #999;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-weight: 500;
}
.stat-value {
    font-size: 28px;
    font-weight: 400;
    color: #1C1C1C;
    font-family: 'Cormorant Garamond', serif;
}
.stat-value.gold { color: #C9A84C; }
.stat-sub { font-size: 11px; color: #bbb; margin-top: 4px; }

/* Tarjetas de propiedades */
.prop-card {
    background: #fff;
    border: 1px solid #E8E2D6;
    border-radius: 0 10px 10px 0;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}
.prop-card.verde  { border-left: 3px solid #4CAF84; }
.prop-card.amarillo { border-left: 3px solid #C9A84C; }
.prop-card.rojo   { border-left: 3px solid #E06060; }

.prop-dir {
    font-size: 14px;
    font-weight: 500;
    color: #1C1C1C;
    margin-bottom: 4px;
    font-family: 'Montserrat', sans-serif;
}
.prop-meta { font-size: 12px; color: #999; }
.prop-precio {
    font-size: 17px;
    font-weight: 400;
    color: #1C1C1C;
    font-family: 'Cormorant Garamond', serif;
    text-align: right;
}
.prop-score {
    display: inline-block;
    background: #FAF8F4;
    border: 1px solid #E8E2D6;
    border-radius: 4px;
    font-size: 10px;
    color: #888;
    padding: 2px 8px;
    margin-top: 4px;
    letter-spacing: 0.5px;
    font-family: 'Montserrat', sans-serif;
}
.badge-particular {
    display: inline-block;
    background: #F0F9F4;
    color: #3A8A5F;
    font-size: 9px;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #C2E0CF;
    margin-left: 8px;
    font-family: 'Montserrat', sans-serif;
}
.badge-agencia {
    display: inline-block;
    background: #F5F0E8;
    color: #8A6A2A;
    font-size: 9px;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #DDD0B0;
    margin-left: 8px;
    font-family: 'Montserrat', sans-serif;
}

/* Card genérica */
.card {
    background: #fff;
    border: 1px solid #E8E2D6;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.sem-box {
    height: 3px;
    border-radius: 2px;
    margin-top: 10px;
}
.muted { opacity: 0.6; font-size: 0.88rem; }
.small { font-size: 0.9rem; }
.hr { height: 1px; background: #E8E2D6; margin: 10px 0; }

/* Botones */
.stButton > button {
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border-radius: 6px;
    font-weight: 500;
}
.stButton > button[kind="primary"] {
    background: #1C1C1C !important;
    color: #C9A84C !important;
    border: 1px solid #C9A84C !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 6px !important;
    border-color: #E8E2D6 !important;
    background: #fff !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 13px !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    color: #888 !important;
}

/* Divider */
hr { border-color: #E8E2D6 !important; }

/* Success / error */
.stSuccess { border-left: 3px solid #4CAF84 !important; }
.stError   { border-left: 3px solid #E06060 !important; }
</style>
""", unsafe_allow_html=True)

# Topbar
st.markdown("""
<div class="topbar">
  <div class="logo"><span>Inmo</span>Luxury · <span style="color:#fff;letter-spacing:1px;font-size:12px;">Madrid</span></div>
  <div class="welcome">Bienvenido, Señor Marcelo</div>
  <div class="topbar-right">Radar Lujo · CRM Privado</div>
</div>
""", unsafe_allow_html=True)


# =========================
# Utils
# =========================
def safe_int(x, default=0) -> int:
    if x is None:
        return default
    try:
        if isinstance(x, float) and math.isnan(x):
            return default
    except Exception:
        pass
    if isinstance(x, str):
        s = x.strip().lower()
        if s in ("", "nan", "none", "null", "-"):
            return default
        s = s.replace(".", "").replace(",", "")
        try:
            return int(float(s))
        except Exception:
            return default
    try:
        return int(x)
    except Exception:
        try:
            return int(float(x))
        except Exception:
            return default


def safe_str(x, default="") -> str:
    if x is None:
        return default
    s = str(x)
    if s.lower() == "nan":
        return default
    return s.strip()


def sem_color(semaforo: str) -> str:
    return {"VERDE": "#4CAF84", "AMARILLO": "#C9A84C", "ROJO": "#E06060"}.get(semaforo, "#C9A84C")


def sem_emoji(semaforo: str) -> str:
    return {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}.get(semaforo, "🟡")


def extract_idealista_id(url: str) -> Optional[str]:
    if not url:
        return None
    m = re.search(r"/inmueble/(\d+)", url)
    return m.group(1) if m else None


# =========================
# DB
# =========================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS particulares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        idealista_url TEXT, idealista_id TEXT,
        zona TEXT, direccion TEXT, tipo_vivienda TEXT,
        m2_construidos INTEGER, m2_parcela INTEGER,
        nombre TEXT, telefono TEXT, comentarios TEXT,
        use_manual_semaforo INTEGER NOT NULL DEFAULT 1,
        semaforo_manual TEXT NOT NULL DEFAULT 'AMARILLO'
    );""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        idealista_url TEXT, idealista_id TEXT,
        zona TEXT, direccion TEXT, tipo_vivienda TEXT,
        m2_construidos INTEGER, m2_parcela INTEGER,
        agencia_nombre TEXT, notas TEXT,
        semaforo_manual TEXT NOT NULL DEFAULT 'AMARILLO'
    );""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        fecha TEXT NOT NULL, hora TEXT, titulo TEXT NOT NULL,
        detalle TEXT, categoria TEXT,
        relacionado_tipo TEXT, relacionado_id INTEGER
    );""")
    conn.commit()
    conn.close()


def df_query(sql: str, params=()):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def execute(sql: str, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()


def insert_particular(data: dict):
    now = datetime.utcnow().isoformat()
    execute("""
        INSERT INTO particulares (
            created_at, updated_at, idealista_url, idealista_id,
            zona, direccion, tipo_vivienda, m2_construidos, m2_parcela,
            nombre, telefono, comentarios, use_manual_semaforo, semaforo_manual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, now, data.get("idealista_url"), data.get("idealista_id"),
          data.get("zona"), data.get("direccion"), data.get("tipo_vivienda"),
          data.get("m2_construidos"), data.get("m2_parcela"),
          data.get("nombre"), data.get("telefono"), data.get("comentarios"),
          int(data.get("use_manual_semaforo", 1)), data.get("semaforo_manual", "AMARILLO")))


def update_particular(pid: int, semaforo_manual: str, comentarios: str):
    now = datetime.utcnow().isoformat()
    execute("UPDATE particulares SET updated_at=?, semaforo_manual=?, comentarios=? WHERE id=?",
            (now, semaforo_manual, comentarios, pid))


def insert_agencia(data: dict):
    now = datetime.utcnow().isoformat()
    execute("""
        INSERT INTO agencia (
            created_at, updated_at, idealista_url, idealista_id,
            zona, direccion, tipo_vivienda, m2_construidos, m2_parcela,
            agencia_nombre, notas, semaforo_manual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, now, data.get("idealista_url"), data.get("idealista_id"),
          data.get("zona"), data.get("direccion"), data.get("tipo_vivienda"),
          data.get("m2_construidos"), data.get("m2_parcela"),
          data.get("agencia_nombre"), data.get("notas"),
          data.get("semaforo_manual", "AMARILLO")))


def update_agencia(aid: int, semaforo_manual: str, notas: str):
    now = datetime.utcnow().isoformat()
    execute("UPDATE agencia SET updated_at=?, semaforo_manual=?, notas=? WHERE id=?",
            (now, semaforo_manual, notas, aid))


def insert_agenda(item: dict):
    now = datetime.utcnow().isoformat()
    execute("""
        INSERT INTO agenda (
            created_at, updated_at, fecha, hora, titulo, detalle,
            categoria, relacionado_tipo, relacionado_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, now, item.get("fecha"), item.get("hora"), item.get("titulo"),
          item.get("detalle"), item.get("categoria"),
          item.get("relacionado_tipo"), item.get("relacionado_id")))


def delete_agenda(agenda_id: int):
    execute("DELETE FROM agenda WHERE id=?", (agenda_id,))


# =========================
# Init
# =========================
init_db()
radar_db.init_db()

SCORING_RULES = {
    "umbral_verde": 50, "umbral_amarillo": 25,
    "bonus_particular": 30,
    "dias_1": 7,  "puntos_dias_1": 5,
    "dias_2": 30, "puntos_dias_2": 15,
    "dias_3": 60, "puntos_dias_3": 25,
    "drop_1": 2,  "puntos_drop_1": 10,
    "drop_2": 5,  "puntos_drop_2": 20,
    "drop_3": 10, "puntos_drop_3": 30,
    "ratio_1": 0.95, "puntos_ratio_1": 10,
    "ratio_2": 0.85, "puntos_ratio_2": 20,
    "ratio_3": 0.75, "puntos_ratio_3": 30,
}

# =========================
# Tabs
# =========================
tabs = st.tabs(["💎 RADAR", "👤 PARTICULARES", "🏢 AGENCIA", "📅 AGENDA"])


# =========================
# TAB 0: RADAR
# =========================
with tabs[0]:

    scored = radar_db.get_scored_inventory(limit=200, rules=SCORING_RULES)
    total = len(scored)
    particulares = sum(1 for x in scored if "particular" in safe_str(x.get("intermediario")).lower())
    oportunidades = sum(1 for x in scored if "🟢" in safe_str(x.get("semaforo")))
    bajadas = sum(1 for x in scored if float(x.get("bajada_pct_reciente") or 0) > 0)

    st.markdown('<div class="section-title">Resumen del inventario</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Total propiedades</div>
            <div class="stat-value gold">{total}</div>
            <div class="stat-sub">en radar</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Particulares</div>
            <div class="stat-value">{particulares}</div>
            <div class="stat-sub">sin agencia</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Bajadas de precio</div>
            <div class="stat-value">{bajadas}</div>
            <div class="stat-sub">detectadas</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Oportunidades</div>
            <div class="stat-value gold">{oportunidades}</div>
            <div class="stat-sub">score alto</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        precio_min = st.number_input("Precio mínimo (€)", min_value=500000, max_value=10000000,
                                     value=1300000, step=100000)
    with col2:
        limit = st.number_input("Nº máx. propiedades", min_value=5, max_value=50, value=15, step=5)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        lanzar = st.button("💎 Lanzar Radar", use_container_width=True, type="primary")

    if lanzar:
        with st.spinner("Escaneando Idealista... un momento, Señor Marcelo ⏳"):
            try:
                propiedades = scraper.obtener_datos_lujo(precio_min=int(precio_min), limit=int(limit))
                scan_id, resumen = radar_db.run_scan(propiedades)
                st.success(f"✅ Escaneo completado · {resumen['created']} nuevas · {resumen['updated']} actualizadas · {resumen['total']} total")
                cambios = radar_db.get_changes_for_scan(scan_id)

                if cambios["nuevos"]:
                    st.markdown('<div class="section-title" style="margin-top:24px">Propiedades nuevas detectadas</div>', unsafe_allow_html=True)
                    for p in cambios["nuevos"]:
                        intermediario = safe_str(p.get("intermediario"), "N/A")
                        es_part = "particular" in intermediario.lower()
                        badge = '<span class="badge-particular">Particular</span>' if es_part else '<span class="badge-agencia">Agencia</span>'
                        clase = "verde" if es_part else "amarillo"
                        st.markdown(f"""
                        <div class="prop-card {clase}">
                          <div style="flex:1">
                            <div class="prop-dir">{safe_str(p.get("zona"))} {badge}</div>
                            <div class="prop-meta">{safe_str(p.get("direccion","N/A"))} · {safe_int(p.get("m2"))} m² · {safe_int(p.get("habitaciones"))} hab</div>
                          </div>
                          <div style="text-align:right">
                            <div class="prop-precio">{int(float(p.get("last_price",0))):,} €</div>
                            <a href="{safe_str(p.get("enlace"))}" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver →</a>
                          </div>
                        </div>""", unsafe_allow_html=True)

                if cambios["bajadas"]:
                    st.markdown('<div class="section-title" style="margin-top:24px">Bajadas de precio</div>', unsafe_allow_html=True)
                    for b in cambios["bajadas"]:
                        st.markdown(f"""
                        <div class="prop-card amarillo">
                          <div style="flex:1">
                            <div class="prop-dir">{safe_str(b.get("zona"))} <span class="badge-agencia">Bajada {b['bajada_pct']:.1f}%</span></div>
                            <div class="prop-meta">{safe_str(b.get("direccion","N/A"))}</div>
                          </div>
                          <div style="text-align:right">
                            <div class="prop-precio" style="text-decoration:line-through;color:#bbb;font-size:14px">{int(b['precio_anterior']):,} €</div>
                            <div class="prop-precio">{int(b['precio_actual']):,} €</div>
                            <a href="{safe_str(b.get("enlace"))}" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver →</a>
                          </div>
                        </div>""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error durante el escaneo: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Inventario · Oportunidades</div>', unsafe_allow_html=True)

    fa, fb = st.columns(2)
    with fa:
        filtro_sem = st.selectbox("Semáforo", ["Todos", "🟢 Oportunidad", "🟡 Vigilar", "🔴 Normal"], key="radar_filtro")
    with fb:
        filtro_inter = st.selectbox("Tipo", ["Todos", "Particular", "Agencia"], key="radar_inter")

    lista = scored
    if filtro_sem != "Todos":
        lista = [x for x in lista if x.get("semaforo") == filtro_sem]
    if filtro_inter != "Todos":
        lista = [x for x in lista if filtro_inter.lower() in safe_str(x.get("intermediario")).lower()]

    st.caption(f"{len(lista)} propiedades")

    if not lista:
        st.info("Aún no hay datos. Lance el Radar para empezar.")
    else:
        for p in lista:
            sem = safe_str(p.get("semaforo"), "🔴 Normal")
            intermediario = safe_str(p.get("intermediario"), "N/A")
            es_part = "particular" in intermediario.lower()
            badge = '<span class="badge-particular">Particular</span>' if es_part else '<span class="badge-agencia">Agencia</span>'
            clase = "verde" if "🟢" in sem else "amarillo" if "🟡" in sem else "rojo"
            st.markdown(f"""
            <div class="prop-card {clase}">
              <div style="flex:1">
                <div class="prop-dir">{safe_str(p.get("zona"))} {badge}</div>
                <div class="prop-meta">{safe_str(p.get("direccion","N/A"))} · {safe_int(p.get("m2"))} m² · {safe_int(p.get("habitaciones"))} hab · {safe_int(p.get("days_on_market"))} días</div>
              </div>
              <div style="text-align:right">
                <div class="prop-precio">{int(float(p.get("last_price",0))):,} €</div>
                <div class="prop-score">{sem} · Score {p.get("score",0)}</div><br>
                <a href="{safe_str(p.get("enlace"))}" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver en Idealista →</a>
              </div>
            </div>""", unsafe_allow_html=True)


# =========================
# TAB 1: PARTICULARES
# =========================
with tabs[1]:
    st.markdown('<div class="section-title">Propietarios · Captación directa</div>', unsafe_allow_html=True)

    with st.expander("➕ Añadir particular"):
        with st.form("add_particular", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nombre = st.text_input("Nombre")
                telefono = st.text_input("Teléfono")
                idealista_url = st.text_input("Link Idealista (opcional)")
            with c2:
                zona = st.text_input("Zona")
                direccion = st.text_input("Dirección")
                tipo_vivienda = st.selectbox("Tipo", ["", "Piso", "Chalet", "Ático", "Dúplex", "Otro"])
            c3, c4 = st.columns(2)
            with c3:
                m2_construidos = st.number_input("M² construidos", min_value=0, step=1, value=0)
            with c4:
                m2_parcela = st.number_input("M² parcela", min_value=0, step=1, value=0)
            comentarios = st.text_area("Comentarios", height=80)
            semaforo_manual = st.selectbox("Semáforo", ["VERDE", "AMARILLO", "ROJO"], index=1)
            if st.form_submit_button("Guardar"):
                insert_particular({
                    "idealista_url": idealista_url.strip(),
                    "idealista_id": extract_idealista_id(idealista_url.strip()),
                    "zona": zona.strip(), "direccion": direccion.strip(),
                    "tipo_vivienda": tipo_vivienda.strip(),
                    "m2_construidos": int(m2_construidos), "m2_parcela": int(m2_parcela),
                    "nombre": nombre.strip(), "telefono": telefono.strip(),
                    "comentarios": comentarios.strip(),
                    "use_manual_semaforo": 1, "semaforo_manual": semaforo_manual
                })
                st.success("Guardado.")
                st.rerun()

    cA, cB = st.columns(2)
    with cA:
        filtro_color = st.selectbox("Filtrar", ["Todos", "VERDE", "AMARILLO", "ROJO"], key="part_filtro")
    with cB:
        buscar = st.text_input("Buscar", key="part_buscar", placeholder="nombre, teléfono, zona...").strip().lower()

    dfp = df_query("SELECT * FROM particulares ORDER BY updated_at DESC")
    if filtro_color != "Todos":
        dfp = dfp[dfp["semaforo_manual"] == filtro_color]
    if buscar:
        dfp = dfp[dfp.apply(lambda r: buscar in " ".join([
            safe_str(r.get("nombre")), safe_str(r.get("telefono")),
            safe_str(r.get("zona")), safe_str(r.get("direccion")),
            safe_str(r.get("comentarios"))]).lower(), axis=1)]

    if dfp.empty:
        st.info("No hay particulares aún.")
    else:
        for r in dfp.to_dict(orient="records"):
            pid = r["id"]
            sem = r.get("semaforo_manual", "AMARILLO")
            st.markdown(f"""
            <div class="card" style="border-left: 3px solid {sem_color(sem)}; border-radius: 0 10px 10px 0;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div style="font-size:15px;font-weight:500;color:#1C1C1C">{sem_emoji(sem)} {safe_str(r.get("nombre"),"Sin nombre")}</div>
                  <div class="small muted">{safe_str(r.get("telefono","sin teléfono"))} · {safe_str(r.get("zona"))} · {safe_str(r.get("direccion"))}</div>
                  <div class="small muted">{safe_str(r.get("tipo_vivienda"))} · {safe_int(r.get("m2_construidos"))} m²</div>
                </div>
              </div>
              <div class="hr"></div>
              <div class="small" style="color:#999">{safe_str(r.get("comentarios","Sin comentarios"))}</div>
              {'<div class="small" style="margin-top:8px"><a href="' + safe_str(r.get("idealista_url")) + '" target="_blank" style="color:#C9A84C;letter-spacing:1px;font-size:11px;">Ver en Idealista →</a></div>' if safe_str(r.get("idealista_url")) else ""}
            </div>""", unsafe_allow_html=True)
            with st.expander(f"Editar #{pid}"):
                sem_new = st.selectbox("Semáforo", ["VERDE", "AMARILLO", "ROJO"],
                                       index=["VERDE","AMARILLO","ROJO"].index(sem), key=f"ps_{pid}")
                com_new = st.text_area("Comentarios", value=safe_str(r.get("comentarios")), height=80, key=f"pc_{pid}")
                if st.button("Guardar", key=f"psave_{pid}"):
                    update_particular(pid, sem_new, com_new)
                    st.success("Actualizado.")
                    st.rerun()


# =========================
# TAB 2: AGENCIA
# =========================
with tabs[2]:
    st.markdown('<div class="section-title">Propiedades con agencia · Estrategia</div>', unsafe_allow_html=True)

    with st.expander("➕ Añadir propiedad con agencia"):
        with st.form("add_agencia", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                idealista_url = st.text_input("Link Idealista")
                agencia_nombre = st.text_input("Agencia")
            with c2:
                zona = st.text_input("Zona")
                direccion = st.text_input("Dirección")
            c3, c4 = st.columns(2)
            with c3:
                tipo_vivienda = st.selectbox("Tipo", ["", "Piso", "Chalet", "Ático", "Dúplex", "Otro"], key="ag_tipo")
                m2_construidos = st.number_input("M² construidos", min_value=0, step=1, value=0, key="ag_m2c")
            with c4:
                m2_parcela = st.number_input("M² parcela", min_value=0, step=1, value=0, key="ag_m2p")
                semaforo_manual = st.selectbox("Semáforo", ["VERDE", "AMARILLO", "ROJO"], index=1, key="ag_sem")
            notas = st.text_area("Notas / estrategia", height=80)
            if st.form_submit_button("Guardar"):
                insert_agencia({
                    "idealista_url": idealista_url.strip(),
                    "idealista_id": extract_idealista_id(idealista_url.strip()),
                    "zona": zona.strip(), "direccion": direccion.strip(),
                    "tipo_vivienda": tipo_vivienda.strip(),
                    "m2_construidos": int(m2_construidos), "m2_parcela": int(m2_parcela),
                    "agencia_nombre": agencia_nombre.strip(), "notas": notas.strip(),
                    "semaforo_manual": semaforo_manual
                })
                st.success("Guardado.")
                st.rerun()

    cA, cB = st.columns(2)
    with cA:
        filtro_color = st.selectbox("Filtrar", ["Todos", "VERDE", "AMARILLO", "ROJO"], key="ag_filtro")
    with cB:
        buscar = st.text_input("Buscar", key="ag_buscar", placeholder="zona, agencia, notas...").strip().lower()

    dfa = df_query("SELECT * FROM agencia ORDER BY updated_at DESC")
    if filtro_color != "Todos":
        dfa = dfa[dfa["semaforo_manual"] == filtro_color]
    if buscar:
        dfa = dfa[dfa.apply(lambda r: buscar in " ".join([
            safe_str(r.get("zona")), safe_str(r.get("direccion")),
            safe_str(r.get("agencia_nombre")), safe_str(r.get("notas"))]).lower(), axis=1)]

    if dfa.empty:
        st.info("No hay propiedades en agencia aún.")
    else:
        for r in dfa.to_dict(orient="records"):
            aid = r["id"]
            sem = r.get("semaforo_manual", "AMARILLO")
            st.markdown(f"""
            <div class="card" style="border-left: 3px solid {sem_color(sem)}; border-radius: 0 10px 10px 0;">
              <div style="font-size:15px;font-weight:500;color:#1C1C1C">{sem_emoji(sem)} {safe_str(r.get("zona"))} <span class="muted">· {safe_str(r.get("agencia_nombre","Agencia desconocida"))}</span></div>
              <div class="small muted">{safe_str(r.get("direccion"))} · {safe_str(r.get("tipo_vivienda"))} · {safe_int(r.get("m2_construidos"))} m²</div>
              <div class="hr"></div>
              <div class="small" style="color:#999">{safe_str(r.get("notas","Sin notas"))}</div>
              {'<div class="small" style="margin-top:8px"><a href="' + safe_str(r.get("idealista_url")) + '" target="_blank" style="color:#C9A84C;letter-spacing:1px;font-size:11px;">Ver en Idealista →</a></div>' if safe_str(r.get("idealista_url")) else ""}
            </div>""", unsafe_allow_html=True)
            with st.expander(f"Editar #{aid}"):
                sem_new = st.selectbox("Semáforo", ["VERDE", "AMARILLO", "ROJO"],
                                       index=["VERDE","AMARILLO","ROJO"].index(sem), key=f"as_{aid}")
                notas_new = st.text_area("Notas", value=safe_str(r.get("notas")), height=80, key=f"an_{aid}")
                if st.button("Guardar", key=f"asave_{aid}"):
                    update_agencia(aid, sem_new, notas_new)
                    st.success("Actualizado.")
                    st.rerun()


# =========================
# TAB 3: AGENDA
# =========================
with tabs[3]:
    st.markdown('<div class="section-title">Agenda · Calendario privado</div>', unsafe_allow_html=True)

    hoy = date.today().isoformat()
    prox7 = (date.today() + timedelta(days=7)).isoformat()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Hoy")
        df_today = df_query("SELECT * FROM agenda WHERE fecha=? ORDER BY hora ASC", (hoy,))
        if df_today.empty:
            st.caption("Sin eventos hoy.")
        else:
            for r in df_today.to_dict(orient="records"):
                st.markdown(f"""<div class="card">
                  <div style="font-size:13px;font-weight:500">{safe_str(r.get('hora',''))} · {r.get('titulo')}</div>
                  <div class="small muted">{safe_str(r.get('categoria'))} · {safe_str(r.get('detalle',''))}</div>
                </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("#### Próximos 7 días")
        df_week = df_query("SELECT * FROM agenda WHERE fecha>? AND fecha<=? ORDER BY fecha ASC, hora ASC", (hoy, prox7))
        if df_week.empty:
            st.caption("Sin eventos próximos.")
        else:
            for r in df_week.to_dict(orient="records"):
                st.markdown(f"""<div class="card">
                  <div style="font-size:13px;font-weight:500">{r.get('fecha')} {safe_str(r.get('hora',''))} · {r.get('titulo')}</div>
                  <div class="small muted">{safe_str(r.get('categoria'))}</div>
                </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Añadir evento")
    with st.form("add_agenda", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            fecha = st.date_input("Fecha", value=date.today())
        with c2:
            hora = st.text_input("Hora (HH:MM)", placeholder="10:30")
        with c3:
            categoria = st.selectbox("Categoría", ["Tarea", "Llamada", "WhatsApp", "Visita", "Reunión", "Seguimiento"])
        titulo = st.text_input("Título *")
        detalle = st.text_area("Detalle", height=80)
        rel_tipo = st.selectbox("Relacionado con", ["", "particular", "agencia"])
        rel_id = st.number_input("ID relacionado (opcional)", min_value=0, step=1, value=0)
        if st.form_submit_button("Guardar en agenda"):
            if not titulo.strip():
                st.error("El título es obligatorio.")
            else:
                insert_agenda({
                    "fecha": fecha.isoformat(), "hora": hora.strip(),
                    "titulo": titulo.strip(), "detalle": detalle.strip(),
                    "categoria": categoria, "relacionado_tipo": rel_tipo.strip(),
                    "relacionado_id": int(rel_id) if int(rel_id) > 0 else None
                })
                st.success("Guardado.")
                st.rerun()

    st.divider()
    st.markdown("#### Ver por fecha")
    filtro_fecha = st.date_input("Fecha", value=date.today(), key="agenda_fecha")
    df_day = df_query("SELECT * FROM agenda WHERE fecha=? ORDER BY hora ASC", (filtro_fecha.isoformat(),))
    if df_day.empty:
        st.info("Sin eventos ese día.")
    else:
        for r in df_day.to_dict(orient="records"):
            ag_id = r["id"]
            st.markdown(f"""<div class="card">
              <div style="font-size:13px;font-weight:500">{safe_str(r.get('hora',''))} · {r.get('titulo')}</div>
              <div class="small muted">{safe_str(r.get('categoria'))} · {safe_str(r.get('detalle',''))}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Borrar", key=f"del_{ag_id}"):
                delete_agenda(ag_id)
                st.rerun()