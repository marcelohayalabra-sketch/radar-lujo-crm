import re
import sqlite3
import math
from datetime import datetime, timedelta, date
from typing import Optional

import pandas as pd
import streamlit as st

import scraper
import db as radar_db

DB_PATH = "radar_lujo.db"
st.set_page_config(page_title="InmoLuxury · CRM Privado", layout="wide", page_icon="💎")

# =========================
# SCORING SIMPLE (AUTOMÁTICO)
# =========================
def calcular_score(p):
    score = 0

    dias = int(p.get("days_on_market") or 0)
    if dias > 60:
        score += 25
    elif dias > 30:
        score += 15
    elif dias > 7:
        score += 5

    bajada = float(p.get("bajada_pct_reciente") or 0)
    if bajada > 10:
        score += 30
    elif bajada > 5:
        score += 20
    elif bajada > 2:
        score += 10

    intermediario = str(p.get("intermediario") or "").lower()
    if "particular" in intermediario:
        score += 30

    return score


def semaforo(score):
    if score >= 60:
        return "🟢 Oportunidad"
    elif score >= 30:
        return "🟡 Vigilar"
    else:
        return "🔴 Normal"


# =========================
# UTILS
# =========================
def safe_int(x, default=0):
    try:
        return int(float(x))
    except:
        return default


def safe_str(x, default=""):
    if x is None:
        return default
    return str(x).strip()


# =========================
# INIT
# =========================
radar_db.init_db()

SCORING_RULES = {}

tabs = st.tabs(["💎 RADAR"])


# =========================
# RADAR
# =========================
with tabs[0]:

    scored = radar_db.get_scored_inventory(limit=200, rules=SCORING_RULES)

    # 👉 APLICAR SCORING
    for p in scored:
        s = calcular_score(p)
        p["score"] = s
        p["semaforo"] = semaforo(s)

    total = len(scored)
    oportunidades = sum(1 for x in scored if x["semaforo"] == "🟢 Oportunidad")

    st.title("💎 Radar de oportunidades")

    c1, c2 = st.columns(2)
    c1.metric("Total propiedades", total)
    c2.metric("Oportunidades", oportunidades)

    st.divider()

    if st.button("💎 Lanzar Radar"):
        propiedades = scraper.obtener_datos_lujo(precio_min=1000000, limit=20)
        radar_db.run_scan(propiedades)
        st.success("Escaneo completado")
        st.rerun()

    st.divider()

    for p in scored:
        st.markdown(f"""
        ### {p.get("zona")}
        {p.get("semaforo")} · Score {p.get("score")}
        
        💰 {int(float(p.get("last_price",0))):,} €
        
        📍 {p.get("direccion")}
        🏠 {p.get("m2")} m² · {p.get("habitaciones")} hab  
        ⏳ {p.get("days_on_market")} días
        
        🔗 [Ver anuncio]({p.get("enlace")})
        """)