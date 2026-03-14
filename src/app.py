"""
AgriPulse Argentina — Plataforma de Inteligencia Comercial
Nutrien Ag Solutions Argentina
Versión 2.0 | Stack: Streamlit 1.55 · Plotly 6.x · Pandas 2.3
"""

import io
import re
import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from agripulse_engine import AgriPulseEngine

# ══════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AgriPulse Argentina | Nutrien Ag Solutions",
    page_icon="AP",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
# CSS — SISTEMA DE DISEÑO NUTRIEN
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --g-dark:    #006B3F;
    --g-mid:     #00853F;
    --g-light:   #E8F5EC;
    --g-accent:  #00A34F;
    --gray-50:   #FAFAFA;
    --gray-100:  #F5F6F7;
    --gray-200:  #E8EAED;
    --gray-400:  #9AA0A6;
    --gray-600:  #5F6368;
    --gray-900:  #1A1A1A;
    --white:     #FFFFFF;
    --amber:     #F59E0B;
    --red:       #DC2626;
    --blue:      #1565C0;
    --shadow:    0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 8px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04);
    --radius:    8px;
}

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--gray-100) !important;
    color: var(--gray-900) !important;
}
.stApp { background-color: var(--gray-100) !important; }
[data-testid="stHeader"]     { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: var(--white) !important;
    border-right: 1px solid var(--gray-200) !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] * { color: var(--gray-900) !important; }

/* Sidebar nav radio */
[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--gray-400) !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    gap: 1px !important;
}
[data-testid="stSidebar"] .stRadio label {
    width: 100% !important;
    border-radius: 6px !important;
    padding: 0.48rem 0.75rem !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--gray-600) !important;
    transition: all 0.12s ease !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background-color: var(--g-light) !important;
    color: var(--g-dark) !important;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:has(input:checked) + p,
[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div {
    color: var(--g-dark) !important;
}

/* Sidebar expanders */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid var(--gray-200) !important;
    border-radius: 6px !important;
    background: var(--gray-50) !important;
    box-shadow: none !important;
}

/* ── MAIN CONTAINER ── */
section[data-testid="stMainBlockContainer"],
.main .block-container {
    padding-top: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ── PAGE HEADER ── */
.page-header {
    padding: 0.5rem 0 1.25rem 0;
    border-bottom: 2px solid var(--g-dark);
    margin-bottom: 1.5rem;
}
.page-title {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: var(--g-dark) !important;
    margin: 0 0 0.25rem 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
}
.page-subtitle {
    font-size: 0.82rem !important;
    color: var(--gray-600) !important;
    margin: 0 !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
}
.page-desc {
    font-size: 0.9rem;
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0.6rem 0 0 0;
}

/* ── SECTION HEADERS (in-page sub-headers) ── */
.section-header {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--gray-900);
    margin: 1.4rem 0 0.65rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--gray-200);
    display: block;
}
/* Keep old class working */
.section-title  { font-size: 0.95rem; font-weight: 600; color: var(--gray-900);
                  margin: 1.2rem 0 0.5rem 0; padding-bottom: 0.3rem;
                  border-bottom: 1px solid var(--gray-200); display: block; }
.section-subtitle { font-size: 0.82rem; color: var(--gray-600); margin-bottom: 1rem; }

/* ── FILTER LABEL (above inputs) ── */
.filter-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--gray-600);
    margin-bottom: 0.3rem;
    display: block;
}

/* ── KPI CARDS ── */
.kpi-box {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    min-height: 96px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: var(--shadow);
    box-sizing: border-box;
}
.kpi-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--g-dark);
    line-height: 1.1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-label {
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--gray-600);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 0.35rem;
}
.kpi-sub {
    font-size: 0.73rem;
    color: var(--gray-400);
    margin-top: 0.12rem;
    font-weight: 400;
}

/* ── CONTENT CARDS ── */
.ap-card {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}

/* ── SCORE COMPONENT CARDS (Priority Score explainer) ── */
.score-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin: 1rem 0;
}
.score-comp-card {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-left: 4px solid var(--g-mid);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow);
}
.score-comp-name  { font-size: 0.97rem; font-weight: 700; color: var(--gray-900); margin-bottom: 0.3rem; }
.score-comp-desc  { font-size: 0.84rem; color: var(--gray-600); line-height: 1.55; }
.score-comp-weight{
    font-size: 0.84rem; font-weight: 800; color: var(--white);
    margin-top: 0.5rem; background: var(--g-mid);
    display: inline-block; padding: 2px 10px; border-radius: 20px;
}

/* ── CULTIVO PILLS SELECTOR (st.pills) ── */
/* Pill base — no seleccionado */
[data-testid="stMainBlockContainer"] [data-testid="stPills"] [data-baseweb="tag"] {
    border: 1.5px solid var(--gray-200) !important;
    border-radius: 8px !important;
    background: var(--white) !important;
    color: var(--gray-900) !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.42rem 1.1rem !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stPills"] [data-baseweb="tag"]:hover {
    border-color: var(--g-mid) !important;
    background: rgba(0,107,63,0.05) !important;
    color: var(--g-dark) !important;
}
/* Pill seleccionado — verde claro */
[data-testid="stMainBlockContainer"] [data-testid="stPills"] [aria-selected="true"][data-baseweb="tag"] {
    background: rgba(0,107,63,0.12) !important;
    border: 2px solid var(--g-dark) !important;
    color: var(--g-dark) !important;
    font-weight: 700 !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stPills"] [aria-selected="true"][data-baseweb="tag"]:hover {
    background: rgba(0,107,63,0.18) !important;
}

/* ── INPUTS — BORDE VISIBLE ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border: 1.5px solid var(--gray-200) !important;
    border-radius: 6px !important;
    background: var(--white) !important;
    transition: border-color 0.12s ease !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: var(--g-mid) !important;
    box-shadow: 0 0 0 3px rgba(0,133,63,0.08) !important;
}
.stNumberInput > div > div,
.stTextInput > div > div,
.stDateInput > div > div {
    border: 1.5px solid var(--gray-200) !important;
    border-radius: 6px !important;
}
.stNumberInput > div > div:focus-within,
.stTextInput > div > div:focus-within {
    border-color: var(--g-mid) !important;
    box-shadow: 0 0 0 3px rgba(0,133,63,0.08) !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
    border: 1px solid var(--gray-200) !important;
    border-radius: var(--radius) !important;
    background: var(--white) !important;
}
[data-testid="stExpander"]:hover { border-color: var(--g-mid) !important; }

/* ── TABS (sub-tabs within modules) ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    padding: 0;
    border-bottom: 2px solid var(--gray-200);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--gray-600);
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    padding: 0.5rem 1.1rem;
    font-weight: 500;
    font-size: 0.85rem;
    margin-bottom: -2px;
    transition: all 0.12s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--g-dark);
    background: var(--g-light);
}
.stTabs [aria-selected="true"] {
    color: var(--g-dark) !important;
    border-bottom: 2px solid var(--g-dark) !important;
    font-weight: 700 !important;
    background: transparent !important;
}

/* ── DATAFRAMES ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--gray-200) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}

/* ── INFO / ALERT BOXES ── */
.info-box {
    background: var(--g-light);
    border-left: 3px solid var(--g-mid);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 0.85rem 1rem;
    margin: 0.75rem 0;
    font-size: 0.875rem;
    color: var(--gray-900);
    line-height: 1.6;
}
.alert-box {
    background: #FFFBEB;
    border-left: 3px solid var(--amber);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 0.85rem 1rem;
    margin: 0.75rem 0;
    font-size: 0.875rem;
    color: var(--gray-900);
}

/* ── BADGES ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.71rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-green { background: rgba(0,107,63,0.1); color: var(--g-dark); border: 1px solid rgba(0,107,63,0.2); }
.badge-amber { background: rgba(245,158,11,0.1); color: #92400E; border: 1px solid rgba(245,158,11,0.25); }
.badge-red   { background: rgba(220,38,38,0.1); color: #991B1B; border: 1px solid rgba(220,38,38,0.2); }
.badge-blue  { background: rgba(21,101,192,0.1); color: var(--blue); border: 1px solid rgba(21,101,192,0.2); }

/* ── BUTTONS ── */
.stButton > button {
    background: var(--g-mid) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    padding: 0.42rem 1.1rem !important;
    transition: background 0.12s ease !important;
}
.stButton > button:hover { background: var(--g-dark) !important; }
.stDownloadButton > button {
    background: var(--white) !important;
    color: var(--g-dark) !important;
    border: 1.5px solid var(--g-dark) !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: var(--g-dark) !important;
    color: var(--white) !important;
}

/* ── FOOTER ── */
.ap-footer {
    margin-top: 2.5rem;
    padding: 1rem 1.5rem;
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    font-size: 0.74rem;
    color: var(--gray-600);
    text-align: center;
    line-height: 1.8;
}
.source-tag {
    background: var(--gray-100);
    border: 1px solid var(--gray-200);
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 0.7rem;
    font-family: monospace;
    display: inline-block;
    margin: 1px;
}

/* ── STYLED HTML TABLES (SaaS style) ── */
.saas-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.82rem;
    font-family: 'Inter', sans-serif;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    overflow: hidden;
}
.saas-table thead th {
    background: var(--gray-100);
    font-size: 0.69rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--gray-600);
    padding: 0.55rem 0.9rem;
    border-bottom: 2px solid var(--gray-200);
    text-align: left;
    white-space: nowrap;
}
.saas-table tbody td {
    padding: 0.42rem 0.9rem;
    border-bottom: 1px solid var(--gray-200);
    color: var(--gray-900);
    vertical-align: middle;
}
.saas-table tbody tr:last-child td { border-bottom: none; }
.saas-table tbody tr:nth-child(odd)  td { background: var(--white); }
.saas-table tbody tr:nth-child(even) td { background: var(--gray-50); }
.saas-table tbody tr:hover td { background: rgba(0,107,63,0.04) !important; }

/* ── CLIMA DASHBOARD CONTROLS PANEL ── */
.clima-controls {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 1rem 1.25rem 0.75rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}

</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# ENGINE + CACHE
# ══════════════════════════════════════════════════════════
@st.cache_resource
def get_engine():
    return AgriPulseEngine()

engine = get_engine()
today_str = datetime.date.today().strftime("%d/%m/%Y")
_DATA_DIR = Path(__file__).parent.parent / 'data'

@st.cache_data(ttl=3600)
def load_market(cultivo, provincia):
    return engine.get_market_potential(cultivo_filter=cultivo, provincia_filter=provincia)  # v2

@st.cache_data(ttl=3600)
def load_ratios():
    return engine.get_price_ratios()

@st.cache_data(ttl=86400)
def load_ciafa():
    return engine.get_ciafa_consumption()

@st.cache_data(ttl=900)
def load_weather(lat, lon):
    return engine.get_weather_intel(lat, lon)

@st.cache_data(ttl=7200)
def load_territorial(cultivo, periodo):
    return engine.get_territorial_classification(cultivo=cultivo, periodo_anios=periodo)  # v2

@st.cache_data(ttl=7200)
def load_brecha(cultivo):
    return engine.get_technology_gap(cultivo=cultivo)

@st.cache_data(ttl=7200)
def load_priority_score(cultivo):
    return engine.get_commercial_priority_score(cultivo=cultivo)  # v2

@st.cache_data(ttl=7200)
def load_climate_corr(cultivo):
    return engine.get_climate_production_correlation(cultivo=cultivo)

@st.cache_data(ttl=3600)
def load_price_history(grain, fert):
    return engine.get_price_history(grain=grain, fertilizer=fert)

@st.cache_data(ttl=86400)
def load_bcr():
    return engine.get_bcr_campaign_data()


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def render_page_header(title: str, subtitle: str = "", desc: str = ""):
    """Cabecera de módulo consistente en toda la app."""
    sub_html  = f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ""
    desc_html = f'<p class="page-desc">{desc}</p>' if desc else ""
    st.markdown(f"""
    <div class="page-header">
        <h2 class="page-title">{title}</h2>
        {sub_html}
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def render_cultivo_buttons(key: str = "cultivo_btn", default: str = "Soja") -> str:
    """Selector de cultivo como pills/tarjetas nativas (st.pills). Sin radio buttons.
    Retorna 'Todos' cuando el usuario selecciona 'Todos los cultivos'.
    """
    _OPTIONS = ["Todos los cultivos", "Soja", "Maíz", "Trigo", "Girasol"]
    _default = default if default in _OPTIONS else "Soja"
    selected = st.pills(
        "Cultivo",
        _OPTIONS,
        default=_default,
        selection_mode="single",
        key=key,
        label_visibility="visible",
    )
    # Fallback si queda None (deselección accidental)
    if selected is None:
        selected = _default
    return "Todos" if selected == "Todos los cultivos" else selected


def section_header(text: str):
    st.markdown(f'<p class="section-header">{text}</p>', unsafe_allow_html=True)


def render_styled_table(df: pd.DataFrame, max_rows: int = 50) -> None:
    """Render a DataFrame as a SaaS-style HTML table (zebra rows, clean headers)."""
    df = df.head(max_rows)
    header_html = "".join(f"<th>{c}</th>" for c in df.columns)
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{v}</td>" for v in row.values)
        rows_html += f"<tr>{cells}</tr>"
    st.markdown(
        f'<div style="overflow-x:auto;margin:0.4rem 0 0.8rem 0;">'
        f'<table class="saas-table"><thead><tr>{header_html}</tr></thead>'
        f'<tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════
# SIDEBAR — NAVEGACIÓN
# ══════════════════════════════════════════════════════════
_NAV_OPTIONS = [
    "Priority Score",
    "Potencial de Mercado",
    "Evolución y Proyección",
    "Clima",
    "Oportunidad",
]

with st.sidebar:
    st.markdown("""
    <div style="padding: 1.1rem 0.9rem 0.5rem 0.9rem;">
        <div style="font-size:1.85rem; font-weight:900; color:#006B3F; letter-spacing:-1px; line-height:1;">NUTRIEN</div>
        <div style="font-size:0.68rem; color:#5F6368; letter-spacing:0.12em; text-transform:uppercase; margin-top:3px;">Ag Solutions Argentina</div>
        <div style="margin-top:0.5rem; font-size:0.65rem; font-weight:600; color:#00853F;
                    background:#E8F5EC; border-radius:4px; display:inline-block; padding:2px 8px;">
            AgriPulse v2.0
        </div>
        <div style="margin-top:0.8rem; padding-top:0.7rem; border-top:1px solid #E8EDEA;">
            <div style="font-size:0.73rem; color:#3C3C3C; line-height:1.5; font-weight:500;">
                Desarrollado por <strong style="font-weight:700;">José Antonio Sotomayor</strong>
            </div>
            <div style="font-size:0.67rem; color:#5F6368; line-height:1.4; margin-top:2px;">
                Proceso de selección<br>Analista Sr. Campaign &amp; Data Analytics
            </div>
            <a href="https://www.linkedin.com/in/joseantoniosotomayor/" target="_blank"
               rel="noopener noreferrer"
               style="display:inline-flex; align-items:center; gap:6px; margin-top:9px;
                      background:#0A66C2; color:#fff; text-decoration:none;
                      font-size:0.72rem; font-weight:600; border-radius:5px;
                      padding:5px 11px; line-height:1;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
                Ver LinkedIn
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    _page = st.radio("Módulos", _NAV_OPTIONS, index=0, key="sidebar_nav")

    st.divider()

    with st.expander("Glosario"):
        st.markdown("""
**GDD** — Grados Día de Desarrollo. Determina estadio fenológico.

**Ratio** — kg grano / kg fertilizante. Ratio bajo = mejor momento de compra.

**MAP** — Fosfato Monoamónico (11-52-0).

**MOP** — Cloruro de Potasio (0-0-60).

**SIIA** — Sistema Integrado de Información Agropecuaria (MAGyP).

**BCR** — Bolsa de Comercio de Rosario.

**CIAFA** — Cámara de la Industria Argentina de Fertilizantes.

**CAGR** — Tasa de crecimiento anual compuesta.

**ENSO** — El Niño-Oscilación del Sur.
        """)

    with st.expander("Fuentes"):
        fuentes = [
            ("Superficies", "SIIA / MAGyP"),
            ("Dosis técnicas", "INTA EEA Marcos Juárez"),
            ("Clima", "NASA POWER API"),
            ("Precios fert.", "CIAFA / Mar 2025"),
            ("Precios granos", "MATBA-ROFEX"),
            ("Campaña", "BCR 2024/25"),
            ("ENSO", "NOAA CPC"),
        ]
        for label, val in fuentes:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:3px 0;'
                f'border-bottom:1px solid #E8EAED;font-size:0.72rem;">'
                f'<span style="font-weight:600;color:#1A1A1A;">{label}</span>'
                f'<span style="color:#5F6368;">{val}</span></div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '<div style="padding:0.7rem 0.9rem;font-size:0.65rem;color:#9AA0A6;">Datos: Marzo 2025</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════
# HEADER FIJO
# ══════════════════════════════════════════════════════════
def app_header():
    st.markdown(f"""
    <div style="background:var(--white);padding:0.9rem 1.5rem;
                border-bottom:2px solid #006B3F;margin-bottom:1.5rem;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;
                            text-transform:uppercase;color:#5F6368;margin-bottom:2px;">
                    NUTRIEN AG SOLUTIONS
                </div>
                <div style="font-size:1.2rem;font-weight:800;color:#006B3F;line-height:1;">
                    AgriPulse Argentina
                </div>
                <div style="font-size:0.8rem;color:#5F6368;margin-top:2px;">
                    Plataforma de Inteligencia Comercial
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;font-weight:600;color:#00853F;
                            background:#E8F5EC;border-radius:6px;padding:4px 12px;
                            border:1px solid #00853F;">
                    Campaña 2024/25
                </div>
                <div style="font-size:0.68rem;color:#9AA0A6;margin-top:4px;">{today_str}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

app_header()


# ══════════════════════════════════════════════════════════
# MÓDULO 1 — PRIORITY SCORE
# ══════════════════════════════════════════════════════════
if _page == "Priority Score":

    render_page_header(
        "Score de Prioridad Comercial",
        "Ranking 0–100 por departamento · 6 dimensiones comerciales integradas",
        "Identifica y ordena los territorios donde el esfuerzo comercial genera mayor retorno: "
        "combina demanda potencial de insumos, expansión de área, brecha tecnológica, "
        "relación precio insumo/grano, condición climática y tendencia de rendimiento."
    )

    # ── CULTIVO (botones) ──
    cultivo_global = render_cultivo_buttons("t1_cultivo", "Soja")

    # ── Explainer ──
    with st.expander("¿Qué es el Priority Score y cómo se usa?"):
        st.markdown("""
**El Priority Score indica al vendedor dónde focalizar el esfuerzo comercial de forma objetiva.**
Se construye combinando 6 dimensiones ponderadas:
        """)
        st.markdown("""
<div class="score-grid">
  <div class="score-comp-card">
    <div class="score-comp-name">Demanda potencial</div>
    <div class="score-comp-desc">Toneladas de fertilizante absorbibles: ha × dosis INTA</div>
    <div class="score-comp-weight">25%</div>
  </div>
  <div class="score-comp-card">
    <div class="score-comp-name">Clasificación territorial</div>
    <div class="score-comp-desc">Si la superficie está creciendo (EXPANSIÓN) o cayendo (CONTRACCIÓN)</div>
    <div class="score-comp-weight">20%</div>
  </div>
  <div class="score-comp-card">
    <div class="score-comp-name">Brecha tecnológica</div>
    <div class="score-comp-desc">Cuánto rinde la zona bajo el potencial INTA — más brecha = más upside</div>
    <div class="score-comp-weight">20%</div>
  </div>
  <div class="score-comp-card">
    <div class="score-comp-name">Ratio insumo/grano</div>
    <div class="score-comp-desc">Si el fertilizante está caro o barato en términos de grano (percentil histórico)</div>
    <div class="score-comp-weight">15%</div>
  </div>
  <div class="score-comp-card">
    <div class="score-comp-name">Clima / ENSO</div>
    <div class="score-comp-desc">Condición climática actual y efecto histórico sobre rendimiento</div>
    <div class="score-comp-weight">10%</div>
  </div>
  <div class="score-comp-card">
    <div class="score-comp-name">Tendencia rendimiento</div>
    <div class="score-comp-desc">Si los rindes de los últimos 5 años subieron o bajaron</div>
    <div class="score-comp-weight">10%</div>
  </div>
</div>
        """, unsafe_allow_html=True)
        st.markdown("""
**Lectura del score:**
- **≥ 75** — Prioridad ALTA. Alta demanda, tecnología rezagada, momento favorable.
- **50–74** — Prioridad MEDIA. Al menos un factor limita el potencial.
- **< 50** — Prioridad BAJA. Zona madura, saturada o con ratio desfavorable.

Podés ajustar los pesos en "Personalizar pesos" para reflejar la estrategia de tu equipo.
        """)

    _TODOS = ["Soja", "Maíz", "Trigo", "Girasol"]
    with st.spinner("Calculando scores comerciales..."):
        try:
            if cultivo_global == "Todos":
                _frames, _metas = [], []
                for _c in _TODOS:
                    _df, _m = load_priority_score(_c)
                    if not _df.empty:
                        _frames.append(_df)
                        _metas.append(_m)
                if not _frames:
                    st.info("Sin datos.")
                    st.stop()
                _num = score_df_base = pd.concat(_frames)
                _num_cols = [c for c in _num.select_dtypes('number').columns if c != 'rank']
                score_df_base = (_num.groupby(['departamento', 'provincia', 'lat', 'lon'], as_index=False)
                                 .agg({c: 'mean' for c in _num_cols if c in _num.columns}))
                score_df_base['clasificacion'] = (
                    pd.concat(_frames).groupby(['departamento', 'provincia'])['clasificacion']
                    .agg(lambda x: x.value_counts().index[0]).reset_index()['clasificacion'].values
                    if len(_frames) > 0 else 'MADUREZ'
                )
                score_meta = {'percentil_ratio': int(sum(m.get('percentil_ratio', 50) for m in _metas) / len(_metas))}
                _arg = pd.concat(_frames).groupby(['departamento', 'provincia'])['argumento_venta'].first().reset_index()
                score_df_base = score_df_base.merge(_arg, on=['departamento', 'provincia'], how='left')
            else:
                score_df_base, score_meta = load_priority_score(cultivo_global)
        except Exception as e:
            st.error(f"Error al calcular Priority Score: {e}")
            st.stop()

    if score_df_base.empty:
        st.info("Sin datos para esta selección.")
        st.stop()

    # ── FILTROS ──
    ps_f1, ps_f2, ps_f3 = st.columns([2, 2, 2])
    with ps_f1:
        _provs_ps = ["Todas"] + sorted(score_df_base['provincia'].unique().tolist())
        prov_ps = st.selectbox("Provincia", _provs_ps, key="ps_prov")
    with ps_f2:
        min_score_ps = st.slider("Score mínimo", 0, 90, 0, 5, key="ps_min")
    with ps_f3:
        _cls_opts = ["Todas", "EXPANSIÓN", "MADUREZ", "CONTRACCIÓN", "EMERGENTE"]
        cls_filter_ps = st.selectbox("Clasificación territorial", _cls_opts, key="ps_cls")

    with st.expander("Personalizar pesos del score (deben sumar 100%)"):
        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            w_dem   = st.number_input("Demanda (%)",    0, 100, 25, 5, key="w_dem")
            w_ratio = st.number_input("Ratio (%)",      0, 100, 15, 5, key="w_ratio")
        with wc2:
            w_terr  = st.number_input("Territorial (%)", 0, 100, 20, 5, key="w_terr")
            w_clima = st.number_input("Clima (%)",       0, 100, 10, 5, key="w_clima")
        with wc3:
            w_brech = st.number_input("Brecha tech. (%)", 0, 100, 20, 5, key="w_brech")
            w_tend  = st.number_input("Tendencia (%)",    0, 100, 10, 5, key="w_tend")
        total_w = w_dem + w_terr + w_brech + w_ratio + w_clima + w_tend
        if total_w != 100:
            st.warning(f"Los pesos suman {total_w}%. Deben sumar 100% para aplicar. Se usan los pesos base.")
            weights = (0.25, 0.20, 0.20, 0.15, 0.10, 0.10)
        else:
            weights = (w_dem/100, w_terr/100, w_brech/100, w_ratio/100, w_clima/100, w_tend/100)
            st.success(f"Pesos personalizados aplicados (suma = {total_w}%)")

    # ── Aplicar pesos y filtros ──
    score_df = score_df_base.copy()
    score_df['score_final'] = (
        score_df['score_demanda']     * weights[0] +
        score_df['score_territorial'] * weights[1] +
        score_df['score_brecha']      * weights[2] +
        score_df['score_ratio']       * weights[3] +
        score_df['score_clima']       * weights[4] +
        score_df['score_tendencia']   * weights[5]
    ).round(1)
    score_df = score_df.sort_values('score_final', ascending=False).reset_index(drop=True)
    score_df['rank'] = score_df.index + 1

    if prov_ps != "Todas":
        score_df = score_df[score_df['provincia'] == prov_ps]
    if min_score_ps > 0:
        score_df = score_df[score_df['score_final'] >= min_score_ps]
    if cls_filter_ps != "Todas":
        score_df = score_df[score_df['clasificacion'] == cls_filter_ps]

    if score_df.empty:
        st.info("Sin departamentos con los filtros seleccionados.")
        st.stop()

    # ── KPIs ──
    kc1, kc2, kc3, kc4 = st.columns(4)
    top_row   = score_df.iloc[0]
    avg_score = score_df['score_final'].mean()
    top_score = score_df['score_final'].max()
    n_deptos  = len(score_df)
    ratio_pct = score_meta['percentil_ratio']

    if ratio_pct < 30:
        momento_badge = '<span class="badge badge-green">Momento COMPRA</span>'
    elif ratio_pct < 60:
        momento_badge = '<span class="badge badge-amber">Momento NEUTRO</span>'
    else:
        momento_badge = '<span class="badge badge-red">Ratio ELEVADO</span>'

    with kc1:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{n_deptos}</div>
            <div class="kpi-label">Departamentos</div>
            <div class="kpi-sub">{cultivo_global} · filtro activo</div>
        </div>""", unsafe_allow_html=True)
    with kc2:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{avg_score:.1f}</div>
            <div class="kpi-label">Score promedio</div>
            <div class="kpi-sub">escala 0–100</div>
        </div>""", unsafe_allow_html=True)
    with kc3:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{top_score:.0f}</div>
            <div class="kpi-label">Score máximo</div>
            <div class="kpi-sub">{top_row['departamento']}, {top_row['provincia']}</div>
        </div>""", unsafe_allow_html=True)
    with kc4:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value" style="font-size:0.95rem;margin-top:0.2rem;">{momento_badge}</div>
            <div class="kpi-label">Momento de mercado</div>
            <div class="kpi-sub">Ratio percentil {ratio_pct}° histórico</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── MAPA + RANKING (siempre lado a lado) ──
    col_map, col_table = st.columns([6, 4], gap="medium")

    with col_map:
        section_header("Mapa de Prioridad")
        fig_map = px.scatter_map(
            score_df,
            lat='lat', lon='lon',
            size='score_final',
            color='score_final',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100],
            size_max=28,
            zoom=4,
            center={'lat': -34.0, 'lon': -63.0},
            map_style='carto-positron',
            hover_name='departamento',
            hover_data={
                'provincia': True,
                'score_final': ':.1f',
                'clasificacion': True,
                'demanda_total_tn': ':,.0f',
                'lat': False, 'lon': False,
            },
            labels={'score_final': 'Score', 'demanda_total_tn': 'Demanda (tn)', 'clasificacion': 'Clasificación'},
            title=f"Prioridad Comercial — {cultivo_global}",
        )
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            template='plotly_white', height=480,
            margin=dict(l=0, r=0, t=36, b=0),
            coloraxis_colorbar=dict(title="Score", thickness=10, len=0.6),
        )
        st.plotly_chart(fig_map, width='stretch')

    with col_table:
        section_header("Ranking de Departamentos")

        # ── Búsqueda rápida por departamento ──
        _srch = st.text_input(
            "Buscar departamento", placeholder="Ej: Marcos Juárez, General…",
            key="ps_search", label_visibility="collapsed",
        )

        # ── Construir DataFrame para la tabla ──
        table_df = score_df[['rank', 'departamento', 'provincia', 'score_final',
                              'demanda_total_tn', 'clasificacion', 'brecha_pct']].copy()
        table_df['brecha_pct'] = table_df['brecha_pct'].fillna(0)

        if _srch:
            table_df = table_df[
                table_df['departamento'].str.contains(_srch, case=False, na=False)
            ]

        st.dataframe(
            table_df,
            column_config={
                'rank': st.column_config.NumberColumn(
                    '#', width='small', format='%d',
                ),
                'departamento': st.column_config.TextColumn(
                    'Departamento', width='medium',
                ),
                'provincia': st.column_config.TextColumn(
                    'Prov.', width='small',
                ),
                'score_final': st.column_config.ProgressColumn(
                    'Score', min_value=0, max_value=100,
                    format='%.1f', width='medium',
                ),
                'demanda_total_tn': st.column_config.NumberColumn(
                    'Demanda (tn)', format='%,.0f', width='medium',
                ),
                'clasificacion': st.column_config.TextColumn(
                    'Clasificación', width='small',
                ),
                'brecha_pct': st.column_config.NumberColumn(
                    'Brecha%', format='%.0f%%', width='small',
                ),
            },
            height=462,
            width='stretch',
            hide_index=True,
        )
        st.markdown(
            '<p style="font-size:0.67rem;color:#9AA0A6;margin-top:4px;">'
            '↑ Haz clic en cualquier cabecera para ordenar · '
            'Usa los filtros superiores para acotar provincias, score o clasificación</p>',
            unsafe_allow_html=True,
        )

    # ── DETALLE DE DEPARTAMENTO ──
    st.markdown("---")
    section_header("Detalle de Departamento")

    depto_options = score_df['departamento'].tolist()
    depto_sel = st.selectbox("Seleccionar departamento", options=depto_options, index=0)
    row_sel   = score_df[score_df['departamento'] == depto_sel].iloc[0]

    dcol1, dcol2 = st.columns([1, 1])

    with dcol1:
        fig_radar = go.Figure(go.Scatterpolar(
            r=[float(row_sel.get(c, 50)) for c in
               ['score_demanda','score_territorial','score_brecha','score_ratio','score_clima','score_tendencia']],
            theta=['Demanda', 'Territorial', 'Brecha Tech.', 'Ratio Mercado', 'Clima', 'Tendencia'],
            fill='toself',
            fillcolor='rgba(0,107,63,0.12)',
            line=dict(color='#006B3F', width=2),
            name=depto_sel,
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9)),
                angularaxis=dict(tickfont=dict(size=10)),
            ),
            paper_bgcolor='rgba(0,0,0,0)', height=320,
            margin=dict(l=40, r=40, t=40, b=20),
            title=dict(text=f"Perfil — {depto_sel}", font=dict(size=12)),
            showlegend=False,
        )
        st.plotly_chart(fig_radar, width='stretch')

    with dcol2:
        argumento = row_sel.get('argumento_venta', '')
        cls_badge = {
            'EXPANSIÓN': 'badge-green', 'MADUREZ': 'badge-amber',
            'CONTRACCIÓN': 'badge-red', 'EMERGENTE': 'badge-blue',
        }.get(str(row_sel.get('clasificacion', '')), 'badge-amber')

        st.markdown(f"""
        <div class="ap-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
                <strong style="font-size:1rem;">{depto_sel}</strong>
                <span class="badge {cls_badge}">{row_sel.get('clasificacion','—')}</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-bottom:0.8rem;">
                <div>
                    <div class="kpi-label">Score Final</div>
                    <div style="font-size:1.5rem;font-weight:800;color:#006B3F;">{row_sel['score_final']:.1f}<span style="font-size:0.9rem;font-weight:500;">/100</span></div>
                </div>
                <div>
                    <div class="kpi-label">Ranking</div>
                    <div style="font-size:1.5rem;font-weight:800;">#{int(row_sel['rank'])}</div>
                </div>
                <div>
                    <div class="kpi-label">Demanda potencial</div>
                    <div style="font-size:0.95rem;font-weight:600;">{row_sel.get('demanda_total_tn',0):,.0f} tn</div>
                </div>
                <div>
                    <div class="kpi-label">Brecha tecnológica</div>
                    <div style="font-size:0.95rem;font-weight:600;">{row_sel.get('brecha_pct',0):.0f}%</div>
                </div>
            </div>
            <div class="info-box" style="margin:0;">
                <strong>Argumento de venta:</strong><br>{argumento}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── EXPORTAR ──
    st.markdown("---")
    export_df = score_df[['rank','departamento','provincia','score_final',
                           'score_demanda','score_territorial','score_brecha',
                           'score_ratio','score_clima','score_tendencia',
                           'demanda_total_tn','clasificacion','brecha_pct','argumento_venta']].copy()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Priority Score')
    st.download_button(
        "Exportar a Excel",
        data=buffer.getvalue(),
        file_name=f"agripulse_priority_{cultivo_global.lower()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ══════════════════════════════════════════════════════════
# MÓDULO 2 — POTENCIAL DE MERCADO
# ══════════════════════════════════════════════════════════
elif _page == "Potencial de Mercado":

    render_page_header(
        "Potencial de Mercado",
        "Demanda potencial de fertilizantes por departamento",
        "Superficie sembrada × dosis técnica INTA. El tamaño de burbuja representa toneladas de fertilizante; "
        "el color, el valor en millones de USD."
    )

    # ── FILTROS ──
    fa_col1, fa_col2, fa_col3, fa_col4 = st.columns([2, 2, 2, 2])
    with fa_col1:
        cultivo_mkt = render_cultivo_buttons("mkt_cultivo_btn", "Soja")
    with fa_col2:
        _sup_df = engine._load_sup()
        prov_opts_mkt = ["Todas"] + sorted(_sup_df['provincia'].unique().tolist())
        prov_mkt = st.selectbox("Provincia", prov_opts_mkt, index=0, key="mkt_prov")
    with fa_col3:
        fert_opts = ["Todos"] + list(engine.FERTILIZER_PRICES.keys())
        fert_mkt = st.selectbox("Fertilizante", fert_opts, key="mkt_fert")
    with fa_col4:
        show_nutrien    = st.checkbox("Sucursales Nutrien", value=True, key="mkt_nutrien")
        show_competitors = st.checkbox("Competidores", value=False, key="mkt_comp")

    # ── DOSIS AJUSTABLES ──
    _cultivo_dosis = cultivo_mkt if cultivo_mkt in engine.TECH_DOSAGE else 'Soja'
    _inta = engine.TECH_DOSAGE[_cultivo_dosis]
    _dk = {f: f"dose_{_cultivo_dosis}_{f}" for f in ['Urea', 'MAP', 'MOP']}
    for f in ['Urea', 'MAP', 'MOP']:
        if _dk[f] not in st.session_state:
            st.session_state[_dk[f]] = int(_inta.get(f, 0))

    with st.expander(f"Ajustar dosis técnicas — {_cultivo_dosis} (kg/ha) · Por defecto: INTA EEA Marcos Juárez"):
        _dc1, _dc2, _dc3, _dc4 = st.columns(4)
        with _dc1:
            st.slider("Urea (kg/ha)", 0, 300, step=10, key=_dk['Urea'])
        with _dc2:
            st.slider("MAP (kg/ha)", 0, 200, step=10, key=_dk['MAP'])
        with _dc3:
            st.slider("MOP (kg/ha)", 0, 150, step=10, key=_dk['MOP'])
        with _dc4:
            st.markdown("<br>", unsafe_allow_html=True)
            def _cb_reset_dose(_dk=_dk, _inta=_inta):
                for f in ['Urea', 'MAP', 'MOP']:
                    st.session_state[_dk[f]] = int(_inta.get(f, 0))
            st.button("Restaurar INTA", key=f"reset_dose_{_cultivo_dosis}",
                      on_click=_cb_reset_dose)
        _dosis_p = {f: st.session_state[_dk[f]] for f in ['Urea', 'MAP', 'MOP']}
        if any(_dosis_p[f] != _inta.get(f, 0) for f in ['Urea', 'MAP', 'MOP']):
            st.info(f"Dosis activas — Urea: {_dosis_p['Urea']} kg/ha · MAP: {_dosis_p['MAP']} kg/ha · MOP: {_dosis_p['MOP']} kg/ha")
    _dosis_activas = {f: st.session_state[_dk[f]] for f in ['Urea', 'MAP', 'MOP']}

    with st.spinner("Cargando datos de mercado..."):
        if cultivo_mkt == "Todos":
            _parts = [load_market(c, prov_mkt)[0] for c in ["Soja", "Maíz", "Trigo", "Girasol"]]
            result_df = pd.concat([p for p in _parts if not p.empty]).reset_index(drop=True)
            map_df = result_df
        else:
            result_df, map_df = load_market(cultivo_mkt, prov_mkt)

    if result_df.empty:
        st.info("Sin datos para esta selección.")
    else:
        result_filt = result_df[result_df['fertilizante'] == fert_mkt].copy() if fert_mkt != "Todos" else result_df.copy()
        for _col in ['dosis_kg_ha', 'demanda_potencial_tn', 'valor_mercado_musd']:
            if _col in result_filt.columns:
                result_filt[_col] = result_filt[_col].astype(float)

        for fert_name, dosis_val in _dosis_activas.items():
            mask = result_filt['fertilizante'] == fert_name
            if mask.any():
                result_filt.loc[mask, 'dosis_kg_ha'] = dosis_val
                result_filt.loc[mask, 'demanda_potencial_tn'] = result_filt.loc[mask, 'area_ha'] * dosis_val / 1000
                price = engine.FERTILIZER_PRICES.get(fert_name, 0)
                result_filt.loc[mask, 'valor_mercado_musd'] = result_filt.loc[mask, 'demanda_potencial_tn'] * price / 1_000_000

        map_filt = (
            result_filt.groupby(['provincia', 'departamento', 'lat', 'lon', 'area_ha'])
            .agg(demanda_total_tn=('demanda_potencial_tn', 'sum'),
                 valor_total_musd=('valor_mercado_musd', 'sum'))
            .reset_index()
        )

        total_dem = result_filt['demanda_potencial_tn'].sum()
        total_val = result_filt['valor_mercado_musd'].sum()
        n_deptos_mkt = map_filt['departamento'].nunique()

        mk1, mk2, mk3, mk4 = st.columns(4)
        with mk1:
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value">{map_filt['area_ha'].sum():,.0f}</div>
                <div class="kpi-label">Hectáreas sembradas</div>
            </div>""", unsafe_allow_html=True)
        with mk2:
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value">{total_dem/1000:,.0f}K</div>
                <div class="kpi-label">Demanda potencial (tn)</div>
            </div>""", unsafe_allow_html=True)
        with mk3:
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value">USD {total_val:.1f}M</div>
                <div class="kpi-label">Valor de mercado</div>
            </div>""", unsafe_allow_html=True)
        with mk4:
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value">{n_deptos_mkt}</div>
                <div class="kpi-label">Departamentos</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        fig_mkt = px.scatter_map(
            map_filt, lat='lat', lon='lon',
            size='demanda_total_tn', color='valor_total_musd',
            color_continuous_scale='Greens', size_max=35,
            zoom=4, center={'lat': -34.0, 'lon': -63.0},
            map_style='carto-positron',
            hover_name='departamento',
            hover_data={'provincia': True, 'demanda_total_tn': ':,.0f',
                        'valor_total_musd': ':.2f', 'area_ha': ':,.0f',
                        'lat': False, 'lon': False},
            labels={'demanda_total_tn': 'Demanda (tn)', 'valor_total_musd': 'Valor (M USD)', 'area_ha': 'Área (ha)'},
            title=f"Potencial de Mercado — {cultivo_mkt} · {fert_mkt}",
        )

        if show_nutrien:
            nutrien_locs = pd.read_csv(_DATA_DIR / 'nutrien_locations.csv')
            # Outer ring (dark green border effect)
            fig_mkt.add_trace(go.Scattermap(
                lat=nutrien_locs['lat'], lon=nutrien_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=22, color='#004D25', symbol='circle', opacity=1.0),
                hoverinfo='skip', showlegend=False,
            ))
            # Inner fill (Nutrien green)
            fig_mkt.add_trace(go.Scattermap(
                lat=nutrien_locs['lat'], lon=nutrien_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=14, color='#00A34F', symbol='circle', opacity=1.0),
                hovertext=nutrien_locs['localidad'], hoverinfo='text', name='Nutrien',
            ))
        if show_competitors:
            comp_locs = pd.read_csv(_DATA_DIR / 'competitor_locations.csv')
            # Outer ring (dark red border effect)
            fig_mkt.add_trace(go.Scattermap(
                lat=comp_locs['lat'], lon=comp_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=22, color='#7C2D12', symbol='circle', opacity=1.0),
                hoverinfo='skip', showlegend=False,
            ))
            # Inner fill (vivid red)
            fig_mkt.add_trace(go.Scattermap(
                lat=comp_locs['lat'], lon=comp_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=14, color='#EF4444', symbol='circle', opacity=1.0),
                hovertext=comp_locs['localidad'], hoverinfo='text', name='Competencia',
            ))

        fig_mkt.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            template='plotly_white', height=460,
            margin=dict(l=0, r=0, t=36, b=0),
        )
        st.plotly_chart(fig_mkt, width='stretch')

        section_header("Top 15 Departamentos por Demanda")
        top15 = (
            map_filt.sort_values('demanda_total_tn', ascending=False)
            .head(15)[['departamento','provincia','area_ha','demanda_total_tn','valor_total_musd']]
            .rename(columns={'departamento':'Departamento','provincia':'Provincia',
                             'area_ha':'Área (ha)','demanda_total_tn':'Demanda (tn)','valor_total_musd':'Valor (M USD)'})
        )
        top15['Área (ha)']     = top15['Área (ha)'].apply(lambda x: f"{x:,.0f}")
        top15['Demanda (tn)']  = top15['Demanda (tn)'].apply(lambda x: f"{x:,.0f}")
        top15['Valor (M USD)'] = top15['Valor (M USD)'].apply(lambda x: f"$ {x:.2f}M")
        render_styled_table(top15)

        if not map_filt.empty:
            top_dept = map_filt.sort_values('demanda_total_tn', ascending=False).iloc[0]
            st.markdown(f"""
            <div class="info-box">
                <strong>Argumento Comercial:</strong><br>
                <strong>{top_dept['departamento']}</strong> ({top_dept['provincia']}) — mayor demanda potencial:
                <strong>{top_dept['demanda_total_tn']:,.0f} tn</strong> valoradas en
                <strong>USD {top_dept['valor_total_musd']:.2f}M</strong>,
                con <strong>{top_dept['area_ha']:,.0f} ha</strong> sembradas de {cultivo_mkt}.
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MÓDULO 3 — EVOLUCIÓN Y PROYECCIÓN
# ══════════════════════════════════════════════════════════
elif _page == "Evolución y Proyección":

    render_page_header(
        "Evolución y Proyección Territorial",
        "Clasificación departamental por CAGR de área sembrada · Proyección 2026/27",
        "Identifica territorios en expansión, madurez, contracción o emergencia a partir del "
        "crecimiento anual compuesto de la superficie sembrada."
    )

    cultivo_global = render_cultivo_buttons("t3_cultivo_btn", "Soja")

    _PERIODO_OPTS = {"Actual": None, "3 años": 3, "5 años": 5}
    periodo_label = st.radio(
        "Período de análisis", options=list(_PERIODO_OPTS.keys()), horizontal=True, index=2,
    )
    periodo_anios = _PERIODO_OPTS[periodo_label]   # None = solo histórico
    show_projection = periodo_anios is not None
    periodo_engine = periodo_anios or 5            # para CAGR/clasificación en el engine

    with st.spinner("Calculando clasificación territorial..."):
        if cultivo_global == "Todos":
            _t_all, _h_all, conteos = [], [], {}
            for _c in ["Soja", "Maíz", "Trigo", "Girasol"]:
                _td, _hd, _cnt = load_territorial(_c, periodo_engine)
                if not _td.empty:
                    _t_all.append(_td)
                    _h_all.append(_hd)
                for k, v in _cnt.items():
                    conteos[k] = conteos.get(k, 0) + v
            terr_df = (pd.concat(_t_all).drop_duplicates(subset=['departamento', 'provincia'])
                       .reset_index(drop=True) if _t_all else pd.DataFrame())
            hist_df = pd.concat(_h_all).reset_index(drop=True) if _h_all else pd.DataFrame()
        else:
            terr_df, hist_df, conteos = load_territorial(cultivo_global, periodo_engine)

    if terr_df.empty:
        st.info("Sin datos de clasificación territorial. Verificar CSVs SIIA.")
    else:
        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
        badge_info = [
            ('EXPANSIÓN', 'badge-green'), ('MADUREZ', 'badge-amber'),
            ('CONTRACCIÓN', 'badge-red'), ('EMERGENTE', 'badge-blue'),
        ]
        for col, (cls, badge_cls) in zip([bcol1, bcol2, bcol3, bcol4], badge_info):
            cnt = conteos.get(cls, 0)
            with col:
                st.markdown(f"""<div class="kpi-box">
                    <div class="kpi-value">{cnt}</div>
                    <div class="kpi-label">{cls}</div>
                    <div class="kpi-sub"><span class="badge {badge_cls}">&nbsp;</span></div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        color_map_terr = {'EXPANSIÓN': '#00A34F', 'MADUREZ': '#f59e0b',
                          'CONTRACCIÓN': '#dc2626', 'EMERGENTE': '#3b82f6'}

        fig_terr = px.scatter_map(
            terr_df, lat='lat', lon='lon',
            size='ha_actual', color='clasificacion',
            color_discrete_map=color_map_terr,
            size_max=35, zoom=4, center={'lat': -34.0, 'lon': -63.0},
            map_style='carto-positron', hover_name='departamento',
            hover_data={'provincia': True, 'clasificacion': True,
                        'cagr_pct': ':.1f', 'ha_actual': ':,.0f',
                        'proj_2026': ':,.0f', 'r2': ':.2f',
                        'lat': False, 'lon': False},
            labels={'cagr_pct': 'CAGR (%)', 'ha_actual': 'Área actual (ha)',
                    'proj_2026': 'Proyección 2026 (ha)', 'r2': 'R²'},
            title=f"Clasificación Territorial — {cultivo_global} · {periodo_label}",
        )
        fig_terr.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            template='plotly_white', height=460,
            margin=dict(l=0, r=0, t=36, b=0),
        )
        st.plotly_chart(fig_terr, width='stretch')

        section_header("Serie Histórica + Proyección por Departamento")
        dept_terr_opts = terr_df['departamento'].tolist()
        if dept_terr_opts:
            dept_terr_sel = st.selectbox("Departamento", options=dept_terr_opts, key="terr_dept_sel")
            dept_row = terr_df[terr_df['departamento'] == dept_terr_sel].iloc[0]
            _dept_mask = (
                (hist_df['departamento'] == dept_terr_sel) &
                (hist_df['provincia'] == dept_row['provincia'])
            )
            if cultivo_global == "Todos":
                # Aggregate across all crops to avoid zigzag multi-crop lines
                dept_hist = (hist_df[_dept_mask]
                             .groupby('año', as_index=False)['sup_sembrada_ha'].sum()
                             .sort_values('año'))
            else:
                dept_hist = hist_df[_dept_mask].sort_values('año')

            if not dept_hist.empty:
                fig_hist = go.Figure()
                last_year = int(dept_hist['año'].max())
                last_val  = float(dept_hist[dept_hist['año'] == last_year]['sup_sembrada_ha'].values[0])

                fig_hist.add_trace(go.Scatter(
                    x=dept_hist['año'], y=dept_hist['sup_sembrada_ha'],
                    mode='lines+markers', name='Superficie histórica',
                    line=dict(color='#006B3F', width=2), marker=dict(size=5),
                ))

                proj_info_str = ""
                if show_projection:
                    # Proyección usando la MISMA ventana que el CAGR para coherencia
                    anio_ini_fit = last_year - periodo_anios
                    period_window = dept_hist[
                        (dept_hist['año'] >= anio_ini_fit) & (dept_hist['año'] <= last_year)
                    ]
                    if len(period_window) >= 2:
                        x_fit = period_window['año'].values.astype(float)
                        y_fit = period_window['sup_sembrada_ha'].values.astype(float)
                        coeffs = np.polyfit(x_fit, y_fit, deg=1)

                        # Años proyectados: N años desde last_year
                        proj_years = list(range(last_year + 1, last_year + periodo_anios + 1))
                        proj_vals  = [max(0.0, float(np.polyval(coeffs, yr))) for yr in proj_years]

                        # IC 95% basado en residuos de toda la serie histórica
                        y_hat_all = np.polyval(coeffs, dept_hist['año'].values.astype(float))
                        ci95 = max(0, round(float(np.std(
                            dept_hist['sup_sembrada_ha'].values.astype(float) - y_hat_all
                        )) * 1.96))

                        # Banda de confianza
                        fig_hist.add_trace(go.Scatter(
                            x=proj_years + proj_years[::-1],
                            y=[v + ci95 for v in proj_vals] + [v - ci95 for v in proj_vals[::-1]],
                            fill='toself', fillcolor='rgba(0,107,63,0.10)',
                            line=dict(color='rgba(0,0,0,0)'), name='IC 95%',
                        ))
                        # Línea de proyección arrancando desde el último dato histórico
                        fig_hist.add_trace(go.Scatter(
                            x=[last_year] + proj_years,
                            y=[last_val] + proj_vals,
                            mode='lines+markers',
                            name=f'Proyección {periodo_label}',
                            line=dict(color='#006B3F', width=2, dash='dash'),
                            marker=dict(size=8, symbol='diamond'),
                        ))
                        proj_fin_year = proj_years[-1]
                        proj_fin_val  = int(proj_vals[-1])
                        proj_info_str = (
                            f" · Proyección {proj_fin_year}: <strong>{proj_fin_val:,} ha</strong>"
                            f" ±{ci95:,}"
                        )

                chart_title_suffix = "" if show_projection else " (solo histórico)"
                fig_hist.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    template='plotly_white', height=320,
                    title=f"{dept_terr_sel} — {cultivo_global} (ha sembradas){chart_title_suffix}",
                    xaxis_title="Campaña", yaxis_title="Hectáreas",
                    legend=dict(orientation='h', y=-0.15),
                    margin=dict(l=0, r=0, t=40, b=0),
                )
                st.plotly_chart(fig_hist, width='stretch')

                r2_val   = dept_row['r2']
                cagr_val = dept_row['cagr_pct']
                cls_val  = dept_row['clasificacion']
                st.markdown(f"""
                <div class="info-box">
                    <strong>{dept_terr_sel}</strong> · Clasificación: <strong>{cls_val}</strong> ·
                    CAGR {periodo_label}: <strong>{cagr_val:+.1f}%</strong> ·
                    R²: <strong>{r2_val:.3f}</strong>{proj_info_str}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Sin datos históricos para este departamento.")

        st.markdown("---")
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            section_header("Top 10 Expansión")
            exp_df = (terr_df[terr_df['clasificacion'] == 'EXPANSIÓN']
                      .nlargest(10, 'cagr_pct')
                      [['departamento','provincia','cagr_pct','ha_actual','proj_2026']])
            if exp_df.empty:
                st.info("Sin departamentos en expansión.")
            else:
                exp_df = exp_df.copy()
                exp_df.columns = ['Depto', 'Prov', 'CAGR (%)', 'Área (ha)', 'Proy. 2026 (ha)']
                exp_df['CAGR (%)']      = exp_df['CAGR (%)'].apply(lambda x: f"+{x:.1f}%")
                exp_df['Área (ha)']     = exp_df['Área (ha)'].apply(lambda x: f"{x:,.0f}")
                exp_df['Proy. 2026 (ha)'] = exp_df['Proy. 2026 (ha)'].apply(lambda x: f"{x:,.0f}")
                render_styled_table(exp_df)

        with tcol2:
            section_header("Top 10 Contracción")
            con_df = (terr_df[terr_df['clasificacion'] == 'CONTRACCIÓN']
                      .nsmallest(10, 'cagr_pct')
                      [['departamento','provincia','cagr_pct','ha_actual','proj_2026']])
            if con_df.empty:
                st.info("Sin departamentos en contracción.")
            else:
                con_df = con_df.copy()
                con_df.columns = ['Depto', 'Prov', 'CAGR (%)', 'Área (ha)', 'Proy. 2026 (ha)']
                con_df['CAGR (%)']      = con_df['CAGR (%)'].apply(lambda x: f"{x:.1f}%")
                con_df['Área (ha)']     = con_df['Área (ha)'].apply(lambda x: f"{x:,.0f}")
                con_df['Proy. 2026 (ha)'] = con_df['Proy. 2026 (ha)'].apply(lambda x: f"{x:,.0f}")
                render_styled_table(con_df)


# ══════════════════════════════════════════════════════════
# MÓDULO 4 — CLIMA
# ══════════════════════════════════════════════════════════
elif _page == "Clima":

    render_page_header(
        "Clima & Producción",
        "Dashboard climático dinámico · NASA POWER + Correlación ENSO–Rendimiento",
        "Explorá distintas zonas y variables climáticas. Los gráficos se actualizan en tiempo real."
    )

    # ── PANEL DE CONTROLES ──
    st.markdown('<div class="clima-controls">', unsafe_allow_html=True)
    cultivo_global = render_cultivo_buttons("t4_cultivo_btn", "Soja")
    cc1, cc2, cc3, cc4, cc5 = st.columns([2, 2, 2, 1, 1], gap="small")
    with cc1:
        zones_list = list(engine.ZONES.keys())
        zona_sel   = st.selectbox("Zona de monitoreo", options=zones_list, key="clima_zona")
    with cc2:
        variable_viz = st.selectbox(
            "Variable climática",
            ["Temperatura + Precipitación", "GDD acumulados", "Humedad relativa"],
            key="clima_var_viz",
        )
    with cc3:
        agg_mode = st.selectbox(
            "Agregación",
            ["Diario", "7 días (media)", "30 días (media)"],
            key="clima_agg",
        )
    with cc4:
        _today_dt    = datetime.date.today()
        _default_from = _today_dt - datetime.timedelta(days=90)
        date_from = st.date_input("Desde", value=_default_from, key="clima_from")
    with cc5:
        date_to = st.date_input("Hasta", value=_today_dt, key="clima_to")
    st.markdown('</div>', unsafe_allow_html=True)

    zona_coords = engine.ZONES[zona_sel]
    lat_w, lon_w = zona_coords['lat'], zona_coords['lon']

    # ── BANNER FENOLÓGICO ──
    _cultivo_feno = ("Maíz" if cultivo_global in ("Todos", None)
                     else (cultivo_global if cultivo_global in engine.ESTADO_ACTUAL_CULTIVOS else "Maíz"))
    _estado_actual = engine.get_estado_fenologico_actual(_cultivo_feno)
    _box_class = "alert-box" if not _estado_actual['ventana_activa'] else "info-box"
    st.markdown(f"""
    <div class="{_box_class}">
        <strong>{cultivo_global} — Estadio actual (Marzo 2026):</strong>
        {_estado_actual['estadio']}<br>
        {_estado_actual['mensaje']}<br>
        <strong>Próxima ventana:</strong> {_estado_actual['proxima_ventana']}
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"Descargando datos climáticos — {zona_sel}..."):
        wx = load_weather(lat_w, lon_w)

    wx_df       = wx['df']
    fuente_str  = wx['fuente']
    fuente_badge = "badge-green" if wx.get('success', False) else "badge-amber"

    # ── FILTRO DE FECHAS ──
    if not wx_df.empty and 'fecha' in wx_df.columns and date_from and date_to:
        wx_df = wx_df[
            (wx_df['fecha'] >= pd.Timestamp(date_from)) &
            (wx_df['fecha'] <= pd.Timestamp(date_to))
        ].copy()

    # ── AGREGACIÓN ──
    if not wx_df.empty and 'fecha' in wx_df.columns:
        if agg_mode == "7 días (media)":
            _num_cols = wx_df.select_dtypes(include='number').columns.tolist()
            wx_df = (wx_df.set_index('fecha')[_num_cols]
                     .resample('7D').mean().reset_index())
        elif agg_mode == "30 días (media)":
            _num_cols = wx_df.select_dtypes(include='number').columns.tolist()
            wx_df = (wx_df.set_index('fecha')[_num_cols]
                     .resample('30D').mean().reset_index())

    # ── KPIs CLIMÁTICOS ──
    wk1, wk2, wk3, wk4, wk5 = st.columns(5)
    with wk1:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{wx['temp_avg']}°C</div>
            <div class="kpi-label">Temp. promedio</div>
            <div class="kpi-sub">{wx['temp_min']}°C / {wx['temp_max']}°C</div>
        </div>""", unsafe_allow_html=True)
    with wk2:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{wx['precip_total']} mm</div>
            <div class="kpi-label">Precipitación total</div>
            <div class="kpi-sub">{wx['dias_lluvia']} días con lluvia</div>
        </div>""", unsafe_allow_html=True)
    with wk3:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{wx['hum_avg']:.0f}%</div>
            <div class="kpi-label">Humedad relativa</div>
            <div class="kpi-sub">promedio período</div>
        </div>""", unsafe_allow_html=True)
    with wk4:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{wx['gdd_acum']:.0f}</div>
            <div class="kpi-label">GDD acumulados</div>
            <div class="kpi-sub">base 10°C</div>
        </div>""", unsafe_allow_html=True)
    with wk5:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value" style="font-size:0.72rem;margin-top:0.3rem;">
                <span class="badge {fuente_badge}">{fuente_str[:28]}</span>
            </div>
            <div class="kpi-label">Fuente de datos</div>
            <div class="kpi-sub">{lat_w:.2f}, {lon_w:.2f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── GRÁFICO DINÁMICO SEGÚN VARIABLE ──
    st.markdown('<div class="ap-card" style="padding:0.75rem 1rem 1rem 1rem;">', unsafe_allow_html=True)
    section_header(f"Serie climática — {zona_sel} · {agg_mode}")

    fig_wx = go.Figure()

    if variable_viz == "Temperatura + Precipitación":
        fig_wx.add_trace(go.Scatter(
            x=wx_df['fecha'], y=wx_df['temp_c'], name='Temperatura (°C)',
            mode='lines', line=dict(color='#ef4444', width=2), yaxis='y1',
        ))
        fig_wx.add_trace(go.Bar(
            x=wx_df['fecha'], y=wx_df['precip_mm'], name='Precipitación (mm)',
            marker_color='rgba(59,130,246,0.55)', yaxis='y2',
        ))
        fig_wx.update_layout(
            yaxis=dict(title="Temperatura (°C)", side='left', color='#ef4444'),
            yaxis2=dict(title="Precipitación (mm)", side='right', overlaying='y', color='#3b82f6'),
            legend=dict(orientation='h', y=1.1),
        )

    elif variable_viz == "GDD acumulados":
        if 'gdd_diario' in wx_df.columns:
            gdd_cum = wx_df['gdd_diario'].cumsum()
        else:
            gdd_cum = pd.Series([wx['gdd_acum'] * (i+1) / len(wx_df) for i in range(len(wx_df))])
        fig_wx.add_trace(go.Scatter(
            x=wx_df['fecha'], y=gdd_cum, name='GDD acumulados',
            mode='lines', fill='tozeroy',
            line=dict(color='#006B3F', width=2),
            fillcolor='rgba(0,107,63,0.10)',
        ))
        fig_wx.update_layout(yaxis=dict(title="GDD acumulados"))

    else:  # Humedad relativa
        if 'hum_pct' in wx_df.columns:
            hum_col = wx_df['hum_pct']
        else:
            hum_col = pd.Series([wx['hum_avg']] * len(wx_df))
        fig_wx.add_trace(go.Scatter(
            x=wx_df['fecha'], y=hum_col, name='Humedad relativa (%)',
            mode='lines', line=dict(color='#3b82f6', width=2),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.10)',
        ))
        fig_wx.update_layout(yaxis=dict(title="Humedad relativa (%)"))

    fig_wx.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_white', height=360,
        title=f"{variable_viz} — {zona_sel} ({agg_mode})",
        xaxis_title="Fecha",
        margin=dict(l=0, r=0, t=50, b=0),
    )
    st.plotly_chart(fig_wx, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SUBTABS: FENOLOGÍA + CORRELACIÓN ENSO ──
    clim_sub_a, clim_sub_b = st.tabs(["Fenología y GDD", "Correlación Clima–Rendimiento"])

    with clim_sub_a:
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            section_header("Estadio Fenológico")
            crop_for_pheno = cultivo_global if cultivo_global in ('Maíz', 'Trigo') else ('Maíz' if cultivo_global in ('Soja', 'Girasol', 'Todos') else 'Maíz')
            stage = engine.get_phenology_stage(crop_for_pheno, wx['gdd_acum'])
            gdd_targets = {
                'Maíz': [(0,'VE'),(100,'V3'),(200,'V6 (fertil.)'),(370,'V10'),
                         (530,'VT'),(670,'R1'),(830,'R2'),(1000,'R4'),(1200,'R6')],
                'Trigo': [(0,'Emerg.'),(150,'Macollaje (fertil.)'),(350,'Encañazón'),
                          (500,'Espigazón'),(650,'Antesis'),(900,'Lechoso'),(1200,'Madurez')],
            }
            targets = gdd_targets.get(crop_for_pheno, gdd_targets['Maíz'])
            max_gdd = targets[-1][0]
            progress_pct = min(100, int(wx['gdd_acum'] / max_gdd * 100))
            st.progress(progress_pct)
            st.markdown(f"""
            <div class="info-box">
                <strong>Cultivo:</strong> {crop_for_pheno}<br>
                <strong>GDD acumulados:</strong> {wx['gdd_acum']:.0f} de {max_gdd}<br>
                <strong>Estadio actual:</strong> {stage}<br>
                <strong>Avance ciclo:</strong> {progress_pct}%
            </div>
            """, unsafe_allow_html=True)

        with fcol2:
            section_header("Hitos del Ciclo")
            milestones_df = pd.DataFrame(targets, columns=['GDD', 'Estadio'])
            milestones_df['Estado'] = milestones_df['GDD'].apply(
                lambda g: 'Alcanzado' if wx['gdd_acum'] >= g else 'Pendiente'
            )
            milestones_df['GDD'] = milestones_df['GDD'].apply(lambda x: f"{x:,}")
            render_styled_table(milestones_df)

    with clim_sub_b:
        st.markdown('<p class="section-subtitle">Correlación histórica clima–rendimiento · Análisis ENSO 2000–2024</p>', unsafe_allow_html=True)

        _cultivo_corr = "Soja" if cultivo_global == "Todos" else cultivo_global
        with st.spinner("Cargando correlación clima-producción..."):
            clim_corr = load_climate_corr(_cultivo_corr)

        corr_df    = clim_corr['df']
        var_clima  = clim_corr['variable_clima']
        pearson_r  = clim_corr['pearson_r']
        pendiente  = clim_corr['pendiente']
        intercepto = clim_corr['intercepto']
        enso_actual = clim_corr['enso_actual']

        if corr_df.empty:
            st.info("Sin datos de correlación para este cultivo.")
        else:
            enso_colors = {'La Niña': '#00A34F', 'El Niño': '#f59e0b', 'neutro': '#9ca3af'}
            fig_corr = go.Figure()

            for enso_type, color in enso_colors.items():
                subset = corr_df[corr_df['enso'] == enso_type]
                if subset.empty:
                    continue
                fig_corr.add_trace(go.Scatter(
                    x=subset['variable_clima'], y=subset['rendimiento'],
                    mode='markers+text', name=enso_type,
                    text=subset['año'].astype(str), textposition='top center',
                    textfont=dict(size=8, color=color),
                    marker=dict(color=color, size=10, line=dict(color='white', width=1)),
                ))

            x_vals = corr_df['variable_clima'].values
            x_lin  = np.linspace(x_vals.min(), x_vals.max(), 50)
            y_lin  = intercepto + pendiente * x_lin
            fig_corr.add_trace(go.Scatter(
                x=x_lin, y=y_lin, mode='lines',
                name=f'Regresión (r={pearson_r:.2f})',
                line=dict(color='#374151', width=1.5, dash='dash'),
            ))

            fig_corr.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white', height=400,
                title=f"Correlación Clima–Rendimiento — {cultivo_global}",
                xaxis_title=var_clima, yaxis_title="Rendimiento (tn/ha)",
                legend=dict(orientation='h', y=-0.15),
                margin=dict(l=0, r=0, t=40, b=60),
            )
            st.plotly_chart(fig_corr, width='stretch')

            abs_r = abs(pearson_r)
            if abs_r > 0.5:
                corr_label = "Correlación FUERTE"
                corr_badge = "badge-green" if pearson_r > 0 else "badge-red"
            elif abs_r > 0.3:
                corr_label = "Correlación MODERADA"; corr_badge = "badge-amber"
            else:
                corr_label = "Correlación DÉBIL"; corr_badge = "badge-red"

            crr_c1, crr_c2 = st.columns([1, 2])
            with crr_c1:
                st.markdown(f"""
                <div class="ap-card" style="text-align:center;">
                    <div class="kpi-value" style="font-size:2.8rem;">{pearson_r:.2f}</div>
                    <div class="kpi-label">Pearson r</div>
                    <div style="margin-top:0.5rem;">
                        <span class="badge {corr_badge}">{corr_label}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with crr_c2:
                enso_estado = enso_actual['estado']
                enso_oni    = enso_actual['indice_oni']
                enso_prob   = enso_actual['probabilidad']
                enso_imp    = enso_actual.get(f"implicancia_{cultivo_global.lower()}",
                                              enso_actual.get('implicancia_soja', ''))
                enso_badge_cls = ("badge-green" if 'Niña' in enso_estado else
                                  "badge-amber" if 'Niño' in enso_estado else "badge-blue")
                st.markdown(f"""
                <div class="ap-card">
                    <strong>Estado ENSO Actual</strong><br>
                    <span class="badge {enso_badge_cls}">{enso_estado}</span>
                    <span style="margin-left:0.5rem;font-size:0.8rem;color:#6b7280;">ONI: {enso_oni}</span>
                    <div style="margin-top:0.8rem;font-size:0.85rem;">
                        <strong>Implicancia para {cultivo_global}:</strong><br>{enso_imp}
                    </div>
                    <div style="margin-top:0.6rem;font-size:0.75rem;color:#9aa0a6;">
                        Neutro {enso_prob['Neutro']}% · El Niño {enso_prob['El Niño']}% · La Niña {enso_prob['La Niña']}%
                        · {enso_actual['fuente']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            if 'enso' in corr_df.columns and 'rendimiento' in corr_df.columns:
                nina_rend   = corr_df[corr_df['enso'] == 'La Niña']['rendimiento'].mean()
                nino_rend   = corr_df[corr_df['enso'] == 'El Niño']['rendimiento'].mean()
                neutro_rend = corr_df[corr_df['enso'] == 'neutro']['rendimiento'].mean()
                if neutro_rend > 0:
                    nina_delta = (nina_rend - neutro_rend) / neutro_rend * 100
                    nino_delta = (nino_rend - neutro_rend) / neutro_rend * 100
                else:
                    nina_delta = nino_delta = 0
                st.markdown(f"""
                <div class="info-box">
                    <strong>Resumen ENSO — {cultivo_global}</strong><br>
                    La Niña: <strong>{nina_rend:.2f} tn/ha</strong> ({nina_delta:+.1f}% vs neutro) ·
                    El Niño: <strong>{nino_rend:.2f} tn/ha</strong> ({nino_delta:+.1f}% vs neutro) ·
                    Neutro: <strong>{neutro_rend:.2f} tn/ha</strong>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MÓDULO 5 — OPORTUNIDAD (Simulador integrado)
# ══════════════════════════════════════════════════════════
elif _page == "Oportunidad":

    render_page_header(
        "Oportunidad de Mercado",
        "Simulador de escenarios comerciales · Modelado de demanda y valor bajo distintos precios y área",
        "Ajustá precios de granos y fertilizantes, variación de área y adopción tecnológica. "
        "El índice de compra indica el momento óptimo para cerrar operaciones."
    )

    sim_left, sim_right = st.columns([1, 2])

    with sim_left:
        section_header("Parámetros del Escenario")

        preset_col1, preset_col2, preset_col3 = st.columns(3)
        with preset_col1:
            pess_btn = st.button("Pesimista", key="btn_pess")
        with preset_col2:
            base_btn = st.button("Base", key="btn_base")
        with preset_col3:
            opt_btn  = st.button("Optimista", key="btn_opt")

        for k, v in [('sim_soja',345),('sim_maiz',188),('sim_urea',480),
                     ('sim_map',685),('sim_area',0),('sim_adopt',85)]:
            if k not in st.session_state:
                st.session_state[k] = v

        if pess_btn:
            st.session_state.update({'sim_soja':280,'sim_maiz':150,'sim_urea':550,
                                     'sim_map':750,'sim_area':-10,'sim_adopt':70})
            st.info("Pesimista: Soja $280 · Maíz $150 · Urea $550 · MAP $750 · Área -10% · Adopción 70%")
        if base_btn:
            st.session_state.update({'sim_soja':345,'sim_maiz':188,'sim_urea':480,
                                     'sim_map':685,'sim_area':0,'sim_adopt':85})
            st.info("Base: Soja $345 · Maíz $188 · Urea $480 · MAP $685 · Área 0% · Adopción 85%")
        if opt_btn:
            st.session_state.update({'sim_soja':420,'sim_maiz':230,'sim_urea':400,
                                     'sim_map':580,'sim_area':10,'sim_adopt':95})
            st.info("Optimista: Soja $420 · Maíz $230 · Urea $400 · MAP $580 · Área +10% · Adopción 95%")

        st.markdown("---")
        st.markdown("**Precios de granos (USD/tn)**")
        precio_soja_sim = st.slider("Precio Soja", 200, 600, st.session_state.sim_soja, 5, key="sl_soja")
        precio_maiz_sim = st.slider("Precio Maíz", 100, 400, st.session_state.sim_maiz, 5, key="sl_maiz")

        st.markdown("**Precios de fertilizantes (USD/tn)**")
        precio_urea_sim = st.slider("Precio Urea", 200, 800, st.session_state.sim_urea, 10, key="sl_urea")
        precio_map_sim  = st.slider("Precio MAP",  300, 1000, st.session_state.sim_map, 10, key="sl_map")

        st.markdown("**Variables de escenario**")
        var_area_sim = st.slider("Variación Área (%)", -20, 20, st.session_state.sim_area, 1, key="sl_area")
        adopcion_sim = st.slider("Adopción tecnológica (%)", 60, 100, st.session_state.sim_adopt, 1, key="sl_adopt")

    with sim_right:
        with st.spinner("Calculando escenario..."):
            sim_result = engine.simulate_scenario(
                precio_soja=precio_soja_sim, precio_maiz=precio_maiz_sim,
                precio_urea=precio_urea_sim, precio_map=precio_map_sim,
                var_area_pct=var_area_sim, adopcion_pct=adopcion_sim,
            )

        total_dem_sim = sim_result['total_dem_tn']
        total_val_sim = sim_result['total_valor_musd']
        delta_dem     = sim_result['delta_dem_pct']
        delta_val     = sim_result['delta_val_pct']
        gauge_val     = sim_result['gauge_compra']
        ratios_sim_df = sim_result['ratios_sim_df']
        top5_cambios  = sim_result['top5_cambios']

        sk1, sk2, sk3, sk4 = st.columns(4)
        with sk1:
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value">{total_dem_sim/1000:.0f}K tn</div>
                <div class="kpi-label">Demanda total</div>
                <div class="kpi-sub">fertilizante simulado</div>
            </div>""", unsafe_allow_html=True)
        with sk2:
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value">USD {total_val_sim:.0f}M</div>
                <div class="kpi-label">Valor de mercado</div>
                <div class="kpi-sub">escenario simulado</div>
            </div>""", unsafe_allow_html=True)
        with sk3:
            dc = "#006B3F" if delta_dem >= 0 else "#DC2626"
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value" style="color:{dc};">{delta_dem:+.1f}%</div>
                <div class="kpi-label">Delta vs base</div>
                <div class="kpi-sub">demanda potencial</div>
            </div>""", unsafe_allow_html=True)
        with sk4:
            gc = "#006B3F" if gauge_val >= 70 else ("#F59E0B" if gauge_val >= 40 else "#DC2626")
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value" style="color:{gc};">{gauge_val}/100</div>
                <div class="kpi-label">Índice de compra</div>
                <div class="kpi-sub">gauge momento mercado</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        gcol1, gcol2 = st.columns([1, 2])
        with gcol1:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=gauge_val,
                title={'text': "Momento de Compra", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 100], 'tickfont': {'size': 10}},
                    'bar': {'color': gc},
                    'steps': [
                        {'range': [0,  40], 'color': 'rgba(220,38,38,0.12)'},
                        {'range': [40, 70], 'color': 'rgba(245,158,11,0.12)'},
                        {'range': [70,100], 'color': 'rgba(0,107,63,0.12)'},
                    ],
                    'threshold': {'line': {'color': '#374151', 'width': 2},
                                  'thickness': 0.75, 'value': gauge_val},
                },
                number={'font': {'size': 28, 'color': gc}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', height=250,
                margin=dict(l=20, r=20, t=40, b=0),
            )
            st.plotly_chart(fig_gauge, width='stretch')

        with gcol2:
            section_header("Ratios Simulados vs Base")
            if not ratios_sim_df.empty:
                ratios_display = ratios_sim_df[
                    (ratios_sim_df['grano'].isin(['Soja', 'Maíz'])) &
                    (ratios_sim_df['fertilizante'].isin(['Urea', 'MAP']))
                ].copy()
                if ratios_display.empty:
                    ratios_display = ratios_sim_df.head(10).copy()
                ratios_display['ratio_sim']  = ratios_display['ratio_sim'].apply(lambda x: f"{x:.2f}")
                ratios_display['ratio_base'] = ratios_display['ratio_base'].apply(lambda x: f"{x:.2f}")
                ratios_display['delta']      = ratios_display['delta'].apply(lambda x: f"{x:+.2f}")
                ratios_display = ratios_display.rename(columns={
                    'grano':'Grano','fertilizante':'Fertilizante',
                    'ratio_sim':'Ratio Sim.','ratio_base':'Ratio Base','delta':'Delta',
                })
                def _highlight_delta(val):
                    try:
                        v = float(val)
                        if v < 0: return 'color:#006B3F;font-weight:600'
                        elif v > 0: return 'color:#DC2626;font-weight:600'
                    except Exception:
                        pass
                    return ''
                st.dataframe(
                    ratios_display.style.map(_highlight_delta, subset=['Delta']),
                    width='stretch', hide_index=True,
                )

        st.markdown("---")
        section_header("Top 5 Zonas con Mayor Cambio")
        if not top5_cambios.empty:
            t5 = top5_cambios.copy()
            t5['delta_pct']  = t5['delta_pct'].apply(lambda x: f"{x:+.1f}%")
            t5['dem_sim_tn'] = t5['dem_sim_tn'].apply(lambda x: f"{x:,.0f}")
            t5 = t5.rename(columns={'departamento':'Departamento','provincia':'Provincia',
                                    'cultivo':'Cultivo','dem_sim_tn':'Demanda sim. (tn)',
                                    'delta_pct':'Delta vs base'})
            st.dataframe(t5, width='stretch', hide_index=True)

        if var_area_sim < -5 and precio_soja_sim < 300:
            escenario_nombre = "PESIMISTA"
        elif var_area_sim > 5 and precio_soja_sim > 380:
            escenario_nombre = "OPTIMISTA"
        else:
            escenario_nombre = "PERSONALIZADO"

        st.markdown(f"""
        <div class="info-box">
            <strong>Resumen Escenario {escenario_nombre}:</strong><br>
            Soja USD {precio_soja_sim}/tn · Maíz USD {precio_maiz_sim}/tn ·
            Urea USD {precio_urea_sim}/tn · MAP USD {precio_map_sim}/tn ·
            Área {var_area_sim:+.0f}% · Adopción {adopcion_sim}%<br><br>
            <strong>Resultado:</strong> Demanda total <strong>{total_dem_sim/1000:.0f}K tn</strong>
            ({delta_dem:+.1f}% vs base) ·
            Valor <strong>USD {total_val_sim:.0f}M</strong> ({delta_val:+.1f}% vs base) ·
            Índice de compra: <strong>{gauge_val}/100</strong>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="ap-footer">
    <strong>AgriPulse Argentina v2.0</strong> · Nutrien Ag Solutions Argentina<br>
    <span class="source-tag">Superficies</span> SIIA/MAGyP 2023/24
    <span class="source-tag">Dosis</span> INTA EEA Marcos Juárez
    <span class="source-tag">Clima</span> NASA POWER API
    <span class="source-tag">Precios</span> MATBA-ROFEX / CIAFA Marzo 2025
    <span class="source-tag">Campaña</span> BCR 2024/25
    <span class="source-tag">ENSO</span> NOAA CPC<br>
    <em>{today_str} · Python 3.12 · Streamlit 1.55 · Plotly 6.x · Pandas 2.3</em>
</div>
""", unsafe_allow_html=True)
