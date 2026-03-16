"""
AgriPulse Argentina — Plataforma de Inteligencia Comercial
Nutrien Ag Solutions Argentina
Versión 2.0 | Stack: Streamlit 1.55 · Plotly 6.x · Pandas 2.3
"""

import io
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

@st.cache_data(ttl=43200)
def load_climate_history(lat, lon, start_year, end_year):
    return engine.get_climate_history(lat, lon, start_year, end_year)

@st.cache_data(ttl=86400)
def load_geo_tables():
    _p = pd.read_csv(_DATA_DIR / "provincias_centroides.csv")
    _d = pd.read_csv(_DATA_DIR / "departamentos_agricolas.csv")
    return _p, _d

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
    st.markdown('<span class="filter-label">Cultivo</span>', unsafe_allow_html=True)
    selected = st.pills(
        "Cultivo",
        _OPTIONS,
        default=_default,
        selection_mode="single",
        key=key,
        label_visibility="collapsed",
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
                _cls_df = (
                    pd.concat(_frames).groupby(['departamento', 'provincia'])['clasificacion']
                    .agg(lambda x: x.value_counts().index[0]).reset_index()
                )
                score_df_base = score_df_base.merge(_cls_df, on=['departamento', 'provincia'], how='left')
                score_df_base['clasificacion'] = score_df_base['clasificacion'].fillna('MADUREZ')
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

    def _reset_weights():
        st.session_state.w_dem   = 25
        st.session_state.w_terr  = 20
        st.session_state.w_brech = 20
        st.session_state.w_ratio = 15
        st.session_state.w_clima = 10
        st.session_state.w_tend  = 10

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
        st.button("↺ Restaurar pesos base", on_click=_reset_weights, key="btn_reset_w")
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

    depto_options = (score_df['departamento'] + ' (' + score_df['provincia'] + ')').tolist()
    depto_label   = st.selectbox("Seleccionar departamento", options=depto_options, index=0)
    row_sel = score_df[
        (score_df['departamento'] + ' (' + score_df['provincia'] + ')') == depto_label
    ].iloc[0]
    depto_sel = row_sel['departamento']

    dcol1, dcol2 = st.columns([1, 1])

    with dcol1:
        _r_vals  = [float(row_sel.get(c, 50)) for c in
                    ['score_demanda','score_territorial','score_brecha','score_ratio','score_clima','score_tendencia']]
        _r_theta = ['Demanda', 'Territorial', 'Brecha Tech.', 'Ratio Mercado', 'Clima', 'Tendencia']
        fig_radar = go.Figure(go.Scatterpolar(
            r=_r_vals + [_r_vals[0]],
            theta=_r_theta + [_r_theta[0]],
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
        fert_opts = ["Todos", "Urea", "MAP", "MOP"]
        fert_mkt = st.selectbox("Fertilizante", fert_opts, key="mkt_fert")
    with fa_col4:
        show_nutrien    = st.checkbox("Sucursales Nutrien", value=True, key="mkt_nutrien")
        show_competitors = st.checkbox("Competidores", value=False, key="mkt_comp")

    # ── DOSIS AJUSTABLES ──
    _cultivo_dosis = cultivo_mkt if cultivo_mkt in engine.TECH_DOSAGE else 'Soja'
    _inta = engine.TECH_DOSAGE[_cultivo_dosis]
    _dk = {f: f"dose_{_cultivo_dosis}_{f}" for f in ['Urea', 'MAP', 'MOP']}

    _fert_ranges = {'Urea': (0, 300), 'MAP': (0, 200), 'MOP': (0, 150)}
    _fert_labels = {'Urea': 'Urea (kg/ha)', 'MAP': 'MAP (kg/ha)', 'MOP': 'MOP (kg/ha)'}

    if cultivo_mkt == "Todos":
        with st.expander("Ajustar dosis técnicas — seleccioná un cultivo específico para personalizar"):
            st.info("Las dosis INTA se aplican por cultivo. Seleccioná un cultivo específico en el filtro para ajustar dosis.")
        _dosis_activas = {}
    else:
        # Solo los fertilizantes que este cultivo realmente usa (dosis INTA > 0).
        # Si dosis==0, el engine no genera filas para ese fert → slider desconectado → se oculta.
        _ferts_usados = [f for f in ['Urea', 'MAP', 'MOP'] if _inta.get(f, 0) > 0]
        for f in ['Urea', 'MAP', 'MOP']:
            if _dk[f] not in st.session_state:
                st.session_state[_dk[f]] = int(_inta.get(f, 0))

        def _cb_reset_dose(_dk=_dk, _inta=_inta):
            for f in ['Urea', 'MAP', 'MOP']:
                st.session_state[_dk[f]] = int(_inta.get(f, 0))

        with st.expander(f"Ajustar dosis técnicas — {_cultivo_dosis} (kg/ha) · INTA EEA Marcos Juárez"):
            _dose_cols = st.columns(len(_ferts_usados) + 1)
            for _i, _f in enumerate(_ferts_usados):
                with _dose_cols[_i]:
                    st.slider(_fert_labels[_f], *_fert_ranges[_f], step=10, key=_dk[_f])
            with _dose_cols[-1]:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button("Restaurar INTA", key=f"reset_dose_{_cultivo_dosis}",
                          on_click=_cb_reset_dose)
            _dosis_p = {f: st.session_state[_dk[f]] for f in _ferts_usados}
            if any(_dosis_p[f] != _inta.get(f, 0) for f in _ferts_usados):
                _badges = ' · '.join(f"{f}: {_dosis_p[f]} kg/ha" for f in _ferts_usados)
                st.info(f"Dosis activas — {_badges}")
        _dosis_activas = {f: st.session_state[_dk[f]] for f in _ferts_usados}

    with st.spinner("Cargando datos de mercado..."):
        if cultivo_mkt == "Todos":
            _parts = [load_market(c, prov_mkt)[0] for c in ["Soja", "Maíz", "Trigo", "Girasol"]]
            result_df = pd.concat([p for p in _parts if not p.empty]).reset_index(drop=True)
        else:
            result_df, _ = load_market(cultivo_mkt, prov_mkt)

    if result_df.empty:
        st.info("Sin datos para esta selección.")
    else:
        # ── Filtro fertilizante ──
        result_filt = (result_df[result_df['fertilizante'] == fert_mkt].copy()
                       if fert_mkt != "Todos" else result_df.copy())
        for _col in ['dosis_kg_ha', 'demanda_potencial_tn', 'valor_mercado_musd']:
            if _col in result_filt.columns:
                result_filt[_col] = result_filt[_col].astype(float)

        # ── Aplicar dosis personalizadas (solo cuando un cultivo específico está activo) ──
        # Bug fix A: _dosis_activas is {} when cultivo_mkt=="Todos" → loop doesn't run
        for fert_name, dosis_val in _dosis_activas.items():
            mask = result_filt['fertilizante'] == fert_name
            if mask.any():
                _new_dem = (result_filt.loc[mask, 'area_ha'] * float(dosis_val) / 1000).values
                price    = engine.FERTILIZER_PRICES.get(fert_name, 0)
                result_filt.loc[mask, 'dosis_kg_ha']          = float(dosis_val)
                result_filt.loc[mask, 'demanda_potencial_tn'] = _new_dem
                result_filt.loc[mask, 'valor_mercado_musd']   = _new_dem * price / 1_000_000

        # ── Agregación por depto×cultivo (intermedia) ──
        map_filt = (
            result_filt.groupby(['provincia', 'departamento', 'lat', 'lon', 'area_ha'])
            .agg(demanda_total_tn=('demanda_potencial_tn', 'sum'),
                 valor_total_musd=('valor_mercado_musd', 'sum'))
            .reset_index()
        )

        # ── Bug fix B/C: colapsar a UN punto por departamento para mapa y tabla ──
        # Cuando cultivo_mkt=="Todos", map_filt tiene múltiples filas por depto (una por cultivo).
        # Sin este paso, el mapa superpone N burbujas en la misma coordenada.
        map_plot = (
            map_filt.groupby(['provincia', 'departamento', 'lat', 'lon'])
            .agg(demanda_total_tn=('demanda_total_tn', 'sum'),
                 valor_total_musd=('valor_total_musd', 'sum'),
                 area_ha=('area_ha', 'sum'))
            .reset_index()
        )

        total_dem    = result_filt['demanda_potencial_tn'].sum()
        total_val    = result_filt['valor_mercado_musd'].sum()
        n_deptos_mkt = map_plot['departamento'].nunique()

        mk1, mk2, mk3, mk4 = st.columns(4)
        with mk1:
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value">{map_plot['area_ha'].sum():,.0f}</div>
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
            map_plot, lat='lat', lon='lon',
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
            # Borde exterior (contraste)
            fig_mkt.add_trace(go.Scattermap(
                lat=nutrien_locs['lat'], lon=nutrien_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=20, color='white', symbol='circle', opacity=1.0),
                hoverinfo='skip', showlegend=False,
            ))
            # Punto Nutrien — círculo verde sólido
            fig_mkt.add_trace(go.Scattermap(
                lat=nutrien_locs['lat'], lon=nutrien_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=13, color='#006B3F', symbol='circle', opacity=1.0),
                hovertext=nutrien_locs['localidad'].apply(lambda x: f"🟢 Nutrien — {x}"),
                hoverinfo='text', name='● Nutrien',
            ))
        if show_competitors:
            comp_locs = pd.read_csv(_DATA_DIR / 'competitor_locations.csv')
            # Borde exterior (contraste)
            fig_mkt.add_trace(go.Scattermap(
                lat=comp_locs['lat'], lon=comp_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=20, color='white', symbol='circle', opacity=1.0),
                hoverinfo='skip', showlegend=False,
            ))
            # Punto Competencia — diamante rojo (forma distinta)
            fig_mkt.add_trace(go.Scattermap(
                lat=comp_locs['lat'], lon=comp_locs['lon'], mode='markers',
                marker=go.scattermap.Marker(size=13, color='#DC2626', symbol='diamond', opacity=1.0),
                hovertext=comp_locs['localidad'].apply(lambda x: f"🔴 Competencia — {x}"),
                hoverinfo='text', name='◆ Competencia',
            ))

        fig_mkt.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            template='plotly_white', height=460,
            margin=dict(l=0, r=0, t=36, b=0),
            legend=dict(
                x=0.99, y=0.99,
                xanchor='right', yanchor='top',
                bgcolor='rgba(255,255,255,0.92)',
                bordercolor='#d1d5db', borderwidth=1,
                font=dict(family='Inter, sans-serif', size=12),
                tracegroupgap=6,
            ),
        )
        st.plotly_chart(fig_mkt, width='stretch')

        section_header("Top 15 Departamentos por Demanda")
        top15 = (
            map_plot.sort_values('demanda_total_tn', ascending=False)
            .head(15)[['departamento','provincia','area_ha','demanda_total_tn','valor_total_musd']]
            .rename(columns={'departamento':'Departamento','provincia':'Provincia',
                             'area_ha':'Área (ha)','demanda_total_tn':'Demanda (tn)','valor_total_musd':'Valor (M USD)'})
        )
        top15['Área (ha)']     = top15['Área (ha)'].apply(lambda x: f"{x:,.0f}")
        top15['Demanda (tn)']  = top15['Demanda (tn)'].apply(lambda x: f"{x:,.0f}")
        top15['Valor (M USD)'] = top15['Valor (M USD)'].apply(lambda x: f"$ {x:.2f}M")
        render_styled_table(top15)

        if not map_plot.empty:
            top_dept = map_plot.sort_values('demanda_total_tn', ascending=False).iloc[0]
            _cult_txt = ("el agregado de cultivos analizados"
                         if cultivo_mkt == "Todos" else cultivo_mkt)
            _fert_txt = ("todos los fertilizantes" if fert_mkt == "Todos"
                         else fert_mkt)
            st.markdown(f"""
            <div class="info-box">
                <strong>Argumento Comercial:</strong><br>
                <strong>{top_dept['departamento']}</strong> ({top_dept['provincia']}) es el departamento
                con mayor demanda potencial de {_fert_txt}:
                <strong>{top_dept['demanda_total_tn']:,.0f} tn</strong> valoradas en
                <strong>USD {top_dept['valor_total_musd']:.2f}M</strong>,
                sobre <strong>{top_dept['area_ha']:,.0f} ha</strong> sembradas de {_cult_txt}.
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

    with st.expander("¿Cómo se construye la proyección?"):
        st.markdown("""
**Clasificación territorial** — cada departamento se clasifica según el CAGR de su superficie sembrada en el período seleccionado: CAGR > 2% → EXPANSIÓN · CAGR < −1% → CONTRACCIÓN · resto → MADUREZ. En "Todos los cultivos" se usa el CAGR ponderado por área de cada cultivo.

**Proyección individual** (cultivo específico) — aplica `ha(t) = ha_base × (1 + CAGR)^t`, usando el mismo CAGR del engine para mantener coherencia con la clasificación del mapa.

**Vista "Todos los cultivos"** — el gráfico principal muestra el histórico agregado de todos los cultivos. La proyección por cultivo se activa opcionalmente y muestra cada cultivo por separado con su propio CAGR.

**Reglas de prudencia** — se señalan o descartan proyecciones cuando: base < 500 ha · CAGR > ±45%/año (se aplica cap) · R² < 0.30. En esos casos la línea aparece gris punteada.

**Banda de incertidumbre** — orientativa. Su amplitud crece con el horizonte temporal (∝ √t). No es un intervalo de confianza estadístico; refleja que la incertidumbre acumulada aumenta con el tiempo.
        """)

    terr_all_df = pd.DataFrame()  # tabla per-cultivo sin deduplicar; solo "Todos"
    with st.spinner("Calculando clasificación territorial..."):
        if cultivo_global == "Todos":
            _t_all, _h_all = [], []
            for _c in ["Soja", "Maíz", "Trigo", "Girasol"]:
                _td, _hd, _ = load_territorial(_c, periodo_engine)
                if not _td.empty:
                    _t_all.append(_td)
                    _hd_c = _hd.copy()
                    _hd_c['cultivo'] = _c   # añadir cultivo para el gráfico per-crop
                    _h_all.append(_hd_c)
            terr_all_df = pd.concat(_t_all).reset_index(drop=True) if _t_all else pd.DataFrame()
            if not terr_all_df.empty:
                # CAGR ponderado por ha_actual y área total por departamento
                _g = terr_all_df.copy()
                _g['_wcagr'] = _g['cagr_pct'] * _g['ha_actual']
                _g['_wr2']   = _g['r2']       * _g['ha_actual']
                terr_df = (
                    _g.groupby(['departamento', 'provincia'])
                    .agg(lat=('lat', 'first'), lon=('lon', 'first'),
                         ha_actual=('ha_actual', 'sum'), proj_2026=('proj_2026', 'sum'),
                         _wcagr=('_wcagr', 'sum'), _wr2=('_wr2', 'sum'),
                         _ha=('ha_actual', 'sum'))
                    .reset_index()
                )
                terr_df['cagr_pct'] = terr_df['_wcagr'] / terr_df['_ha'].clip(lower=1)
                terr_df['r2']       = terr_df['_wr2']   / terr_df['_ha'].clip(lower=1)
                terr_df = terr_df.drop(columns=['_wcagr', '_wr2', '_ha'])
                terr_df['clasificacion'] = terr_df['cagr_pct'].apply(
                    lambda c: 'EXPANSIÓN' if c > 2.0 else ('CONTRACCIÓN' if c < -1.0 else 'MADUREZ')
                )
                conteos = terr_df['clasificacion'].value_counts().to_dict()
            else:
                terr_df = pd.DataFrame()
                conteos = {}
            hist_df = pd.concat(_h_all).reset_index(drop=True) if _h_all else pd.DataFrame()
        else:
            terr_df, hist_df, conteos = load_territorial(cultivo_global, periodo_engine)

    if terr_df.empty:
        st.info("Sin datos de clasificación territorial. Verificar CSVs SIIA.")
    else:
        if cultivo_global == "Todos":
            # El CAGR ponderado del agregado produce solo EXPANSIÓN/MADUREZ/CONTRACCIÓN
            _badge_info = [('EXPANSIÓN','badge-green'),('MADUREZ','badge-amber'),('CONTRACCIÓN','badge-red')]
            _kpi_cols = st.columns(3)
        else:
            _badge_info = [('EXPANSIÓN','badge-green'),('MADUREZ','badge-amber'),
                           ('CONTRACCIÓN','badge-red'),('EMERGENTE','badge-blue')]
            _kpi_cols = st.columns(4)
        for _bc, (cls, badge_cls) in zip(_kpi_cols, _badge_info):
            cnt = conteos.get(cls, 0)
            with _bc:
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
        dept_terr_opts = (terr_df['departamento'] + ' (' + terr_df['provincia'] + ')').tolist()
        if dept_terr_opts:
            dept_terr_label = st.selectbox("Departamento", options=dept_terr_opts, key="terr_dept_sel")
            dept_row = terr_df[
                (terr_df['departamento'] + ' (' + terr_df['provincia'] + ')') == dept_terr_label
            ].iloc[0]
            dept_terr_sel = dept_row['departamento']
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

                _hist_label = ('Total cultivos (agregado)'
                               if cultivo_global == "Todos" else 'Superficie histórica')
                fig_hist.add_trace(go.Scatter(
                    x=dept_hist['año'], y=dept_hist['sup_sembrada_ha'],
                    mode='lines+markers', name=_hist_label,
                    line=dict(color='#006B3F', width=2), marker=dict(size=5),
                ))

                # Guardrails de proyección
                _CAGR_CAP = 0.45    # limita proyecciones disparadas (±45%/año)
                _MIN_HA   = 500     # base mínima para proyección confiable
                proj_info_str = ""

                if show_projection and cultivo_global != "Todos":
                    # ── Proyección CAGR — cultivo específico ──
                    # Usa el CAGR del engine: misma ventana y método que la clasificación.
                    _cagr        = dept_row['cagr_pct'] / 100.0
                    _r2          = dept_row['r2']
                    _cagr_capped = abs(_cagr) > _CAGR_CAP
                    _cagr_proj   = max(-_CAGR_CAP, min(_CAGR_CAP, _cagr))
                    _tiny_base   = last_val < _MIN_HA
                    _low_conf    = _r2 < 0.30 or _tiny_base

                    # Volatilidad histórica para banda orientativa
                    _pct_ch = (dept_hist['sup_sembrada_ha']
                               .pct_change().replace([np.inf, -np.inf], np.nan).dropna())
                    _vol = float(_pct_ch.std()) if len(_pct_ch) > 2 else 0.25

                    proj_years = list(range(last_year + 1, last_year + periodo_anios + 1))
                    proj_vals  = [max(0.0, last_val * (1 + _cagr_proj) ** t)
                                  for t in range(1, len(proj_years) + 1)]
                    # Banda orientativa: volatilidad × √t (se ensancha con el horizonte)
                    _ci_lo = [max(0.0, v * (1 - _vol * t ** 0.5)) for t, v in enumerate(proj_vals, 1)]
                    _ci_hi = [v * (1 + _vol * t ** 0.5) for t, v in enumerate(proj_vals, 1)]

                    _band_fill = 'rgba(239,68,68,0.08)' if _low_conf else 'rgba(0,107,63,0.10)'
                    _line_col  = '#9ca3af' if _low_conf else '#006B3F'
                    _line_dash = 'dot'     if _low_conf else 'dash'

                    fig_hist.add_trace(go.Scatter(
                        x=proj_years + proj_years[::-1], y=_ci_hi + _ci_lo[::-1],
                        fill='toself', fillcolor=_band_fill,
                        line=dict(color='rgba(0,0,0,0)'), name='Rango orientativo',
                    ))
                    fig_hist.add_trace(go.Scatter(
                        x=[last_year] + proj_years, y=[last_val] + proj_vals,
                        mode='lines+markers',
                        name=f'Proyección CAGR ({_cagr_proj:+.1%}/año)',
                        line=dict(color=_line_col, width=2, dash=_line_dash),
                        marker=dict(size=8, symbol='diamond', color=_line_col),
                    ))
                    proj_fin_year = proj_years[-1]
                    proj_fin_val  = int(proj_vals[-1])
                    _warn = []
                    if _cagr_capped: _warn.append(f'CAGR real {_cagr*100:+.1f}% → cap ±{_CAGR_CAP*100:.0f}%')
                    if _tiny_base:   _warn.append(f'base pequeña ({last_val:,.0f} ha)')
                    if _r2 < 0.30:   _warn.append(f'R²={_r2:.2f}')
                    _conf_tag = (f' · <em style="color:#9ca3af">baja confianza: {", ".join(_warn)}</em>'
                                 if _warn else '')
                    proj_info_str = (
                        f" · Proyección {proj_fin_year}: <strong>{proj_fin_val:,} ha</strong>"
                        f" (CAGR {_cagr_proj:+.1%}/año){_conf_tag}"
                    )

                _title_suf = (" (total agregado)" if cultivo_global == "Todos"
                              else ("" if show_projection else " (histórico)"))
                fig_hist.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    template='plotly_white', height=320,
                    title=f"{dept_terr_sel} — {cultivo_global} (ha sembradas){_title_suf}",
                    xaxis_title="Campaña", yaxis_title="Hectáreas",
                    legend=dict(orientation='h', y=-0.15),
                    margin=dict(l=0, r=0, t=40, b=0),
                )
                st.plotly_chart(fig_hist, width='stretch')

                # ── Proyección por cultivo — solo "Todos" + periodo activo ──
                if cultivo_global == "Todos" and show_projection:
                    if st.checkbox("Ver proyección por cultivo", value=False, key="terr_per_crop"):
                        _CROP_COLORS = {
                            'Soja': '#006B3F', 'Maíz': '#f59e0b',
                            'Trigo': '#3b82f6', 'Girasol': '#e57200',
                        }
                        fig_crop = go.Figure()
                        for _c in ['Soja', 'Maíz', 'Trigo', 'Girasol']:
                            if 'cultivo' not in hist_df.columns:
                                break
                            _crop_h = hist_df[
                                (hist_df['departamento'] == dept_terr_sel) &
                                (hist_df['provincia'] == dept_row['provincia']) &
                                (hist_df['cultivo'] == _c)
                            ].sort_values('año')
                            if _crop_h.empty:
                                continue
                            _crop_rows = terr_all_df[
                                (terr_all_df['departamento'] == dept_terr_sel) &
                                (terr_all_df['provincia'] == dept_row['provincia']) &
                                (terr_all_df['cultivo'] == _c)
                            ]
                            if _crop_rows.empty:
                                continue
                            _cr       = _crop_rows.iloc[0]
                            _cc       = _CROP_COLORS.get(_c, '#6b7280')
                            _c_ly     = int(_crop_h['año'].max())
                            _c_lv     = float(_crop_h[_crop_h['año'] == _c_ly]['sup_sembrada_ha'].values[0])
                            _c_cagr_r = float(_cr['cagr_pct']) / 100.0
                            _c_cagr   = max(-_CAGR_CAP, min(_CAGR_CAP, _c_cagr_r))
                            _c_low    = (_c_lv < _MIN_HA or abs(_c_cagr_r) > _CAGR_CAP
                                         or float(_cr['r2']) < 0.25)
                            # Histórico por cultivo (línea + markers pequeños)
                            _conf_sfx = "" if not _c_low else " ⚠"
                            fig_crop.add_trace(go.Scatter(
                                x=_crop_h['año'], y=_crop_h['sup_sembrada_ha'],
                                mode='lines+markers',
                                name=f'{_c}  {_c_cagr:+.1%}/año{_conf_sfx}',
                                line=dict(color=_cc, width=2), legendgroup=_c,
                                marker=dict(size=4, color=_cc),
                            ))
                            # Proyección (omitida si baja confianza)
                            if not _c_low:
                                _c_py = list(range(_c_ly + 1, _c_ly + periodo_anios + 1))
                                _c_pv = [max(0.0, _c_lv * (1 + _c_cagr) ** t)
                                         for t in range(1, len(_c_py) + 1)]
                                fig_crop.add_trace(go.Scatter(
                                    x=[_c_ly] + _c_py, y=[_c_lv] + _c_pv,
                                    mode='lines+markers', name=_c,
                                    legendgroup=_c, showlegend=False,
                                    line=dict(color=_cc, width=2, dash='dash'),
                                    marker=dict(size=7, symbol='diamond', color=_cc),
                                ))
                        if fig_crop.data:
                            fig_crop.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                template='plotly_white', height=310,
                                title=f"{dept_terr_sel} — evolución y proyección por cultivo",
                                xaxis_title="Campaña", yaxis_title="Hectáreas",
                                legend=dict(orientation='h', y=-0.25, tracegroupgap=0),
                                margin=dict(l=0, r=0, t=40, b=20),
                            )
                            st.plotly_chart(fig_crop, width='stretch')
                            st.caption(
                                "─── histórico (marcadores ●) · ╌ ╌ proyección CAGR (marcadores ◆) · "
                                "⚠ = baja confianza (base < 500 ha, CAGR > ±45%/año o R² < 0.25) — proyección omitida"
                            )
                        else:
                            st.info("Sin datos por cultivo para este departamento.")

                # ── Info box ──
                cls_val = dept_row['clasificacion']
                if cultivo_global == "Todos":
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>{dept_terr_sel}</strong> ·
                        Vista: <strong>Total cultivos (área agregada)</strong> ·
                        Clasificación agregada: <strong>{cls_val}</strong> ·
                        CAGR ponderado: <strong>{dept_row['cagr_pct']:+.1f}%</strong>
                        {(' · ' + proj_info_str) if proj_info_str else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>{dept_terr_sel}</strong> · Clasificación: <strong>{cls_val}</strong> ·
                        CAGR {periodo_label}: <strong>{dept_row['cagr_pct']:+.1f}%</strong> ·
                        R²: <strong>{dept_row['r2']:.3f}</strong>{proj_info_str}
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
# MÓDULO 4 — ANÁLISIS CLIMÁTICO
# ══════════════════════════════════════════════════════════
elif _page == "Clima":

    render_page_header(
        "Análisis Climático",
        "Laboratorio histórico multi-decadal · NASA POWER · Hasta 40+ años de datos",
        "Exploración guiada por tipo de análisis: tendencias, estacionalidad, anomalías, extremos y riesgo climático.",
    )

    # ─── CONSTANTES ───────────────────────────────────────────
    _CY = datetime.date.today().year
    _VAR_MAP = {
        "Temperatura media":  {"col": "temp_mean", "label": "Temp. Media (°C)",     "unit": "°C",       "color": "#ef4444", "agg": "Media"},
        "Temperatura máxima": {"col": "temp_max",  "label": "Temp. Máxima (°C)",    "unit": "°C",       "color": "#f97316", "agg": "Máximo"},
        "Temperatura mínima": {"col": "temp_min",  "label": "Temp. Mínima (°C)",    "unit": "°C",       "color": "#3b82f6", "agg": "Mínimo"},
        "Precipitación":      {"col": "precip",    "label": "Precipitación (mm)",    "unit": "mm",       "color": "#2563eb", "agg": "Suma"},
        "Humedad relativa":   {"col": "humidity",  "label": "Humedad Relativa (%)",  "unit": "%",        "color": "#0891b2", "agg": "Media"},
        "Radiación solar":    {"col": "radiation", "label": "Radiación (MJ/m²/d)",  "unit": "MJ/m²/d",  "color": "#eab308", "agg": "Media"},
        "GDD acumulados":     {"col": "gdd",       "label": "GDD (base 10°C)",       "unit": "GDD",      "color": "#006B3F", "agg": "Suma"},
    }
    _AGG_FN    = {"Media": "mean", "Suma": "sum", "Máximo": "max", "Mínimo": "min"}
    _MON_NAMES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    _CHART_MAP = {
        "Tendencia histórica":   ["Línea", "Área", "Barras", "Scatter"],
        "Estacionalidad":        ["Heatmap", "Boxplot", "Barras"],
        "Anomalías":             ["Barras", "Línea"],
        "Extremos":              ["Línea", "Scatter"],
        "Variabilidad":          ["Área", "Línea"],
        "Acumulados":            ["Línea", "Área"],
        "Comparación histórica": ["Línea", "Área"],
        "Riesgo climático":      ["Heatmap", "Barras"],
    }

    # ─── DATOS GEOGRÁFICOS ────────────────────────────────────
    _geo_prov, _geo_depto = load_geo_tables()
    _prov_list   = sorted(_geo_prov["provincia"].unique())
    _prov_coords = _geo_prov.set_index("provincia")[["lat", "lon"]].to_dict("index")

    # ─── PANEL DE CONTROLES ───────────────────────────────────
    st.markdown('<div class="clima-controls">', unsafe_allow_html=True)

    # Fila 1 — Qué analizar
    f1a, f1b, f1c = st.columns([3, 3, 3], gap="small")
    with f1a:
        tipo_analisis = st.selectbox("Tipo de análisis", list(_CHART_MAP.keys()), key="ca_tipo")
    with f1b:
        var_clim = st.selectbox("Variable climática", list(_VAR_MAP.keys()), key="ca_var")
    with f1c:
        tipo_grafico = st.selectbox("Tipo de gráfico", _CHART_MAP[tipo_analisis], key="ca_chart")

    st.markdown('<div style="border-top:1px solid #e8eaed;margin:0.5rem 0 0.3rem 0;"></div>',
                unsafe_allow_html=True)

    # Fila 2 — Dónde y cuándo
    f2a, f2b, f2c, f2d, f2e = st.columns([2, 2, 2, 1.5, 1.5], gap="small")
    lat_ca = lon_ca = None
    lugar_label = ""
    with f2a:
        nivel_geo = st.selectbox(
            "Nivel geográfico", ["Zona predefinida", "Provincia", "Departamento"], key="ca_nivel"
        )
    with f2b:
        if nivel_geo == "Zona predefinida":
            zona_ca = st.selectbox("Zona", list(engine.ZONES.keys()), key="ca_zona2")
            lat_ca, lon_ca = engine.ZONES[zona_ca]["lat"], engine.ZONES[zona_ca]["lon"]
            lugar_label = zona_ca
        else:
            prov_sel = st.selectbox("Provincia", _prov_list, key="ca_prov")
    with f2c:
        if nivel_geo == "Departamento":
            _dep_list = sorted(
                _geo_depto[_geo_depto["provincia"] == prov_sel]["departamento"].unique()
            )
            if _dep_list:
                depto_sel = st.selectbox("Departamento", _dep_list, key="ca_depto")
                _r = _geo_depto[
                    (_geo_depto["provincia"] == prov_sel) &
                    (_geo_depto["departamento"] == depto_sel)
                ]
                lat_ca, lon_ca = float(_r["lat"].iloc[0]), float(_r["lon"].iloc[0])
                lugar_label = f"{depto_sel} · {prov_sel}"
            else:
                lat_ca, lon_ca, lugar_label = -33.89, -60.57, prov_sel
        elif nivel_geo == "Provincia":
            lat_ca  = float(_prov_coords[prov_sel]["lat"])
            lon_ca  = float(_prov_coords[prov_sel]["lon"])
            lugar_label = prov_sel
        if lat_ca is not None:
            st.markdown(
                f'<div style="padding:0.28rem 0.55rem;background:#f5f6f7;border-radius:6px;'
                f'font-size:0.78rem;color:#5F6368;margin-top:1.5rem;">📍 {lat_ca:.2f}°, {lon_ca:.2f}°</div>',
                unsafe_allow_html=True,
            )
    with f2d:
        yr_ini = st.number_input(
            "Año inicio", min_value=1984, max_value=_CY - 1, value=_CY - 20, step=1, key="ca_yr_ini"
        )
    with f2e:
        yr_fin = st.number_input(
            "Año fin", min_value=1984, max_value=_CY - 1, value=_CY - 1, step=1, key="ca_yr_fin"
        )

    yr_ini, yr_fin = int(min(yr_ini, yr_fin)), int(max(yr_ini, yr_fin))
    st.markdown('<div style="border-top:1px solid #e8eaed;margin:0.5rem 0 0.3rem 0;"></div>',
                unsafe_allow_html=True)

    # Fila 3 — Cuándo (meses) + agregación
    _vi = _VAR_MAP[var_clim]
    f3a, f3b, f3c = st.columns([5, 2, 2], gap="small")
    with f3a:
        meses_disp = st.pills(
            "Meses incluidos en el análisis",
            options=_MON_NAMES,
            default=_MON_NAMES,
            selection_mode="multi",
            key="ca_meses_pills",
        )
        if not meses_disp:
            meses_disp = list(_MON_NAMES)
    with f3b:
        granularidad = st.selectbox(
            "Granularidad", ["Mensual", "Anual", "Campaña agrícola"], key="ca_gran"
        )
    with f3c:
        _agg_opts = ["Media", "Suma", "Máximo", "Mínimo"]
        agregacion = st.selectbox(
            "Agregación", _agg_opts, index=_agg_opts.index(_vi["agg"]), key="ca_agg"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ─── VALIDACIONES ─────────────────────────────────────────
    meses_idx = ([_MON_NAMES.index(m) + 1 for m in meses_disp]
                 if meses_disp else list(range(1, 13)))
    start_yr, end_yr = yr_ini, yr_fin
    if lat_ca is None:
        lat_ca, lon_ca, lugar_label = -33.89, -60.57, "Zona Núcleo (fallback)"

    # ─── CARGA DE DATOS ───────────────────────────────────────
    with st.spinner(f"Cargando {start_yr}–{end_yr} · {lugar_label}..."):
        _ch         = load_climate_history(lat_ca, lon_ca, start_yr, end_yr)
    raw_df_full = _ch["df"]
    fuente_ch   = _ch["fuente"]
    ok_ch       = _ch["success"]

    # ─── FILTRO DE MESES ──────────────────────────────────────
    raw_df = (raw_df_full[raw_df_full["month"].isin(meses_idx)].copy()
              if set(meses_idx) != set(range(1, 13)) else raw_df_full.copy())
    if raw_df.empty:
        st.warning("Sin datos para la selección. Amplía el rango o los meses.")
        st.stop()

    # ─── COMMON VARS ──────────────────────────────────────────
    col    = _vi["col"]
    vcolor = _vi["color"]
    vlabel = _vi["label"]
    vunit  = _vi["unit"]
    agg_fn = _AGG_FN[agregacion]

    _meses_presentes = sorted(raw_df["month"].unique())
    _mon_labels      = [_MON_NAMES[m - 1] for m in _meses_presentes]

    def _rgba(hx, a=0.15):
        h = hx.lstrip("#")
        return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

    def _trace(x, y, name, color, ct, **kw):
        if ct == "Barras":
            return go.Bar(x=x, y=y, name=name, marker_color=color, **kw)
        if ct == "Scatter":
            return go.Scatter(x=x, y=y, mode="markers", name=name,
                              marker=dict(color=color, size=6), **kw)
        if ct == "Área":
            return go.Scatter(x=x, y=y, mode="lines", fill="tozeroy", name=name,
                              line=dict(color=color, width=2),
                              fillcolor=_rgba(color, 0.20), **kw)
        return go.Scatter(x=x, y=y, mode="lines", name=name,
                          line=dict(color=color, width=2), **kw)

    # ─── AGREGACIÓN ───────────────────────────────────────────
    def _agg_data(df, gran, _col, _fn):
        if gran == "Mensual":
            return df[["date", "year", "month", _col]].copy()
        if gran == "Anual":
            return (df.groupby("year")[_col].agg(_fn).reset_index()
                    .assign(date=lambda d: pd.to_datetime(d["year"].astype(str) + "-07-01")))
        df2 = df.copy()
        df2["camp_yr"]    = df2.apply(lambda r: r["year"] if r["month"] <= 9 else r["year"] + 1, axis=1)
        df2["camp_label"] = df2["camp_yr"].apply(lambda y: f"{y-1}/{str(y)[2:]}")
        return (df2.groupby(["camp_yr", "camp_label"])[_col].agg(_fn).reset_index()
                .assign(date=lambda d: pd.to_datetime(d["camp_yr"].astype(str) + "-09-01"))
                .rename(columns={"camp_yr": "year"}))

    agg_df = _agg_data(raw_df, granularidad, col, agg_fn)

    # ─── EJE X CONTEXTUAL ─────────────────────────────────────
    _single_yr = (start_yr == end_yr)
    if granularidad == "Mensual" and _single_yr:
        agg_df["x_label"] = agg_df["month"].apply(lambda m: _MON_NAMES[m - 1])
        x_col, x_title = "x_label", "Mes"
    elif granularidad == "Mensual":
        x_col, x_title = "date", "Fecha"
    elif granularidad == "Anual":
        x_col, x_title = "year", "Año"
    else:
        x_col, x_title = "camp_label", "Campaña agrícola"

    # ─── KPI CARDS ────────────────────────────────────────────
    _all_v   = raw_df[col].dropna()
    _ann_agg = (raw_df.groupby("year")[col].agg(agg_fn)
                if not raw_df.empty else pd.Series(dtype=float))
    _mean_v  = float(_all_v.mean())     if len(_all_v) else 0.0
    _max_v   = float(_all_v.max())      if len(_all_v) else 0.0
    _min_v   = float(_all_v.min())      if len(_all_v) else 0.0
    _last_v  = float(_ann_agg.iloc[-1]) if len(_ann_agg) else 0.0
    _last_pct = ((_last_v - _mean_v) / abs(_mean_v) * 100) if _mean_v else 0.0

    if len(_ann_agg) >= 3:
        _yr_arr  = np.array(_ann_agg.index, dtype=float)
        _yv_arr  = _ann_agg.values.astype(float)
        _ok_m    = ~np.isnan(_yv_arr)
        _trend_c = float(np.polyfit(_yr_arr[_ok_m], _yv_arr[_ok_m], 1)[0]) if _ok_m.sum() >= 3 else 0.0
    else:
        _trend_c = 0.0
    _trend_dec  = _trend_c * 10
    _trend_icon = "▲" if _trend_c > 0.005 else ("▽" if _trend_c < -0.005 else "→")
    _trend_col  = "#ef4444" if _trend_c > 0.005 else ("#3b82f6" if _trend_c < -0.005 else "#6b7280")
    _meses_txt  = (", ".join(_mon_labels) if len(_mon_labels) < 12 else "todos los meses")

    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    with kc1:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{_mean_v:.1f}<span style="font-size:0.85rem;font-weight:400"> {vunit}</span></div>
            <div class="kpi-label">Media período</div>
            <div class="kpi-sub">{start_yr}–{end_yr} · {_meses_txt[:22]}</div>
        </div>""", unsafe_allow_html=True)
    with kc2:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{_max_v:.1f}<span style="font-size:0.85rem;font-weight:400"> {vunit}</span></div>
            <div class="kpi-label">Máximo mensual</div>
            <div class="kpi-sub">período analizado</div>
        </div>""", unsafe_allow_html=True)
    with kc3:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{_min_v:.1f}<span style="font-size:0.85rem;font-weight:400"> {vunit}</span></div>
            <div class="kpi-label">Mínimo mensual</div>
            <div class="kpi-sub">período analizado</div>
        </div>""", unsafe_allow_html=True)
    with kc4:
        _sign = "+" if _last_pct >= 0 else ""
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{_last_v:.1f}<span style="font-size:0.85rem;font-weight:400"> {vunit}</span></div>
            <div class="kpi-label">Valor {end_yr} ({agregacion.lower()})</div>
            <div class="kpi-sub">{_sign}{_last_pct:.1f}% vs media</div>
        </div>""", unsafe_allow_html=True)
    with kc5:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value" style="font-size:1.3rem;color:{_trend_col};">{_trend_icon} {abs(_trend_dec):.2f}</div>
            <div class="kpi-label">Tendencia / década</div>
            <div class="kpi-sub"><span class="badge {'badge-green' if ok_ch else 'badge-amber'}">{fuente_ch[:22]}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # VISUALIZACIÓN PRINCIPAL
    # ─────────────────────────────────────────────────────────
    st.markdown('<div class="ap-card" style="padding:0.75rem 1rem 1rem 1rem;">', unsafe_allow_html=True)
    section_header(f"{tipo_analisis} · {var_clim} · {lugar_label} · {tipo_grafico}")
    fig_main = go.Figure()

    # ── A. TENDENCIA HISTÓRICA ────────────────────────────────
    if tipo_analisis == "Tendencia histórica":
        _d  = agg_df.copy()
        _xs = _d[x_col]
        _ys = _d[col]
        # P25–P75 band (monthly only, not for bar/scatter)
        if granularidad == "Mensual" and tipo_grafico not in ("Barras", "Scatter"):
            _p25m = raw_df.groupby("month")[col].quantile(0.25)
            _p75m = raw_df.groupby("month")[col].quantile(0.75)
            _lo   = list(_d["month"].map(_p25m))
            _hi   = list(_d["month"].map(_p75m))
            _xl   = list(_xs)
            fig_main.add_trace(go.Scatter(
                x=_xl + _xl[::-1], y=_hi + _lo[::-1],
                fill="toself", fillcolor=_rgba(vcolor, 0.12),
                line=dict(width=0), name="Rango P25–P75",
            ))
        fig_main.add_trace(_trace(_xs, _ys, vlabel, vcolor, tipo_grafico, opacity=0.85))
        # Moving average (line/area only)
        _maw = 12 if granularidad == "Mensual" else 5
        if len(_d) >= _maw and tipo_grafico in ("Línea", "Área"):
            _ma = _ys.rolling(_maw, center=True, min_periods=max(3, _maw // 2)).mean()
            fig_main.add_trace(go.Scatter(
                x=_xs, y=_ma, mode="lines", name=f"MA {_maw}",
                line=dict(color=vcolor, width=2.5),
            ))
        # Linear trend
        if len(_d) >= 5:
            _xn = np.arange(len(_d), dtype=float)
            _yv = _ys.values.astype(float)
            _ok = ~np.isnan(_yv)
            if _ok.sum() >= 5:
                _tr = np.polyval(np.polyfit(_xn[_ok], _yv[_ok], 1), _xn)
                fig_main.add_trace(go.Scatter(
                    x=_xs, y=_tr, mode="lines", name="Tendencia lineal",
                    line=dict(color="#374151", width=1.5, dash="dash"),
                ))
        fig_main.update_layout(yaxis_title=vlabel, xaxis_title=x_title,
                               legend=dict(orientation="h", y=1.08, x=0))

    # ── B. ESTACIONALIDAD ─────────────────────────────────────
    elif tipo_analisis == "Estacionalidad":
        if tipo_grafico == "Boxplot":
            for mi, mn in zip(_meses_presentes, _mon_labels):
                _mv = raw_df[raw_df["month"] == mi][col].dropna().values
                fig_main.add_trace(go.Box(
                    y=_mv, name=mn, marker_color=vcolor, boxmean="sd",
                    line=dict(color="#374151", width=1), fillcolor=_rgba(vcolor, 0.25),
                ))
            fig_main.update_layout(yaxis_title=vlabel, xaxis_title="Mes", showlegend=False)
        elif tipo_grafico == "Barras":
            _seas = raw_df.groupby("month")[col].mean().reindex(_meses_presentes)
            fig_main.add_trace(go.Bar(
                x=_mon_labels, y=_seas.values,
                marker_color=vcolor, name=f"Media {agregacion}",
            ))
            fig_main.update_layout(yaxis_title=vlabel, xaxis_title="Mes")
        else:  # Heatmap (default)
            _pivot = raw_df.pivot_table(values=col, index="year", columns="month", aggfunc=agg_fn)
            _pivot = _pivot.reindex(columns=_meses_presentes)
            _pivot.columns = [_MON_NAMES[m - 1] for m in _pivot.columns]
            _cscale = "Blues" if col in ("precip", "humidity") else "RdYlGn"
            fig_main = go.Figure(go.Heatmap(
                z=_pivot.values, x=_pivot.columns.tolist(), y=_pivot.index.tolist(),
                colorscale=_cscale, colorbar=dict(title=vunit, len=0.8),
            ))
            fig_main.update_layout(yaxis_title="Año", xaxis_title="Mes")

    # ── C. ANOMALÍAS ──────────────────────────────────────────
    elif tipo_analisis == "Anomalías":
        _clim_m   = raw_df.groupby("month")[col].mean()
        _df_an    = raw_df.copy()
        _df_an["anom"] = _df_an[col] - _df_an["month"].map(_clim_m)
        _ann_an   = _df_an.groupby("year")["anom"].mean().reset_index()
        if tipo_grafico == "Línea":
            _poscol = _rgba(vcolor, 0.9)
            fig_main.add_trace(go.Scatter(
                x=_ann_an["year"], y=_ann_an["anom"],
                mode="lines+markers", name="Anomalía anual",
                line=dict(color=vcolor, width=2),
                marker=dict(color=[_poscol if v >= 0 else "#3b82f6"
                                   for v in _ann_an["anom"]], size=6),
            ))
        else:  # Barras (default)
            _barcols = [_rgba(vcolor, 0.9) if v >= 0 else "#3b82f6" for v in _ann_an["anom"]]
            fig_main.add_trace(go.Bar(x=_ann_an["year"], y=_ann_an["anom"],
                                      marker_color=_barcols, name="Anomalía anual"))
        fig_main.add_hline(y=0, line_color="#374151", line_width=1)
        if len(_ann_an) >= 5:
            _xn = np.arange(len(_ann_an), dtype=float)
            _yv = _ann_an["anom"].values
            _tr = np.polyval(np.polyfit(_xn, _yv, 1), _xn)
            fig_main.add_trace(go.Scatter(
                x=_ann_an["year"], y=_tr, mode="lines", name="Tendencia",
                line=dict(color="#ef4444", width=2, dash="dash"),
            ))
        fig_main.update_layout(
            yaxis_title=f"Anomalía ({vunit})", xaxis_title="Año",
            legend=dict(orientation="h", y=1.08, x=0),
        )

    # ── D. EXTREMOS ───────────────────────────────────────────
    elif tipo_analisis == "Extremos":
        _d   = agg_df.copy()
        _xs  = _d[x_col]
        _ys  = _d[col]
        _p10 = float(_ys.quantile(0.10))
        _p90 = float(_ys.quantile(0.90))
        _mc  = ["#ef4444" if v > _p90 else ("#3b82f6" if v < _p10 else "#9ca3af") for v in _ys]
        if tipo_grafico == "Scatter":
            fig_main.add_trace(go.Scatter(x=_xs, y=_ys, mode="markers",
                                          marker=dict(color=_mc, size=7), showlegend=False))
        else:  # Línea (default)
            fig_main.add_trace(go.Scatter(x=_xs, y=_ys, mode="lines",
                                          line=dict(color="#d1d5db", width=1.2), showlegend=False))
            fig_main.add_trace(go.Scatter(x=_xs, y=_ys, mode="markers",
                                          marker=dict(color=_mc, size=5), showlegend=False))
        fig_main.add_hline(y=_p90, line_color="#ef4444", line_dash="dot", line_width=1,
                           annotation_text="P90", annotation_position="right")
        fig_main.add_hline(y=_p10, line_color="#3b82f6", line_dash="dot", line_width=1,
                           annotation_text="P10", annotation_position="right")
        fig_main.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
                                      marker=dict(color="#ef4444", size=8),
                                      name=f"Extremo alto (>{_p90:.1f} {vunit})"))
        fig_main.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
                                      marker=dict(color="#3b82f6", size=8),
                                      name=f"Extremo bajo (<{_p10:.1f} {vunit})"))
        fig_main.update_layout(yaxis_title=vlabel, xaxis_title=x_title,
                               legend=dict(orientation="h", y=1.08, x=0))

    # ── E. VARIABILIDAD ───────────────────────────────────────
    elif tipo_analisis == "Variabilidad":
        _am  = raw_df.groupby("year")[col].mean()
        _as  = raw_df.groupby("year")[col].std().fillna(0)
        _yrs = list(_am.index)
        if tipo_grafico == "Línea":
            fig_main.add_trace(go.Scatter(
                x=_yrs, y=_am.values, mode="lines+markers", name="Media anual",
                line=dict(color=vcolor, width=2.2), marker=dict(size=5, color=vcolor),
            ))
            fig_main.add_trace(go.Scatter(
                x=_yrs, y=(_am + _as).values, mode="lines", name="+1σ",
                line=dict(color=vcolor, width=1, dash="dot"),
            ))
            fig_main.add_trace(go.Scatter(
                x=_yrs, y=(_am - _as).values, mode="lines", name="-1σ",
                line=dict(color=vcolor, width=1, dash="dot"),
            ))
        else:  # Área (default)
            fig_main.add_trace(go.Scatter(
                x=_yrs + _yrs[::-1],
                y=list(_am + _as) + list((_am - _as).values[::-1]),
                fill="toself", fillcolor=_rgba(vcolor, 0.15),
                line=dict(width=0), name="Rango ±σ anual",
            ))
            fig_main.add_trace(go.Scatter(
                x=_yrs, y=_am.values, mode="lines+markers", name="Media anual",
                line=dict(color=vcolor, width=2.2), marker=dict(size=5, color=vcolor),
            ))
        fig_main.add_hline(y=float(_am.mean()), line_color="#374151", line_dash="dash",
                           line_width=1, annotation_text="Media hist.", annotation_position="right")
        fig_main.update_layout(yaxis_title=vlabel, xaxis_title="Año",
                               legend=dict(orientation="h", y=1.08, x=0))

    # ── F. ACUMULADOS ─────────────────────────────────────────
    elif tipo_analisis == "Acumulados":
        _hist_cum  = raw_df.groupby("month")[col].mean().reindex(_meses_presentes).cumsum()
        _yrs_all   = sorted(raw_df["year"].unique())
        _show_yrs  = _yrs_all[-5:] if len(_yrs_all) > 5 else _yrs_all
        _pal       = ["#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8"]
        for i, yr in enumerate(_show_yrs):
            _yd  = raw_df[raw_df["year"] == yr].sort_values("month")
            _yd  = _yd[_yd["month"].isin(_meses_presentes)]
            _yc  = _yd[col].cumsum().values
            _mns = [_MON_NAMES[m - 1] for m in _yd["month"].values]
            _c   = _pal[i % len(_pal)]
            if tipo_grafico == "Área":
                fig_main.add_trace(go.Scatter(
                    x=_mns, y=_yc, mode="lines", name=str(yr), fill="tozeroy",
                    line=dict(color=_c, width=1.5), fillcolor=_rgba(_c, 0.10),
                ))
            else:  # Línea (default)
                fig_main.add_trace(go.Scatter(
                    x=_mns, y=_yc, mode="lines+markers", name=str(yr),
                    line=dict(color=_c, width=1.5), marker=dict(size=4),
                ))
        fig_main.add_trace(go.Scatter(
            x=_mon_labels, y=_hist_cum.values, mode="lines", name="Media histórica",
            line=dict(color="#374151", width=2.5, dash="dash"),
        ))
        fig_main.update_layout(yaxis_title=f"{vlabel} acumulado", xaxis_title="Mes",
                               legend=dict(orientation="h", y=1.08, x=0))

    # ── G. COMPARACIÓN HISTÓRICA ──────────────────────────────
    elif tipo_analisis == "Comparación histórica":
        _p10m = raw_df.groupby("month")[col].quantile(0.10).reindex(_meses_presentes)
        _p50m = raw_df.groupby("month")[col].quantile(0.50).reindex(_meses_presentes)
        _p90m = raw_df.groupby("month")[col].quantile(0.90).reindex(_meses_presentes)
        _mxs  = _mon_labels
        fig_main.add_trace(go.Scatter(
            x=_mxs + _mxs[::-1],
            y=list(_p90m.values) + list(_p10m.values[::-1]),
            fill="toself", fillcolor=_rgba(vcolor, 0.12),
            line=dict(width=0), name="Rango P10–P90",
        ))
        fig_main.add_trace(go.Scatter(
            x=_mxs, y=_p50m.values, mode="lines", name="Mediana histórica",
            line=dict(color="#374151", width=2, dash="dash"),
        ))
        _lyd = raw_df[raw_df["year"] == end_yr].sort_values("month")
        _lyd = _lyd[_lyd["month"].isin(_meses_presentes)]
        if not _lyd.empty:
            if tipo_grafico == "Área":
                fig_main.add_trace(go.Scatter(
                    x=[_MON_NAMES[m - 1] for m in _lyd["month"].values],
                    y=_lyd[col].values,
                    mode="lines", name=str(end_yr), fill="tozeroy",
                    line=dict(color=vcolor, width=2.5),
                    fillcolor=_rgba(vcolor, 0.15),
                ))
            else:  # Línea (default)
                fig_main.add_trace(go.Scatter(
                    x=[_MON_NAMES[m - 1] for m in _lyd["month"].values],
                    y=_lyd[col].values,
                    mode="lines+markers", name=str(end_yr),
                    line=dict(color=vcolor, width=2.5),
                    marker=dict(size=7, color=vcolor, line=dict(color="white", width=1.5)),
                ))
        fig_main.update_layout(yaxis_title=vlabel, xaxis_title="Mes",
                               legend=dict(orientation="h", y=1.08, x=0))

    # ── H. RIESGO CLIMÁTICO ───────────────────────────────────
    elif tipo_analisis == "Riesgo climático":
        _clim_m  = raw_df.groupby("month")[col].mean().replace(0, float("nan"))
        _df_r    = raw_df.copy()
        _df_r["anom_pct"] = ((_df_r[col] - _df_r["month"].map(_clim_m))
                              / _df_r["month"].map(_clim_m) * 100)
        _pvt_r   = _df_r.pivot_table(values="anom_pct", index="year", columns="month", aggfunc="mean")
        _pvt_r   = _pvt_r.reindex(columns=_meses_presentes)
        _pvt_r.columns = [_MON_NAMES[m - 1] for m in _pvt_r.columns]
        if tipo_grafico == "Barras":
            _rsk_m  = _df_r.groupby("month")["anom_pct"].std().reindex(_meses_presentes)
            _mx_r   = float(_rsk_m.max()) if float(_rsk_m.max()) > 0 else 1.0
            _rc     = ["#ef4444" if v > _mx_r * 0.75 else
                       ("#f59e0b" if v > _mx_r * 0.5 else "#22c55e")
                       for v in _rsk_m.values]
            fig_main.add_trace(go.Bar(
                x=_mon_labels, y=_rsk_m.values,
                marker_color=_rc, name="Volatilidad (%)",
            ))
            fig_main.update_layout(yaxis_title="Volatilidad anomalía (%)", xaxis_title="Mes")
        else:  # Heatmap (default)
            fig_main = go.Figure(go.Heatmap(
                z=_pvt_r.values, x=_pvt_r.columns.tolist(), y=_pvt_r.index.tolist(),
                colorscale="RdBu_r", zmid=0,
                colorbar=dict(title="Anomalía (%)", len=0.8),
            ))
            fig_main.update_layout(yaxis_title="Año", xaxis_title="Mes")

    # ── Layout común ──────────────────────────────────────────
    fig_main.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        template="plotly_white", height=420,
        margin=dict(l=0, r=40, t=45, b=0),
    )
    st.plotly_chart(fig_main, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)



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
