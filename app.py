import re
import sqlite3
import math
from datetime import datetime, timedelta, date
from typing import Optional

import pandas as pd
import streamlit as st

import db as radar_db

DB_PATH = "radar_lujo.db"
st.set_page_config(page_title="InmoLuxury · CRM Privado", layout="wide", page_icon="💎")

# =========================
# Estilos deluxe
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Montserrat:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #FAF8F4;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp { background-color: #FAF8F4; }
.block-container { padding-top: 0 !important; background-color: #FAF8F4; }

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
    font-size: 17px;
    color: #C9A84C;
    font-style: italic;
}
.topbar-right { font-size: 11px; color: #666; letter-spacing: 1px; }

.stTabs [data-baseweb="tab-list"] {
    background: #fff;
    border-bottom: 1px solid #E8E2D6;
    gap: 0; padding: 0 8px;
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

.section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #C9A84C;
    margin-bottom: 16px;
    font-weight: 500;
}

.stat-card {
    background: #fff;
    border: 1px solid #E8E2D6;
    border-radius: 12px;
    padding: 20px 22px;
}
.stat-label {
    font-size: 10px; color: #999;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px; font-weight: 500;
}
.stat-value {
    font-size: 32px; font-weight: 400;
    color: #1C1C1C;
    font-family: 'Cormorant Garamond', serif;
}
.stat-value.gold { color: #C9A84C; }
.stat-sub { font-size: 11px; color: #bbb; margin-top: 4px; }

.prop-card {
    background: #fff;
    border: 1px solid #E8E2D6;
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s;
}
.prop-card:hover { box-shadow: 0 4px 20px rgba(201,168,76,0.08); }
.prop-card.verde  { border-left: 3px solid #4CAF84; }
.prop-card.amarillo { border-left: 3px solid #C9A84C; }
.prop-card.rojo   { border-left: 3px solid #E06060; }

.prop-zona {
    font-size: 11px; letter-spacing: 2px;
    text-transform: uppercase; color: #C9A84C;
    margin-bottom: 4px; font-weight: 500;
}
.prop-dir {
    font-size: 15px; font-weight: 500;
    color: #1C1C1C; margin-bottom: 6px;
}
.prop-meta { font-size: 12px; color: #999; line-height: 1.8; }
.prop-precio {
    font-size: 22px; font-weight: 400;
    color: #1C1C1C;
    font-family: 'Cormorant Garamond', serif;
    text-align: right;
}
.prop-score {
    display: inline-block;
    background: #FAF8F4;
    border: 1px solid #E8E2D6;
    border-radius: 4px;
    font-size: 10px; color: #888;
    padding: 3px 10px; margin-top: 6px;
    letter-spacing: 0.5px;
}
.badge-particular {
    display: inline-block;
    background: #F0F9F4; color: #3A8A5F;
    font-size: 9px; letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 8px; border-radius: 4px;
    border: 1px solid #C2E0CF; margin-left: 8px;
}
.badge-agencia {
    display: inline-block;
    background: #F5F0E8; color: #8A6A2A;
    font-size: 9px; letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 8px; border-radius: 4px;
    border: 1px solid #DDD0B0; margin-left: 8px;
}
.badge-nv {
    display: inline-block;
    background: #F0F4FF; color: #3A5A8A;
    font-size: 9px; letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 8px; border-radius: 4px;
    border: 1px solid #C0CFEE; margin-left: 8px;
}

.card {
    background: #fff;
    border: 1px solid #E8E2D6;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 14px;
}
.card:hover { box-shadow: 0 4px 20px rgba(201,168,76,0.08); }
.hr { height: 1px; background: #E8E2D6; margin: 12px 0; }
.muted { opacity: 0.6; font-size: 0.88rem; }
.small { font-size: 0.9rem; }

.stButton > button {
    font-family: 'Montserrat', sans-serif;
    font-size: 11px; letter-spacing: 1.5px;
    text-transform: uppercase;
    border-radius: 6px; font-weight: 500;
}
.stButton > button[kind="primary"] {
    background: #1C1C1C !important;
    color: #C9A84C !important;
    border: 1px solid #C9A84C !important;
}
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
hr { border-color: #E8E2D6 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
  <div class="logo"><span>Inmo</span>Luxury · <span style="color:#fff;letter-spacing:1px;font-size:12px;">Madrid</span></div>
  <div class="welcome">Bienvenido, Señor Marcelo</div>
  <div class="topbar-right">CRM Privado · Lujo</div>
</div>
""", unsafe_allow_html=True)


# =========================
# Utils
# =========================
def safe_int(x, default=0) -> int:
    if x is None: return default
    try:
        if isinstance(x, float) and math.isnan(x): return default
    except: pass
    try: return int(float(str(x).replace(".", "").replace(",", "")))
    except: return default

def safe_str(x, default="") -> str:
    if x is None: return default
    s = str(x)
    return default if s.lower() == "nan" else s.strip()

def sem_color(s): return {"VERDE":"#4CAF84","AMARILLO":"#C9A84C","ROJO":"#E06060"}.get(s,"#C9A84C")
def sem_emoji(s): return {"VERDE":"🟢","AMARILLO":"🟡","ROJO":"🔴"}.get(s,"🟡")

def extract_idealista_id(url: str) -> Optional[str]:
    if not url: return None
    m = re.search(r"/inmueble/(\d+)", url)
    return m.group(1) if m else None

def calcular_score(intermediario, dias, bajada_pct):
    score = 0
    if "particular" in str(intermediario).lower(): score += 30
    if dias > 60: score += 25
    elif dias > 30: score += 15
    elif dias > 7: score += 5
    if bajada_pct > 10: score += 30
    elif bajada_pct > 5: score += 20
    elif bajada_pct > 2: score += 10
    return min(score, 100)

def score_to_semaforo(score):
    if score >= 50: return "🟢 Oportunidad"
    elif score >= 25: return "🟡 Vigilar"
    return "🔴 Normal"


# =========================
# DB local (particulares, agencia, agenda, propiedades)
# =========================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS propiedades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        fecha_entrada TEXT,
        zona TEXT,
        direccion TEXT,
        tipo_vivienda TEXT,
        m2_construidos INTEGER,
        m2_parcela INTEGER,
        habitaciones INTEGER,
        precio REAL,
        precio_m2 REAL,
        planta TEXT,
        estado TEXT,
        intermediario TEXT,
        idealista_url TEXT,
        idealista_id TEXT,
        notas TEXT,
        semaforo TEXT DEFAULT 'AMARILLO',
        dias_mercado INTEGER DEFAULT 0
    );""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS particulares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        idealista_url TEXT, idealista_id TEXT,
        zona TEXT, direccion TEXT, tipo_vivienda TEXT,
        m2_construidos INTEGER, m2_parcela INTEGER,
        nombre TEXT, telefono TEXT, comentarios TEXT,
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

def df_query(sql, params=()):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute(sql, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

def insert_propiedad(data: dict):
    now = datetime.utcnow().isoformat()
    precio = float(data.get("precio") or 0)
    m2 = int(data.get("m2_construidos") or 0)
    precio_m2 = round(precio / m2, 0) if m2 > 0 else 0
    dias = int(data.get("dias_mercado") or 0)
    score = calcular_score(data.get("intermediario",""), dias, 0)
    sem = score_to_semaforo(score)
    execute("""
        INSERT INTO propiedades (
            created_at, updated_at, fecha_entrada, zona, direccion,
            tipo_vivienda, m2_construidos, m2_parcela, habitaciones,
            precio, precio_m2, planta, estado, intermediario,
            idealista_url, idealista_id, notas, semaforo, dias_mercado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, now,
          data.get("fecha_entrada"), data.get("zona"), data.get("direccion"),
          data.get("tipo_vivienda"), m2, int(data.get("m2_parcela") or 0),
          int(data.get("habitaciones") or 0), precio, precio_m2,
          data.get("planta"), data.get("estado"), data.get("intermediario"),
          data.get("idealista_url"), extract_idealista_id(data.get("idealista_url","")),
          data.get("notas"), sem, dias))

def update_propiedad(pid, notas, semaforo, dias):
    now = datetime.utcnow().isoformat()
    execute("UPDATE propiedades SET updated_at=?, notas=?, semaforo=?, dias_mercado=? WHERE id=?",
            (now, notas, semaforo, dias, pid))

def delete_propiedad(pid):
    execute("DELETE FROM propiedades WHERE id=?", (pid,))

def insert_particular(data: dict):
    now = datetime.utcnow().isoformat()
    execute("""
        INSERT INTO particulares (
            created_at, updated_at, idealista_url, idealista_id,
            zona, direccion, tipo_vivienda, m2_construidos, m2_parcela,
            nombre, telefono, comentarios, semaforo_manual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, now, data.get("idealista_url"), extract_idealista_id(data.get("idealista_url","")),
          data.get("zona"), data.get("direccion"), data.get("tipo_vivienda"),
          data.get("m2_construidos"), data.get("m2_parcela"),
          data.get("nombre"), data.get("telefono"), data.get("comentarios"),
          data.get("semaforo_manual", "AMARILLO")))

def update_particular(pid, sem, comentarios):
    now = datetime.utcnow().isoformat()
    execute("UPDATE particulares SET updated_at=?, semaforo_manual=?, comentarios=? WHERE id=?",
            (now, sem, comentarios, pid))

def insert_agencia(data: dict):
    now = datetime.utcnow().isoformat()
    execute("""
        INSERT INTO agencia (
            created_at, updated_at, idealista_url, idealista_id,
            zona, direccion, tipo_vivienda, m2_construidos, m2_parcela,
            agencia_nombre, notas, semaforo_manual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, now, data.get("idealista_url"), extract_idealista_id(data.get("idealista_url","")),
          data.get("zona"), data.get("direccion"), data.get("tipo_vivienda"),
          data.get("m2_construidos"), data.get("m2_parcela"),
          data.get("agencia_nombre"), data.get("notas"),
          data.get("semaforo_manual", "AMARILLO")))

def update_agencia(aid, sem, notas):
    now = datetime.utcnow().isoformat()
    execute("UPDATE agencia SET updated_at=?, semaforo_manual=?, notas=? WHERE id=?",
            (now, sem, notas, aid))

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

def delete_agenda(agenda_id):
    execute("DELETE FROM agenda WHERE id=?", (agenda_id,))


# =========================
# Init
# =========================
init_db()
radar_db.init_db()

# =========================
# Tabs
# =========================
tabs = st.tabs(["🏠 PROPIEDADES", "👤 PARTICULARES", "🏢 AGENCIA", "📅 AGENDA"])


# =========================
# TAB 0: PROPIEDADES
# =========================
with tabs[0]:
    st.markdown('<div class="section-title">Propiedades · Registro diario desde Idealista</div>', unsafe_allow_html=True)

    # Stats
    df_props = df_query("SELECT * FROM propiedades ORDER BY created_at DESC")
    total = len(df_props)
    oport = len(df_props[df_props["semaforo"] == "🟢 Oportunidad"]) if not df_props.empty else 0
    parts = len(df_props[df_props["intermediario"].str.lower().str.contains("particular", na=False)]) if not df_props.empty else 0
    hoy_count = len(df_props[df_props["fecha_entrada"] == date.today().isoformat()]) if not df_props.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Total registradas</div>
            <div class="stat-value gold">{total}</div>
            <div class="stat-sub">en cartera</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Añadidas hoy</div>
            <div class="stat-value">{hoy_count}</div>
            <div class="stat-sub">esta mañana</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Particulares</div>
            <div class="stat-value">{parts}</div>
            <div class="stat-sub">sin agencia</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Oportunidades</div>
            <div class="stat-value gold">{oport}</div>
            <div class="stat-sub">score alto</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Formulario añadir
    with st.expander("➕ Añadir propiedad desde Idealista", expanded=False):
        with st.form("add_prop", clear_on_submit=True):
            st.markdown('<div class="section-title">Nueva propiedad</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                idealista_url = st.text_input("🔗 Link de Idealista *")
                zona = st.selectbox("Zona", ["Aravaca", "Valdemarín", "Puerta de Hierro", "Pozuelo", "Majadahonda", "El Viso", "Otra"])
                direccion = st.text_input("Dirección")
                intermediario = st.selectbox("Vendido por", ["Particular", "Agencia", "N/A"])
            with c2:
                precio = st.number_input("Precio (€) *", min_value=0, step=10000, value=1300000)
                tipo_vivienda = st.selectbox("Tipo", ["Chalet", "Piso", "Ático", "Dúplex", "Villa", "Otro"])
                fecha_entrada = st.date_input("Fecha del anuncio", value=date.today())
                dias_mercado = st.number_input("Días en mercado (aprox.)", min_value=0, step=1, value=0)
            c3, c4, c5 = st.columns(3)
            with c3:
                m2_construidos = st.number_input("M² construidos", min_value=0, step=1, value=0)
            with c4:
                m2_parcela = st.number_input("M² parcela", min_value=0, step=1, value=0)
            with c5:
                habitaciones = st.number_input("Habitaciones", min_value=0, step=1, value=0)
            c6, c7 = st.columns(2)
            with c6:
                planta = st.text_input("Planta", placeholder="Baja, 1ª, Ático...")
            with c7:
                estado = st.selectbox("Estado", ["Buen estado", "A estrenar", "Reformado", "Para reformar", "Obra nueva", "N/A"])
            notas = st.text_area("Notas / observaciones", height=80)

            if st.form_submit_button("💎 Guardar propiedad", type="primary"):
                if not idealista_url.strip():
                    st.error("El link de Idealista es obligatorio.")
                else:
                    insert_propiedad({
                        "idealista_url": idealista_url.strip(),
                        "zona": zona, "direccion": direccion.strip(),
                        "tipo_vivienda": tipo_vivienda,
                        "m2_construidos": int(m2_construidos),
                        "m2_parcela": int(m2_parcela),
                        "habitaciones": int(habitaciones),
                        "precio": float(precio),
                        "planta": planta.strip(),
                        "estado": estado,
                        "intermediario": intermediario,
                        "fecha_entrada": fecha_entrada.isoformat(),
                        "dias_mercado": int(dias_mercado),
                        "notas": notas.strip(),
                    })
                    st.success("✅ Propiedad guardada.")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros
    st.markdown('<div class="section-title">Inventario · Oportunidades</div>', unsafe_allow_html=True)
    fa, fb, fc = st.columns(3)
    with fa:
        f_sem = st.selectbox("Semáforo", ["Todos", "🟢 Oportunidad", "🟡 Vigilar", "🔴 Normal"], key="p_sem")
    with fb:
        f_zona = st.selectbox("Zona", ["Todas", "Aravaca", "Valdemarín", "Puerta de Hierro", "Pozuelo", "Majadahonda", "El Viso", "Otra"], key="p_zona")
    with fc:
        f_inter = st.selectbox("Tipo", ["Todos", "Particular", "Agencia"], key="p_inter")

    df_show = df_query("SELECT * FROM propiedades ORDER BY created_at DESC")

    if f_sem != "Todos" and not df_show.empty:
        df_show = df_show[df_show["semaforo"] == f_sem]
    if f_zona != "Todas" and not df_show.empty:
        df_show = df_show[df_show["zona"] == f_zona]
    if f_inter != "Todos" and not df_show.empty:
        df_show = df_show[df_show["intermediario"].str.lower().str.contains(f_inter.lower(), na=False)]

    if df_show.empty:
        st.info("Aún no hay propiedades. Añada la primera usando el formulario de arriba.")
    else:
        st.caption(f"{len(df_show)} propiedades")
        for r in df_show.to_dict(orient="records"):
            pid = r["id"]
            sem = safe_str(r.get("semaforo"), "🟡 Vigilar")
            intermediario = safe_str(r.get("intermediario"), "N/A")
            es_part = "particular" in intermediario.lower()
            badge = '<span class="badge-particular">Particular</span>' if es_part else '<span class="badge-agencia">Agencia</span>'
            clase = "verde" if "🟢" in sem else "amarillo" if "🟡" in sem else "rojo"
            precio_fmt = f"{int(float(r.get('precio') or 0)):,}".replace(",", ".")
            precio_m2_fmt = f"{int(float(r.get('precio_m2') or 0)):,}".replace(",", ".")

            st.markdown(f"""
            <div class="prop-card {clase}">
              <div style="flex:1">
                <div class="prop-zona">{safe_str(r.get("zona"))}</div>
                <div class="prop-dir">{safe_str(r.get("direccion","Sin dirección"))} {badge}</div>
                <div class="prop-meta">
                  🏠 {safe_str(r.get("tipo_vivienda"))} &nbsp;·&nbsp;
                  📐 {safe_int(r.get("m2_construidos"))} m² &nbsp;·&nbsp;
                  🛏 {safe_int(r.get("habitaciones"))} hab &nbsp;·&nbsp;
                  ⏳ {safe_int(r.get("dias_mercado"))} días &nbsp;·&nbsp;
                  📊 {safe_str(r.get("estado"))}
                </div>
                <div class="prop-meta" style="margin-top:4px">
                  💶 {precio_m2_fmt} €/m² &nbsp;·&nbsp;
                  📅 {safe_str(r.get("fecha_entrada"))}
                </div>
              </div>
              <div style="text-align:right;min-width:140px">
                <div class="prop-precio">{precio_fmt} €</div>
                <div class="prop-score">{sem}</div><br>
                {'<a href="' + safe_str(r.get("idealista_url")) + '" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver en Idealista →</a>' if safe_str(r.get("idealista_url")) else ""}
              </div>
            </div>""", unsafe_allow_html=True)

            with st.expander(f"Editar / borrar #{pid}"):
                col1, col2 = st.columns(2)
                with col1:
                    sem_new = st.selectbox("Semáforo", ["🟢 Oportunidad", "🟡 Vigilar", "🔴 Normal"],
                                           index=["🟢 Oportunidad","🟡 Vigilar","🔴 Normal"].index(sem) if sem in ["🟢 Oportunidad","🟡 Vigilar","🔴 Normal"] else 1,
                                           key=f"psem_{pid}")
                    dias_new = st.number_input("Días en mercado", min_value=0, value=safe_int(r.get("dias_mercado")), key=f"pdias_{pid}")
                with col2:
                    notas_new = st.text_area("Notas", value=safe_str(r.get("notas")), height=80, key=f"pnot_{pid}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Guardar", key=f"psave_{pid}"):
                        update_propiedad(pid, notas_new, sem_new, dias_new)
                        st.success("Actualizado.")
                        st.rerun()
                with c2:
                    if st.button("🗑️ Borrar propiedad", key=f"pdel_{pid}"):
                        delete_propiedad(pid)
                        st.success("Borrada.")
                        st.rerun()


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
            if st.form_submit_button("💎 Guardar", type="primary"):
                insert_particular({
                    "idealista_url": idealista_url.strip(),
                    "zona": zona.strip(), "direccion": direccion.strip(),
                    "tipo_vivienda": tipo_vivienda.strip(),
                    "m2_construidos": int(m2_construidos), "m2_parcela": int(m2_parcela),
                    "nombre": nombre.strip(), "telefono": telefono.strip(),
                    "comentarios": comentarios.strip(),
                    "semaforo_manual": semaforo_manual
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
            <div class="card" style="border-left: 3px solid {sem_color(sem)}; border-radius: 0 12px 12px 0;">
              <div style="font-size:15px;font-weight:500;color:#1C1C1C">{sem_emoji(sem)} {safe_str(r.get("nombre"),"Sin nombre")}</div>
              <div class="small muted">{safe_str(r.get("telefono","sin teléfono"))} · {safe_str(r.get("zona"))} · {safe_str(r.get("direccion"))}</div>
              <div class="small muted">{safe_str(r.get("tipo_vivienda"))} · {safe_int(r.get("m2_construidos"))} m²</div>
              <div class="hr"></div>
              <div class="small" style="color:#999">{safe_str(r.get("comentarios","Sin comentarios"))}</div>
              {'<div style="margin-top:8px"><a href="' + safe_str(r.get("idealista_url")) + '" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver en Idealista →</a></div>' if safe_str(r.get("idealista_url")) else ""}
            </div>""", unsafe_allow_html=True)
            with st.expander(f"Editar #{pid}"):
                sem_new = st.selectbox("Semáforo", ["VERDE","AMARILLO","ROJO"],
                                       index=["VERDE","AMARILLO","ROJO"].index(sem), key=f"ps_{pid}")
                com_new = st.text_area("Comentarios", value=safe_str(r.get("comentarios")), height=80, key=f"pc_{pid}")
                if st.button("💾 Guardar", key=f"psave_{pid}"):
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
                tipo_vivienda = st.selectbox("Tipo", ["","Piso","Chalet","Ático","Dúplex","Otro"], key="ag_tipo")
                m2_construidos = st.number_input("M² construidos", min_value=0, step=1, value=0, key="ag_m2c")
            with c4:
                m2_parcela = st.number_input("M² parcela", min_value=0, step=1, value=0, key="ag_m2p")
                semaforo_manual = st.selectbox("Semáforo", ["VERDE","AMARILLO","ROJO"], index=1, key="ag_sem")
            notas = st.text_area("Notas / estrategia", height=80)
            if st.form_submit_button("💎 Guardar", type="primary"):
                insert_agencia({
                    "idealista_url": idealista_url.strip(),
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
        filtro_color = st.selectbox("Filtrar", ["Todos","VERDE","AMARILLO","ROJO"], key="ag_filtro")
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
            <div class="card" style="border-left: 3px solid {sem_color(sem)}; border-radius: 0 12px 12px 0;">
              <div style="font-size:15px;font-weight:500;color:#1C1C1C">{sem_emoji(sem)} {safe_str(r.get("zona"))} <span class="muted">· {safe_str(r.get("agencia_nombre","Agencia desconocida"))}</span></div>
              <div class="small muted">{safe_str(r.get("direccion"))} · {safe_str(r.get("tipo_vivienda"))} · {safe_int(r.get("m2_construidos"))} m²</div>
              <div class="hr"></div>
              <div class="small" style="color:#999">{safe_str(r.get("notas","Sin notas"))}</div>
              {'<div style="margin-top:8px"><a href="' + safe_str(r.get("idealista_url")) + '" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver en Idealista →</a></div>' if safe_str(r.get("idealista_url")) else ""}
            </div>""", unsafe_allow_html=True)
            with st.expander(f"Editar #{aid}"):
                sem_new = st.selectbox("Semáforo", ["VERDE","AMARILLO","ROJO"],
                                       index=["VERDE","AMARILLO","ROJO"].index(sem), key=f"as_{aid}")
                notas_new = st.text_area("Notas", value=safe_str(r.get("notas")), height=80, key=f"an_{aid}")
                if st.button("💾 Guardar", key=f"asave_{aid}"):
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
            categoria = st.selectbox("Categoría", ["Tarea","Llamada","WhatsApp","Visita","Reunión","Seguimiento"])
        titulo = st.text_input("Título *")
        detalle = st.text_area("Detalle", height=80)
        rel_tipo = st.selectbox("Relacionado con", ["","particular","agencia"])
        rel_id = st.number_input("ID relacionado (opcional)", min_value=0, step=1, value=0)
        if st.form_submit_button("💎 Guardar en agenda", type="primary"):
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
            if st.button("🗑️ Borrar", key=f"del_{ag_id}"):
                delete_agenda(ag_id)
                st.rerun()