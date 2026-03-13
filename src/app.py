"""
AgriPulse Argentina — Plataforma de Inteligencia Comercial
Nutrien Ag Solutions Argentina
Versión 2.0 | Stack: Streamlit 1.55 · Plotly 6.x · Pandas 2.3
"""

import io
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
from agripulse_engine import AgriPulseEngine

# ══════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AgriPulse Argentina | Nutrien Ag Solutions",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
# CSS — TEMA NUTRIEN
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── HEADER BAR ── */
.ap-header {
    background: linear-gradient(135deg, #00A34F 0%, #007A3D 60%, #005C2E 100%);
    padding: 1.2rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.2rem;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.ap-header h1 { margin: 0; font-size: 1.7rem; font-weight: 700; }
.ap-header p  { margin: 0; font-size: 0.9rem; opacity: 0.88; }

/* ── CARDS ── */
.ap-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ── KPI BOXES ── */
.kpi-box {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #00A34F;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #00A34F;
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.72rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}
.kpi-sub {
    font-size: 0.78rem;
    color: #9ca3af;
    margin-top: 0.15rem;
}

/* ── SECTION TITLES ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #00A34F;
    display: inline-block;
}
.section-subtitle {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 1rem;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #f9fafb;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.45rem 1rem;
    font-weight: 500;
    font-size: 0.82rem;
    color: #374151;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00A34F, #007A3D) !important;
    color: #fff !important;
    border-radius: 8px;
}

/* ── BADGES ── */
.badge-green {
    background: rgba(0,163,79,0.12);
    color: #00A34F;
    border: 1px solid rgba(0,163,79,0.3);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-amber {
    background: rgba(245,158,11,0.12);
    color: #b45309;
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-red {
    background: rgba(220,38,38,0.10);
    color: #dc2626;
    border: 1px solid rgba(220,38,38,0.25);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-blue {
    background: rgba(59,130,246,0.12);
    color: #2563eb;
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}

/* ── INFO / ALERT BOXES ── */
.info-box {
    background: rgba(0,163,79,0.07);
    border-left: 4px solid #00A34F;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.88rem;
    color: #1f2937;
    line-height: 1.6;
}
.alert-box {
    background: rgba(245,158,11,0.08);
    border-left: 4px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.88rem;
    color: #1f2937;
}

/* ── SOURCE TAGS ── */
.source-tag {
    background: #f3f4f6;
    color: #6b7280;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.72rem;
    font-family: monospace;
    display: inline-block;
    margin: 2px;
}

/* ── SIDEBAR DARK ── */
[data-testid="stSidebar"] {
    background-color: #1D1D1D !important;
}
[data-testid="stSidebar"] * {
    color: #F0F0F0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F0F0F0 !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #2d2d2d !important;
    border-color: #444 !important;
    color: #F0F0F0 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #444 !important;
}

/* ── NUTRIEN GREEN BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #00A34F, #007A3D);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.45rem 1.2rem;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #007A3D, #005C2E);
    box-shadow: 0 4px 12px rgba(0,163,79,0.3);
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: #fff;
    color: #00A34F;
    border: 2px solid #00A34F;
    border-radius: 8px;
    font-weight: 600;
}
.stDownloadButton > button:hover {
    background: #00A34F;
    color: #fff;
}

/* ── FOOTER ── */
.ap-footer {
    margin-top: 3rem;
    padding: 1.5rem 2rem;
    background: #f9fafb;
    border-top: 1px solid #e5e7eb;
    border-radius: 12px;
    font-size: 0.75rem;
    color: #9ca3af;
    text-align: center;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)


def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Business Case Argumentator", ln=1, align="C")
    pdf.multi_cell(0, 10, txt=text)
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# ══════════════════════════════════════════════════════════
# INICIALIZACIÓN DEL ENGINE
# ══════════════════════════════════════════════════════════
@st.cache_resource
def get_engine():
    return AgriPulseEngine()

engine = get_engine()


# ══════════════════════════════════════════════════════════
# FUNCIONES DE CACHÉ (ttl en segundos)
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def load_market(cultivo, provincia):
    return engine.get_market_potential(cultivo_filter=cultivo, provincia_filter=provincia)

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
    return engine.get_territorial_classification(cultivo=cultivo, periodo_anios=periodo)

@st.cache_data(ttl=7200)
def load_brecha(cultivo):
    return engine.get_technology_gap(cultivo=cultivo)

@st.cache_data(ttl=7200)
def load_priority_score(cultivo):
    return engine.get_commercial_priority_score(cultivo=cultivo)

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
# SIDEBAR — FILTROS GLOBALES + GUÍA
# ══════════════════════════════════════════════════════════
with st.sidebar:
    # Logo Nutrien
    st.markdown("""
    <div style="text-align:center; padding: 1.2rem 0 0.8rem 0;">
        <div style="font-size:2rem; font-weight:900; color:#00A34F; letter-spacing:-1px;">
            NUTRIEN
        </div>
        <div style="font-size:0.72rem; color:#aaa; letter-spacing:0.15em; text-transform:uppercase;">
            Ag Solutions Argentina
        </div>
        <div style="margin-top:0.5rem; padding:3px 12px; background:rgba(0,163,79,0.15);
                    border-radius:20px; display:inline-block; font-size:0.7rem; color:#00A34F;">
            AgriPulse v2.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Filtros Globales")

    cultivo_global = st.selectbox(
        "Cultivo principal",
        options=["Soja", "Maíz", "Trigo", "Girasol"],
        index=0,
        help="Filtra todos los módulos por este cultivo"
    )

    provincias_disponibles = sorted(engine._load_siia_data()['provincia'].unique().tolist())
    provincia_global = st.selectbox(
        "Provincia",
        options=["Todas"] + provincias_disponibles,
        index=0,
        help="Filtra por provincia (aplica a Potencial de Mercado)"
    )

    fecha_campana = st.date_input(
        "Fecha de referencia campaña",
        value=datetime.date(2025, 3, 13),
        help="Referencia temporal para cálculo fenológico"
    )

    st.divider()

    st.markdown("### Capas del Mapa")
    show_nutrien = st.checkbox("Mostrar sucursales Nutrien", value=True)
    show_competitors = st.checkbox("Mostrar competidores", value=False)

    st.divider()

    with st.expander("📖 Guía de uso"):
        st.markdown("""
        **⭐ Priority Score** — Ranking de departamentos por score comercial compuesto 0-100.

        **🗺️ Oportunidad & Territorio** — Potencial de mercado de fertilizantes y clasificación territorial por CAGR de área.

        **📊 Ratio Insumo/Grano** — Evolución histórica del ratio precio fertilizante / precio grano. Identifica ventanas de compra.

        **🌡️ Clima & Producción** — Condiciones climáticas actuales via NASA POWER y correlación histórica clima-rendimiento con análisis ENSO.

        **⚡ Pulso de Campaña** — Estado actual de siembra y cosecha 2024/25 según BCR + consumo de fertilizantes CIAFA 2015-2024.

        **🎯 Simulador** — Escenarios reactivos de demanda y valor de mercado bajo distintos precios de granos y fertilizantes.
        """)

    with st.expander("📚 Glosario"):
        st.markdown("""
        **GDD** — Grados Día de Desarrollo. Suma de (Tmed – Tbase) diarias. Determina estadio fenológico.

        **Ratio** — kg de grano necesarios para comprar 1 kg de fertilizante. Ratio bajo = fertilizante barato en términos de grano.

        **MAP** — Fosfato Monoamónico (11-52-0). Fertilizante fosfatado clave en siembra de soja.

        **MOP** — Cloruro de Potasio (0-0-60). Fuente de potasio.

        **V6** — Estadio vegetativo de maíz: 6 hojas desplegadas. Ventana óptima para fertilización nitrogenada.

        **SIIA** — Sistema Integrado de Información Agropecuaria. MAGyP Argentina. Superficies y rindes oficiales.

        **BCR** — Bolsa de Comercio de Rosario. Publica avance de siembra y cosecha semanalmente.

        **CIAFA** — Cámara de la Industria Argentina de Fertilizantes. Estadísticas de consumo y precios.

        **CAGR** — Compound Annual Growth Rate. Tasa de crecimiento anual compuesta de la superficie sembrada.

        **ENSO** — El Niño-Oscilación del Sur. Fenómeno climático que afecta precipitaciones en Argentina.
        """)

    with st.expander("🗂️ Fuentes de datos"):
        st.markdown("""
        | Dato | Fuente |
        |------|--------|
        | Superficies sembradas | SIIA / MAGyP |
        | Dosis técnicas | INTA EEA Marcos Juárez |
        | Clima actual | NASA POWER API |
        | Precios fertilizantes | CIAFA / Mercado Marzo 2025 |
        | Precios granos | MATBA-ROFEX / Marzo 2025 |
        | Avance campaña | BCR 2024/25 |
        | Correlación ENSO | NOAA CPC |
        """)

    st.divider()
    st.markdown("""
    <div style="font-size:0.7rem; color:#666; text-align:center;">
        Última actualización<br>
        <strong>Marzo 2025</strong><br>
        AgriPulse · Nutrien Ag Solutions
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════
today_str = datetime.date.today().strftime("%d/%m/%Y")
st.markdown(f"""
<div class="ap-header">
    <div style="font-size:2.5rem;">🌱</div>
    <div>
        <h1>AgriPulse Argentina</h1>
        <p>Plataforma de Inteligencia Comercial · Nutrien Ag Solutions Argentina</p>
    </div>
    <div style="margin-left:auto; text-align:right;">
        <span class="badge-green">Campaña 2024/25</span><br>
        <span style="font-size:0.78rem; opacity:0.8; margin-top:4px; display:block;">
            {today_str} · {cultivo_global} · {provincia_global}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ══════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⭐ Priority Score",
    "🗺️ Oportunidad & Territorio",
    "📊 Ratio Insumo/Grano",
    "🌡️ Clima & Producción",
    "⚡ Pulso de Campaña",
    "🎯 Simulador",
])


# ══════════════════════════════════════════════════════════
# TAB 1 — PRIORITY SCORE
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-title">⭐ Score de Prioridad Comercial</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-subtitle">Ranking 0-100 por departamento · Combina demanda, tendencia territorial, brecha tecnológica, precio de mercado, clima y producción</p>',
        unsafe_allow_html=True
    )

    with st.expander("ℹ️ ¿Qué es el Priority Score y cómo se usa?"):
        st.markdown("""
        El **Priority Score** es un índice compuesto que combina 6 dimensiones para indicarle al vendedor **dónde conviene focalizar el esfuerzo comercial** de forma objetiva.

        | Componente | Qué mide | Peso base |
        |---|---|---|
        | 🏭 Demanda potencial | Cuántas toneladas de fertilizante puede absorber la zona (ha × dosis INTA) | 25% |
        | 📈 Clasificación territorial | Si la superficie sembrada está creciendo (EXPANSIÓN) o cayendo (CONTRACCIÓN) | 20% |
        | ⚡ Brecha tecnológica | Cuánto rinde la zona por debajo del potencial INTA (mayor brecha = más upside) | 20% |
        | 💰 Ratio insumo/grano | Si el fertilizante está caro o barato respecto al grano (percentil histórico) | 15% |
        | 🌡️ Clima | Condición climática actual (ENSO) y su efecto histórico sobre el rendimiento | 10% |
        | 📊 Tendencia rendimiento | Si los rindes de los últimos 5 años subieron o bajaron | 10% |

        **Cómo leer el score:**
        - **≥75** — Prioridad ALTA. Zona con alta demanda, tecnología rezagada y momento de mercado favorable.
        - **50-74** — Prioridad MEDIA. Oportunidad sólida, pero al menos un factor limita el potencial.
        - **<50** — Prioridad BAJA. Zona madura, saturada o con ratio desfavorable.

        Podés ajustar los pesos en el panel **"⚖️ Personalizar pesos"** para reflejar la estrategia comercial de tu equipo.
        """)

    with st.spinner("Calculando scores comerciales..."):
        try:
            score_df_base, score_meta = load_priority_score(cultivo_global)
        except Exception as e:
            st.error(f"Error al calcular Priority Score: {e}")
            st.stop()

    if score_df_base.empty:
        st.info("Sin datos para esta selección.")
        st.stop()

    # ── FILTROS Y PESOS ──────────────────────────────────
    ps_f1, ps_f2, ps_f3 = st.columns([2, 2, 2])
    with ps_f1:
        _provs_ps = ["Todas"] + sorted(score_df_base['provincia'].unique().tolist())
        prov_ps = st.selectbox("Provincia", _provs_ps, key="ps_prov")
    with ps_f2:
        min_score_ps = st.slider("Score mínimo", min_value=0, max_value=90, value=0, step=5, key="ps_min")
    with ps_f3:
        _cls_opts = ["Todas", "EXPANSIÓN", "MADUREZ", "CONTRACCIÓN", "EMERGENTE"]
        cls_filter_ps = st.selectbox("Clasificación territorial", _cls_opts, key="ps_cls")

    with st.expander("⚖️ Personalizar pesos del score (deben sumar 100%)"):
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
            st.warning(f"⚠️ Los pesos suman {total_w}%. Deben sumar exactamente 100% para aplicar. Se usarán los pesos base.")
            weights = (0.25, 0.20, 0.20, 0.15, 0.10, 0.10)
        else:
            weights = (w_dem/100, w_terr/100, w_brech/100, w_ratio/100, w_clima/100, w_tend/100)
            st.success(f"✓ Pesos personalizados aplicados (suma = {total_w}%)")

    # Aplicar pesos y filtros
    score_df = score_df_base.copy()
    score_df['score_final'] = (
        score_df['score_demanda']    * weights[0] +
        score_df['score_territorial']* weights[1] +
        score_df['score_brecha']     * weights[2] +
        score_df['score_ratio']      * weights[3] +
        score_df['score_clima']      * weights[4] +
        score_df['score_tendencia']  * weights[5]
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

    # ── KPI ROW ──────────────────────────────────────────
    kc1, kc2, kc3, kc4 = st.columns(4)

    top_row = score_df.iloc[0]
    avg_score = score_df['score_final'].mean()
    top_score = score_df['score_final'].max()
    n_deptos = len(score_df)

    ratio_pct = score_meta['percentil_ratio']
    if ratio_pct < 30:
        momento_badge = '<span class="badge-green">🟢 Momento COMPRA</span>'
    elif ratio_pct < 60:
        momento_badge = '<span class="badge-amber">🟡 Momento NEUTRO</span>'
    else:
        momento_badge = '<span class="badge-red">🔴 Ratio ELEVADO</span>'

    with kc1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{n_deptos}</div>
            <div class="kpi-label">Departamentos analizados</div>
            <div class="kpi-sub">{cultivo_global} · todos</div>
        </div>
        """, unsafe_allow_html=True)
    with kc2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{avg_score:.1f}</div>
            <div class="kpi-label">Score promedio</div>
            <div class="kpi-sub">0-100 escala compuesta</div>
        </div>
        """, unsafe_allow_html=True)
    with kc3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{top_score:.0f}</div>
            <div class="kpi-label">Score máximo</div>
            <div class="kpi-sub">{top_row['departamento']}, {top_row['provincia']}</div>
        </div>
        """, unsafe_allow_html=True)
    with kc4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value" style="font-size:1.1rem;">{momento_badge}</div>
            <div class="kpi-label">Momento de mercado</div>
            <div class="kpi-sub">Ratio percentil {ratio_pct}° histórico</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── MAIN: MAP + RANKING ───────────────────────────────
    col_map, col_table = st.columns([6, 4])

    with col_map:
        st.markdown('<p class="section-title">Mapa de Prioridad</p>', unsafe_allow_html=True)

        fig_map = px.scatter_map(
            score_df,
            lat='lat', lon='lon',
            size='score_final',
            color='score_final',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100],
            size_max=30,
            zoom=4,
            center={'lat': -34.0, 'lon': -63.0},
            map_style='carto-positron',
            hover_name='departamento',
            hover_data={
                'provincia': True,
                'score_final': ':.1f',
                'clasificacion': True,
                'demanda_total_tn': ':,.0f',
                'lat': False,
                'lon': False,
            },
            labels={
                'score_final': 'Score',
                'demanda_total_tn': 'Demanda (tn)',
                'clasificacion': 'Clasificación',
            },
            title=f"Prioridad Comercial — {cultivo_global}",
        )
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            template='plotly_white',
            height=480,
            margin=dict(l=0, r=0, t=36, b=0),
            coloraxis_colorbar=dict(
                title="Score",
                thickness=12,
                len=0.6,
            ),
        )
        st.plotly_chart(fig_map, width='stretch')

    with col_table:
        st.markdown('<p class="section-title">Ranking de Departamentos</p>', unsafe_allow_html=True)

        table_df = score_df[['rank', 'departamento', 'provincia', 'score_final',
                              'demanda_total_tn', 'clasificacion', 'brecha_pct']].copy()
        table_df.columns = ['Rank', 'Depto', 'Prov', 'Score', 'Demanda (tn)', 'Clasificación', 'Brecha%']
        table_df['Demanda (tn)'] = table_df['Demanda (tn)'].apply(lambda x: f"{x:,.0f}")
        table_df['Score'] = table_df['Score'].apply(lambda x: f"{x:.1f}")
        table_df['Brecha%'] = table_df['Brecha%'].apply(
            lambda x: f"{x:.0f}%" if pd.notna(x) else "—"
        )

        def style_score_row(row):
            rank = int(row['Rank'])
            if rank <= 10:
                return ['background-color: rgba(0,163,79,0.10)'] * len(row)
            elif rank > len(table_df) - 10:
                return ['background-color: rgba(220,38,38,0.08)'] * len(row)
            return [''] * len(row)

        styled = table_df.style.apply(style_score_row, axis=1)
        st.dataframe(styled, height=460, width='stretch')

    # ── DETALLE DE DEPARTAMENTO ───────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-title">Detalle de Departamento</p>', unsafe_allow_html=True)

    depto_options = score_df['departamento'].tolist()
    depto_sel = st.selectbox("Ver detalle de departamento", options=depto_options, index=0)

    row_sel = score_df[score_df['departamento'] == depto_sel].iloc[0]

    dcol1, dcol2 = st.columns([1, 1])

    with dcol1:
        # Radar chart
        s_dem   = float(row_sel.get('score_demanda', 50))
        s_terr  = float(row_sel.get('score_territorial', 50))
        s_brech = float(row_sel.get('score_brecha', 50))
        s_ratio = float(row_sel.get('score_ratio', 50))
        s_clim  = float(row_sel.get('score_clima', 50))
        s_tend  = float(row_sel.get('score_tendencia', 50))

        fig_radar = go.Figure(go.Scatterpolar(
            r=[s_dem, s_terr, s_brech, s_ratio, s_clim, s_tend],
            theta=['Demanda', 'Territorial', 'Brecha Tech.', 'Ratio Mercado', 'Clima', 'Tendencia'],
            fill='toself',
            fillcolor='rgba(0,163,79,0.15)',
            line=dict(color='#00A34F', width=2),
            name=depto_sel,
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9)),
                angularaxis=dict(tickfont=dict(size=10)),
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            margin=dict(l=40, r=40, t=50, b=20),
            title=dict(text=f"Perfil de Score — {depto_sel}", font=dict(size=13)),
            showlegend=False,
        )
        st.plotly_chart(fig_radar, width='stretch')

    with dcol2:
        # Argumento de venta
        argumento = row_sel.get('argumento_venta', '')
        clasificacion_badge = {
            'EXPANSIÓN': 'badge-green',
            'MADUREZ': 'badge-amber',
            'CONTRACCIÓN': 'badge-red',
            'EMERGENTE': 'badge-blue',
        }.get(str(row_sel.get('clasificacion', '')), 'badge-amber')

        st.markdown(f"""
        <div class="ap-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                <strong style="font-size:1rem;">{depto_sel}</strong>
                <span class="{clasificacion_badge}">{row_sel.get('clasificacion', '—')}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-bottom:0.8rem;">
                <div><span class="kpi-label">Score Final</span><br>
                     <strong style="color:#00A34F; font-size:1.4rem;">{row_sel['score_final']:.1f}/100</strong></div>
                <div><span class="kpi-label">Ranking</span><br>
                     <strong style="font-size:1.4rem;">#{int(row_sel['rank'])}</strong></div>
                <div><span class="kpi-label">Demanda potencial</span><br>
                     <strong>{row_sel.get('demanda_total_tn', 0):,.0f} tn</strong></div>
                <div><span class="kpi-label">Brecha tecnológica</span><br>
                     <strong>{row_sel.get('brecha_pct', 0):.0f}%</strong></div>
            </div>
            <div class="info-box">
                <strong>Argumento de venta:</strong><br>{argumento}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── EXPORTAR EXCEL ────────────────────────────────────
    st.markdown("---")
    export_df = score_df[['rank', 'departamento', 'provincia', 'score_final',
                           'score_demanda', 'score_territorial', 'score_brecha',
                           'score_ratio', 'score_clima', 'score_tendencia',
                           'demanda_total_tn', 'clasificacion', 'brecha_pct',
                           'argumento_venta']].copy()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Priority Score')
    st.download_button(
        label="📥 Exportar a Excel",
        data=buffer.getvalue(),
        file_name=f"agripulse_priority_{cultivo_global.lower()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ══════════════════════════════════════════════════════════
# TAB 2 — OPORTUNIDAD & TERRITORIO
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">🗺️ Oportunidad & Territorio</p>', unsafe_allow_html=True)

    subtab_a, subtab_b = st.tabs(["📊 Mapa de Potencial de Mercado", "🗂️ Clasificación Territorial"])

    # ── SUB-TAB A: POTENCIAL DE MERCADO ──────────────────
    with subtab_a:
        st.markdown('<p class="section-subtitle">Demanda potencial de fertilizantes por departamento (SIIA/MAGyP + INTA)</p>', unsafe_allow_html=True)

        with st.expander("ℹ️ ¿Cómo se calcula la demanda potencial?"):
            st.markdown("""
            **Fórmula:**
            ```
            Demanda potencial (tn) = Superficie sembrada (ha) × Dosis técnica INTA (kg/ha) ÷ 1,000
            ```
            Las **dosis técnicas INTA** representan la fertilización recomendada para rendimiento óptimo:
            | Fertilizante | Soja | Maíz | Trigo | Girasol |
            |---|---|---|---|---|
            | Urea (kg/ha) | 0 | 180 | 150 | 80 |
            | MAP (kg/ha) | 90 | 80 | 100 | 80 |
            | MOP (kg/ha) | 70 | 60 | 0 | 0 |

            El **tamaño de burbuja** en el mapa = toneladas de fertilizante que puede absorber el departamento.
            El **color** = valor en millones de USD.

            **Importante:** Esta es la demanda *potencial máxima*. La demanda real depende de la adopción tecnológica del productor (tipicamente 65-90% de la dosis recomendada).
            """)


        fa_col1, fa_col2, fa_col3 = st.columns(3)
        with fa_col1:
            cultivos_opts_mkt = ["Todos", "Soja", "Maíz", "Trigo", "Girasol"]
            default_mkt_idx = cultivos_opts_mkt.index(cultivo_global) if cultivo_global in cultivos_opts_mkt else 1
            cultivo_mkt = st.selectbox("Cultivo", cultivos_opts_mkt,
                                       index=default_mkt_idx,
                                       key="mkt_cultivo")
        with fa_col2:
            _sup_df = engine._load_siia_data()
            prov_opts_mkt = ["Todas"] + sorted(_sup_df['provincia'].unique().tolist())
            prov_mkt_idx = prov_opts_mkt.index(provincia_global) if provincia_global in prov_opts_mkt else 0
            prov_mkt = st.selectbox("Provincia", prov_opts_mkt,
                                    index=prov_mkt_idx,
                                    key="mkt_prov")
        with fa_col3:
            fert_opts = ["Todos"] + list(engine.FERTILIZER_PRICES.keys())
            fert_mkt = st.selectbox("Fertilizante", fert_opts, key="mkt_fert")

        with st.spinner("Cargando datos de mercado..."):
            result_df, map_df = load_market(cultivo_mkt, prov_mkt)

        if result_df.empty:
            st.info("Sin datos para esta selección.")
        else:
            if fert_mkt != "Todos":
                result_filt = result_df[result_df['fertilizante'] == fert_mkt]
            else:
                result_filt = result_df

            # Reagrupar mapa
            map_filt = (
                result_filt.groupby(['provincia', 'departamento', 'lat', 'lon', 'area_ha'])
                .agg(
                    demanda_total_tn=('demanda_potencial_tn', 'sum'),
                    valor_total_musd=('valor_mercado_musd', 'sum'),
                ).reset_index()
            )

            # KPI row
            total_dem = result_filt['demanda_potencial_tn'].sum()
            total_val = result_filt['valor_mercado_musd'].sum()
            n_deptos_mkt = map_filt['departamento'].nunique()

            mk1, mk2, mk3, mk4 = st.columns(4)
            with mk1:
                st.markdown(f"""<div class="kpi-box">
                    <div class="kpi-value">{map_filt['area_ha'].sum():,.0f}</div>
                    <div class="kpi-label">Hectáreas (ha)</div>
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

            st.markdown("")

            px.set_mapbox_access_token(st.secrets["MAPBOX_TOKEN"])
            fig_mkt = px.scatter_mapbox(
                map_filt,
                lat='lat', lon='lon',
                size='demanda_total_tn',
                color='valor_total_musd',
                color_continuous_scale='Greens',
                size_max=15,
                zoom=4,
                center={'lat': -34.0, 'lon': -63.0},
                hover_name='departamento',
                hover_data={
                    'provincia': True,
                    'demanda_total_tn': ':,.0f',
                    'valor_total_musd': ':.2f',
                    'area_ha': ':,.0f',
                    'lat': False,
                    'lon': False,
                },
                labels={
                    'demanda_total_tn': 'Demanda (tn)',
                    'valor_total_musd': 'Valor (M USD)',
                    'area_ha': 'Área (ha)',
                },
                title=f"Potencial de Mercado — {cultivo_mkt} · {fert_mkt}",
            )

            if show_nutrien:
                nutrien_locs = pd.read_csv('data/nutrien_locations.csv')
                fig_mkt.add_trace(go.Scattermapbox(
                    lat=nutrien_locs['lat'],
                    lon=nutrien_locs['lon'],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=10,
                        color='green',
                        opacity=0.8
                    ),
                    hoverinfo='text',
                    text=nutrien_locs['localidad'],
                    name='Nutrien'
                ))

            if show_competitors:
                competitor_locs = pd.read_csv('data/competitor_locations.csv')
                fig_mkt.add_trace(go.Scattermapbox(
                    lat=competitor_locs['lat'],
                    lon=competitor_locs['lon'],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=10,
                        color='red',
                        opacity=0.8
                    ),
                    hoverinfo='text',
                    text=competitor_locs['localidad'],
                    name='Competencia'
                ))

            fig_mkt.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white',
                height=460,
                margin=dict(l=0, r=0, t=36, b=0),
            )
            st.plotly_chart(fig_mkt, width='stretch')

            # Top 15 departamentos
            top15 = (
                map_filt.sort_values('demanda_total_tn', ascending=False)
                .head(15)[['departamento', 'provincia', 'area_ha', 'demanda_total_tn', 'valor_total_musd']]
                .rename(columns={
                    'departamento': 'Departamento',
                    'provincia': 'Provincia',
                    'area_ha': 'Área (ha)',
                    'demanda_total_tn': 'Demanda (tn)',
                    'valor_total_musd': 'Valor (M USD)',
                })
            )
            top15['Área (ha)'] = top15['Área (ha)'].apply(lambda x: f"{x:,.0f}")
            top15['Demanda (tn)'] = top15['Demanda (tn)'].apply(lambda x: f"{x:,.0f}")
            top15['Valor (M USD)'] = top15['Valor (M USD)'].apply(lambda x: f"$ {x:.2f}M")

            st.markdown('<p class="section-title">Top 15 Departamentos por Demanda</p>', unsafe_allow_html=True)
            st.dataframe(top15, width='stretch', hide_index=True)

            # Argumento comercial
            if not map_filt.empty:
                top_dept = map_filt.sort_values('demanda_total_tn', ascending=False).iloc[0]
                st.markdown(f"""
                <div class="info-box">
                    <strong>Argumento Comercial:</strong><br>
                    <strong>{top_dept['departamento']}</strong> ({top_dept['provincia']}) es el departamento con mayor demanda potencial:
                    <strong>{top_dept['demanda_total_tn']:,.0f} tn</strong> de fertilizante valoradas en
                    <strong>USD {top_dept['valor_total_musd']:.2f}M</strong>.
                    Con <strong>{top_dept['area_ha']:,.0f} ha</strong> sembradas de {cultivo_mkt},
                    existe una oportunidad comercial significativa para maximizar captura de mercado.
                </div>
                """, unsafe_allow_html=True)

    # ── SUB-TAB B: CLASIFICACIÓN TERRITORIAL ─────────────
    with subtab_b:
        st.markdown('<p class="section-subtitle">Clasificación departamental por CAGR de área sembrada · Proyección 2026/27</p>', unsafe_allow_html=True)

        periodo_sel = st.radio(
            "Período de análisis",
            options=[5, 10, 20],
            format_func=lambda x: f"{x} años",
            horizontal=True,
            index=1,
        )

        with st.spinner("Calculando clasificación territorial..."):
            terr_df, hist_df, conteos = load_territorial(cultivo_global, periodo_sel)

        if terr_df.empty:
            st.info("Sin datos de clasificación territorial. Verificar CSVs SIIA.")
        else:
            # Badges por clasificación
            bcol1, bcol2, bcol3, bcol4 = st.columns(4)
            badge_info = [
                ('EXPANSIÓN', 'badge-green', '🟢'),
                ('MADUREZ', 'badge-amber', '🟡'),
                ('CONTRACCIÓN', 'badge-red', '🔴'),
                ('EMERGENTE', 'badge-blue', '🔵'),
            ]
            for col, (cls, badge_cls, ico) in zip([bcol1, bcol2, bcol3, bcol4], badge_info):
                cnt = conteos.get(cls, 0)
                with col:
                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-value" style="font-size:1.5rem;">{cnt}</div>
                        <div class="kpi-label">{ico} {cls}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("")

            # Mapa territorial
            color_map_terr = {
                'EXPANSIÓN': '#00A34F',
                'MADUREZ': '#f59e0b',
                'CONTRACCIÓN': '#dc2626',
                'EMERGENTE': '#3b82f6',
            }

            fig_terr = px.scatter_map(
                terr_df,
                lat='lat', lon='lon',
                size='ha_actual',
                color='clasificacion',
                color_discrete_map=color_map_terr,
                size_max=35,
                zoom=4,
                center={'lat': -34.0, 'lon': -63.0},
                map_style='carto-positron',
                hover_name='departamento',
                hover_data={
                    'provincia': True,
                    'clasificacion': True,
                    'cagr_pct': ':.1f',
                    'ha_actual': ':,.0f',
                    'proj_2026': ':,.0f',
                    'r2': ':.2f',
                    'lat': False,
                    'lon': False,
                },
                labels={
                    'cagr_pct': 'CAGR (%)',
                    'ha_actual': 'Área actual (ha)',
                    'proj_2026': 'Proyección 2026 (ha)',
                    'r2': 'R²',
                },
                title=f"Clasificación Territorial — {cultivo_global} · {periodo_sel} años",
            )
            fig_terr.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white',
                height=460,
                margin=dict(l=0, r=0, t=36, b=0),
            )
            st.plotly_chart(fig_terr, width='stretch')

            # Selector departamento → serie histórica + proyección
            st.markdown('<p class="section-title">Serie Histórica + Proyección por Departamento</p>', unsafe_allow_html=True)

            dept_terr_opts = terr_df['departamento'].tolist()
            if dept_terr_opts:
                dept_terr_sel = st.selectbox("Departamento", options=dept_terr_opts, key="terr_dept_sel")

                dept_row = terr_df[terr_df['departamento'] == dept_terr_sel].iloc[0]
                dept_hist = hist_df[
                    (hist_df['departamento'] == dept_terr_sel) &
                    (hist_df['provincia'] == dept_row['provincia'])
                ].sort_values('año')

                if not dept_hist.empty:
                    fig_hist = go.Figure()

                    # Serie histórica
                    fig_hist.add_trace(go.Scatter(
                        x=dept_hist['año'],
                        y=dept_hist['sup_sembrada_ha'],
                        mode='lines+markers',
                        name='Superficie histórica',
                        line=dict(color='#00A34F', width=2),
                        marker=dict(size=5),
                    ))

                    # Proyección 2026/27
                    last_year = int(dept_hist['año'].max())
                    last_val = float(dept_hist[dept_hist['año'] == last_year]['sup_sembrada_ha'].values[0])
                    proj_2026 = int(dept_row['proj_2026'])
                    proj_2027 = int(dept_row['proj_2027'])
                    ci95 = int(dept_row['ci95'])

                    proj_x = [last_year, 2026, 2027]
                    proj_y = [last_val, proj_2026, proj_2027]

                    # Banda de confianza
                    fig_hist.add_trace(go.Scatter(
                        x=[2026, 2027, 2027, 2026],
                        y=[proj_2026 + ci95, proj_2027 + ci95, proj_2027 - ci95, proj_2026 - ci95],
                        fill='toself',
                        fillcolor='rgba(0,163,79,0.12)',
                        line=dict(color='rgba(0,0,0,0)'),
                        name='IC 95%',
                        showlegend=True,
                    ))

                    # Línea proyección
                    fig_hist.add_trace(go.Scatter(
                        x=proj_x, y=proj_y,
                        mode='lines+markers',
                        name='Proyección',
                        line=dict(color='#00A34F', width=2, dash='dash'),
                        marker=dict(size=8, symbol='diamond'),
                    ))

                    fig_hist.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        template='plotly_white',
                        height=320,
                        title=f"{dept_terr_sel} — {cultivo_global} (ha sembradas 2000-2027)",
                        xaxis_title="Campaña",
                        yaxis_title="Hectáreas",
                        legend=dict(orientation='h', y=-0.15),
                        margin=dict(l=0, r=0, t=40, b=0),
                    )
                    st.plotly_chart(fig_hist, width='stretch')

                    # Info card con R²
                    r2_val = dept_row['r2']
                    cagr_val = dept_row['cagr_pct']
                    cls_val = dept_row['clasificacion']
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>{dept_terr_sel}</strong> · Clasificación: <strong>{cls_val}</strong> ·
                        CAGR {periodo_sel}a: <strong>{cagr_val:+.1f}%</strong> ·
                        R² ajuste lineal: <strong>{r2_val:.3f}</strong> ·
                        Proyección 2026: <strong>{proj_2026:,} ha</strong> ±{ci95:,} · 2027: <strong>{proj_2027:,} ha</strong>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Sin datos históricos para este departamento.")

            # Tablas expansión / contracción
            st.markdown("---")
            tcol1, tcol2 = st.columns(2)

            with tcol1:
                st.markdown('<p class="section-title">🟢 Top 10 Expansión</p>', unsafe_allow_html=True)
                exp_df = (terr_df[terr_df['clasificacion'] == 'EXPANSIÓN']
                          .nlargest(10, 'cagr_pct')
                          [['departamento', 'provincia', 'cagr_pct', 'ha_actual', 'proj_2026']])
                if exp_df.empty:
                    st.info("Sin departamentos en expansión.")
                else:
                    exp_df = exp_df.copy()
                    exp_df.columns = ['Depto', 'Prov', 'CAGR (%)', 'Área actual (ha)', 'Proy. 2026 (ha)']
                    exp_df['CAGR (%)'] = exp_df['CAGR (%)'].apply(lambda x: f"+{x:.1f}%")
                    exp_df['Área actual (ha)'] = exp_df['Área actual (ha)'].apply(lambda x: f"{x:,.0f}")
                    exp_df['Proy. 2026 (ha)'] = exp_df['Proy. 2026 (ha)'].apply(lambda x: f"{x:,.0f}")
                    st.dataframe(exp_df, width='stretch', hide_index=True)

            with tcol2:
                st.markdown('<p class="section-title">🔴 Top 10 Contracción</p>', unsafe_allow_html=True)
                con_df = (terr_df[terr_df['clasificacion'] == 'CONTRACCIÓN']
                          .nsmallest(10, 'cagr_pct')
                          [['departamento', 'provincia', 'cagr_pct', 'ha_actual', 'proj_2026']])
                if con_df.empty:
                    st.info("Sin departamentos en contracción.")
                else:
                    con_df = con_df.copy()
                    con_df.columns = ['Depto', 'Prov', 'CAGR (%)', 'Área actual (ha)', 'Proy. 2026 (ha)']
                    con_df['CAGR (%)'] = con_df['CAGR (%)'].apply(lambda x: f"{x:.1f}%")
                    con_df['Área actual (ha)'] = con_df['Área actual (ha)'].apply(lambda x: f"{x:,.0f}")
                    con_df['Proy. 2026 (ha)'] = con_df['Proy. 2026 (ha)'].apply(lambda x: f"{x:,.0f}")
                    st.dataframe(con_df, width='stretch', hide_index=True)


# ══════════════════════════════════════════════════════════
# TAB 3 — RATIO INSUMO / GRANO
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-title">📊 Ratio Insumo/Grano</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">kg de grano necesarios para comprar 1 kg de fertilizante · Menor ratio = mejor momento de compra</p>', unsafe_allow_html=True)

    with st.expander("ℹ️ ¿Cómo leer el ratio insumo/grano?"):
        st.markdown("""
        **El ratio responde a:** *"¿Cuántos kilos de grano tiene que vender el productor para comprar 1 kilo de fertilizante?"*

        **Fórmula:**
        ```
        Ratio = Precio fertilizante (USD/tn) ÷ Precio grano (USD/tn)
        ```

        **Ejemplo concreto:**
        - Urea = USD 480/tn · Soja = USD 345/tn → Ratio = 480 ÷ 345 = **1.39**
        - Significa: por cada kg de Urea, el productor necesita vender **1.39 kg de Soja**
        - Por una bolsa de 50 kg de Urea: **69.5 kg de Soja** (≈ USD 24)

        **Percentil histórico:**
        - **Percentil 20°**: el fertilizante es más barato que el 80% de los precios históricos desde 2020 → 🟢 **Momento de compra**
        - **Percentil 60°**: precio en rango normal → 🟡 **Neutro**
        - **Percentil 80°+**: fertilizante caro vs grano → 🔴 **Esperar o reducir dosis**

        **Por qué importa para Nutrien:** Un productor con ratio bajo compra más volumen porque su margen mejora. Identificar estos momentos y comunicarlos proactivamente es la diferencia entre cerrar o no una venta.
        """)

    rc1, rc2 = st.columns(2)
    with rc1:
        grain_opts = list(engine.GRAIN_PRICES.keys())
        grain_default_idx = grain_opts.index(cultivo_global) if cultivo_global in grain_opts else 0
        grain_sel = st.selectbox(
            "Grano de referencia",
            options=grain_opts,
            index=grain_default_idx,
            key="ratio_grain",
        )
    with rc2:
        fert_options_ratio = list(engine.FERTILIZER_PRICES.keys())
        default_fert = {'Maíz': 'Urea', 'Trigo': 'Urea', 'Soja': 'MAP', 'Girasol': 'Urea'}.get(grain_sel, 'Urea')
        fert_sel = st.selectbox(
            "Fertilizante",
            options=fert_options_ratio,
            index=fert_options_ratio.index(default_fert) if default_fert in fert_options_ratio else 0,
            key="ratio_fert",
        )

    with st.spinner("Cargando historial de ratios..."):
        hist_ratio_df, ratio_actual, ratio_pct_ratio = load_price_history(grain_sel, fert_sel)
        ratios_tabla = load_ratios()

    # Filtrar para grano y fert seleccionados
    ratio_row = ratios_tabla[
        (ratios_tabla['grano'] == grain_sel) &
        (ratios_tabla['fertilizante'] == fert_sel)
    ]
    ratio_actual_val = ratio_row['ratio'].values[0] if not ratio_row.empty else ratio_actual
    kg_bolsa = ratio_row['kg_grano_x_bolsa_50kg'].values[0] if not ratio_row.empty else round(ratio_actual * 50, 1)

    # KPI row
    precio_grano_base = engine.GRAIN_PRICES.get(grain_sel, 300)
    precio_fert_base  = engine.FERTILIZER_PRICES.get(fert_sel, 500)

    if ratio_pct_ratio < 30:
        momento_txt = "COMPRA — Ratio históricamente bajo"
        momento_badge_r = "badge-green"
        recom = "Momento muy favorable. El fertilizante está barato en relación al grano. Recomendamos anticipar compras."
    elif ratio_pct_ratio < 60:
        momento_txt = "NEUTRO — Ratio en rango normal"
        momento_badge_r = "badge-amber"
        recom = "Ratio dentro de rangos históricos normales. Comprar según necesidad operativa y flujo de caja."
    else:
        momento_txt = "ESPERAR — Ratio elevado"
        momento_badge_r = "badge-red"
        recom = "El fertilizante está caro en relación al grano. Si es posible, diferir compras o evaluar dosis alternativas."

    rk1, rk2, rk3, rk4 = st.columns(4)
    with rk1:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{ratio_actual_val:.2f}</div>
            <div class="kpi-label">Ratio actual</div>
            <div class="kpi-sub">kg {grain_sel} / kg {fert_sel}</div>
        </div>""", unsafe_allow_html=True)
    with rk2:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{ratio_pct_ratio}°</div>
            <div class="kpi-label">Percentil histórico</div>
            <div class="kpi-sub">desde 2020</div>
        </div>""", unsafe_allow_html=True)
    with rk3:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{kg_bolsa:.0f} kg</div>
            <div class="kpi-label">Por bolsa 50kg</div>
            <div class="kpi-sub">grano equivalente</div>
        </div>""", unsafe_allow_html=True)
    with rk4:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value" style="font-size:0.88rem;">
                <span class="{momento_badge_r}">{momento_txt}</span>
            </div>
            <div class="kpi-label">Señal de mercado</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Simulador de escenario de ratio
    # Variables inicializadas en valores base; el expander las sobreescribe si está abierto
    var_grano_pct    = 0
    var_fert_pct     = 0
    precio_grano_sim = precio_grano_base
    precio_fert_sim  = precio_fert_base
    ratio_sim        = ratio_actual_val

    with st.expander("🎛️ Simulador de escenario de ratio"):
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            var_grano_pct = st.slider(
                f"Variación precio {grain_sel} (%)",
                min_value=-30, max_value=30, value=0, step=5,
                key="sim_grano_ratio"
            )
        with sim_col2:
            var_fert_pct = st.slider(
                f"Variación precio {fert_sel} (%)",
                min_value=-30, max_value=30, value=0, step=5,
                key="sim_fert_ratio"
            )

        precio_grano_sim = precio_grano_base * (1 + var_grano_pct / 100)
        precio_fert_sim  = precio_fert_base  * (1 + var_fert_pct  / 100)
        ratio_sim = precio_fert_sim / max(precio_grano_sim, 1)

        ssim_c1, ssim_c2, ssim_c3 = st.columns(3)
        with ssim_c1:
            st.metric(f"Precio {grain_sel} sim.", f"USD {precio_grano_sim:.0f}/tn",
                      delta=f"{var_grano_pct:+.0f}%")
        with ssim_c2:
            st.metric(f"Precio {fert_sel} sim.", f"USD {precio_fert_sim:.0f}/tn",
                      delta=f"{var_fert_pct:+.0f}%")
        with ssim_c3:
            delta_ratio = ratio_sim - ratio_actual_val
            st.metric("Ratio simulado", f"{ratio_sim:.2f}",
                      delta=f"{delta_ratio:+.2f} vs actual")

    # Gráfico histórico del ratio
    fig_ratio = go.Figure()

    fig_ratio.add_trace(go.Scatter(
        x=hist_ratio_df['fecha'],
        y=hist_ratio_df['ratio'],
        mode='lines+markers',
        name='Ratio histórico',
        line=dict(color='#00A34F', width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(0,163,79,0.08)',
    ))

    # Línea ratio actual
    fig_ratio.add_hline(
        y=ratio_actual_val,
        line_dash='dash',
        line_color='#f59e0b',
        annotation_text=f"Actual: {ratio_actual_val:.2f}",
        annotation_position="top right",
    )

    # Línea ratio simulado (si hay variación)
    if var_grano_pct != 0 or var_fert_pct != 0:
        fig_ratio.add_hline(
            y=ratio_sim,
            line_dash='dot',
            line_color='#dc2626',
            annotation_text=f"Simulado: {ratio_sim:.2f}",
            annotation_position="bottom right",
        )

    fig_ratio.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_white',
        height=360,
        title=f"Ratio {grain_sel}/{fert_sel} — Evolución 2020-2025",
        xaxis_title="Período",
        yaxis_title=f"kg {grain_sel} / kg {fert_sel}",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_ratio, width='stretch')

    # Heatmap de todos los ratios actuales
    st.markdown('<p class="section-title">Mapa de Calor — Ratios Actuales</p>', unsafe_allow_html=True)

    # Pivot para heatmap
    heat_data = ratios_tabla.pivot(index='fertilizante', columns='grano', values='ratio')
    fig_heat = px.imshow(
        heat_data,
        color_continuous_scale='RdYlGn_r',
        text_auto='.2f',
        aspect='auto',
        title='Ratio Fertilizante/Grano (menor = más favorable para el productor)',
        labels=dict(color='Ratio'),
    )
    fig_heat.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_white',
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_heat, width='stretch')

    # Argumento comercial
    argumento_text = f"""El ratio {grain_sel}/{fert_sel} actual es {ratio_actual_val:.2f}, en el percentil {ratio_pct_ratio}° de su historia desde 2020.
    Cada bolsa de 50 kg de {fert_sel} equivale hoy a {kg_bolsa:.0f} kg de {grain_sel} (USD {precio_fert_base:.0f}/tn fert vs USD {precio_grano_base:.0f}/tn grano).

    Recomendación: {recom}"""

    st.markdown(f"""
    <div class="info-box">
        <strong>Argumento listo para usar:</strong><br>
        {argumento_text.replace(chr(10), "<br>")}
    </div>
    """, unsafe_allow_html=True)

    pdf_buffer = create_pdf(argumento_text)
    st.download_button(
        label="📥 Exportar a PDF",
        data=pdf_buffer,
        file_name=f"argumento_{grain_sel.lower()}_{fert_sel.lower()}.pdf",
        mime="application/pdf",
    )


# ══════════════════════════════════════════════════════════
# TAB 4 — CLIMA & PRODUCCIÓN
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">🌡️ Clima & Producción</p>', unsafe_allow_html=True)

    clim_sub_a, clim_sub_b = st.tabs(["🌦️ Clima Actual (NASA POWER)", "📈 Correlación Clima-Rendimiento"])

    # ── SUB-TAB A: CLIMA ACTUAL ───────────────────────────
    with clim_sub_a:
        st.markdown('<p class="section-subtitle">Datos climáticos en tiempo real via NASA POWER · Fallback: normales SMN/INTA</p>', unsafe_allow_html=True)

        # Date awareness banner
        _estado_actual = engine.get_estado_fenologico_actual(cultivo_global if cultivo_global in engine.ESTADO_ACTUAL_CULTIVOS else 'Maíz')
        _box_class = "alert-box" if not _estado_actual['ventana_activa'] else "info-box"
        _vent_icon = "⚠️" if not _estado_actual['ventana_activa'] else "✅"
        st.markdown(f"""
        <div class="{_box_class}">
            {_vent_icon} <strong>{cultivo_global} — Estadio actual (Marzo 2026):</strong>
            {_estado_actual['estadio']}<br>
            {_estado_actual['mensaje']}<br>
            <strong>Próxima ventana:</strong> {_estado_actual['proxima_ventana']}
        </div>
        """, unsafe_allow_html=True)

        zones_list = list(engine.ZONES.keys())
        zona_sel = st.selectbox("Zona de monitoreo", options=zones_list, key="clima_zona")
        zona_coords = engine.ZONES[zona_sel]
        lat_w, lon_w = zona_coords['lat'], zona_coords['lon']

        with st.spinner(f"Descargando datos climáticos — {zona_sel}..."):
            wx = load_weather(lat_w, lon_w)

        wx_df = wx['df']
        fuente_str = wx['fuente']
        fuente_badge = "badge-green" if wx.get('success', False) else "badge-amber"

        # KPI row climática
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
                <div class="kpi-value" style="font-size:0.72rem;">
                    <span class="{fuente_badge}">{fuente_str[:30]}</span>
                </div>
                <div class="kpi-label">Fuente de datos</div>
                <div class="kpi-sub">{lat_w:.2f}, {lon_w:.2f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Gráfico temperatura + precipitación
        fig_wx = go.Figure()

        fig_wx.add_trace(go.Scatter(
            x=wx_df['fecha'], y=wx_df['temp_c'],
            name='Temperatura (°C)',
            mode='lines',
            line=dict(color='#ef4444', width=2),
            yaxis='y1',
        ))

        fig_wx.add_trace(go.Bar(
            x=wx_df['fecha'], y=wx_df['precip_mm'],
            name='Precipitación (mm)',
            marker_color='rgba(59,130,246,0.6)',
            yaxis='y2',
        ))

        fig_wx.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            template='plotly_white',
            height=340,
            title=f"Temperatura y Precipitación — {zona_sel}",
            xaxis_title="Fecha",
            yaxis=dict(title="Temperatura (°C)", side='left', color='#ef4444'),
            yaxis2=dict(title="Precipitación (mm)", side='right', overlaying='y', color='#3b82f6'),
            legend=dict(orientation='h', y=1.1),
            margin=dict(l=0, r=0, t=50, b=0),
        )
        st.plotly_chart(fig_wx, width='stretch')

        # Fenología y GDD
        st.markdown("---")
        fcol1, fcol2 = st.columns(2)

        with fcol1:
            st.markdown('<p class="section-title">Estadio Fenológico</p>', unsafe_allow_html=True)
            crop_for_pheno = cultivo_global if cultivo_global in ('Maíz', 'Trigo') else 'Maíz'
            stage = engine.get_phenology_stage(crop_for_pheno, wx['gdd_acum'])

            gdd_targets = {
                'Maíz': [
                    (0, 'VE'), (100, 'V3'), (200, 'V6 ⭐'), (370, 'V10'),
                    (530, 'VT'), (670, 'R1'), (830, 'R2'), (1000, 'R4'), (1200, 'R6'),
                ],
                'Trigo': [
                    (0, 'Emerg.'), (150, 'Macollaje ⭐'), (350, 'Encañazón'),
                    (500, 'Espigazón'), (650, 'Antesis'), (900, 'Lechoso'), (1200, 'Madurez'),
                ],
            }
            targets = gdd_targets.get(crop_for_pheno, gdd_targets['Maíz'])
            max_gdd_crop = targets[-1][0]

            progress_pct = min(100, int(wx['gdd_acum'] / max_gdd_crop * 100))
            st.progress(progress_pct)
            st.markdown(f"""
            <div class="info-box">
                <strong>Cultivo:</strong> {crop_for_pheno}<br>
                <strong>GDD acumulados:</strong> {wx['gdd_acum']:.0f} de {max_gdd_crop} (máx ciclo)<br>
                <strong>Estadio actual:</strong> {stage}<br>
                <strong>Avance ciclo:</strong> {progress_pct}%
            </div>
            """, unsafe_allow_html=True)

        with fcol2:
            st.markdown('<p class="section-title">Hitos del Ciclo</p>', unsafe_allow_html=True)
            milestones_df = pd.DataFrame(targets, columns=['GDD', 'Estadio'])
            milestones_df['Alcanzado'] = milestones_df['GDD'].apply(
                lambda g: '✅' if wx['gdd_acum'] >= g else '⏳'
            )
            milestones_df['GDD'] = milestones_df['GDD'].apply(lambda x: f"{x:,}")
            st.dataframe(milestones_df, width='stretch', hide_index=True)

    # ── SUB-TAB B: CORRELACIÓN CLIMA-RENDIMIENTO ──────────
    with clim_sub_b:
        st.markdown('<p class="section-subtitle">Correlación histórica entre variable climática clave y rendimiento · Análisis ENSO 2000-2024</p>', unsafe_allow_html=True)

        with st.expander("ℹ️ ¿Por qué importa el clima para planificar ventas de fertilizantes?"):
            st.markdown("""
            **El rendimiento de los cultivos varía hasta ±30% según el año climático.** Esto impacta directamente en el ingreso del productor y en su predisposición a invertir en fertilización.

            **ENSO (El Niño / La Niña)** es el fenómeno climático de mayor impacto en Argentina:
            - **El Niño** → lluvias por encima de lo normal en la Pampa Húmeda → rendimientos altos → más margen para fertilizar
            - **La Niña** → sequía → rendimientos bajos → productores restringen gastos en insumos
            - **Neutro** → condiciones normales

            **Correlación de Pearson (r):**
            - `r > 0.5` → correlación fuerte: cuando llueve más, rinde más
            - `r < 0` → correlación inversa (raro en cultivos de verano, más común en trigo)

            **Cómo usar esto en ventas:** Si estamos en año Niño, el productor espera buenos rindes → argumentar inversión en dosis completa. Si es Niña, enfocar en eficiencia: "fertilizá menos pero fertilizá bien, la planta necesita lo que no da la lluvia."
            """)


        with st.spinner("Cargando correlación clima-producción..."):
            clim_corr = load_climate_corr(cultivo_global)

        corr_df    = clim_corr['df']
        var_clima  = clim_corr['variable_clima']
        pearson_r  = clim_corr['pearson_r']
        pendiente  = clim_corr['pendiente']
        intercepto = clim_corr['intercepto']
        enso_actual = clim_corr['enso_actual']

        if corr_df.empty:
            st.info("Sin datos de correlación para este cultivo.")
        else:
            # Scatter ENSO
            enso_colors = {
                'La Niña': '#00A34F',
                'El Niño': '#f59e0b',
                'neutro':  '#9ca3af',
            }

            fig_corr = go.Figure()

            for enso_type, color in enso_colors.items():
                subset = corr_df[corr_df['enso'] == enso_type]
                if subset.empty:
                    continue
                fig_corr.add_trace(go.Scatter(
                    x=subset['variable_clima'],
                    y=subset['rendimiento'],
                    mode='markers+text',
                    name=enso_type,
                    text=subset['año'].astype(str),
                    textposition='top center',
                    textfont=dict(size=8, color=color),
                    marker=dict(
                        color=color,
                        size=10,
                        line=dict(color='white', width=1),
                    ),
                ))

            # Línea de regresión
            x_vals = corr_df['variable_clima'].values
            x_lin = np.linspace(x_vals.min(), x_vals.max(), 50)
            y_lin = intercepto + pendiente * x_lin

            fig_corr.add_trace(go.Scatter(
                x=x_lin, y=y_lin,
                mode='lines',
                name=f'Regresión (r={pearson_r:.2f})',
                line=dict(color='#374151', width=1.5, dash='dash'),
            ))

            fig_corr.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white',
                height=420,
                title=f"Correlación Clima-Rendimiento — {cultivo_global}",
                xaxis_title=var_clima,
                yaxis_title="Rendimiento (tn/ha)",
                legend=dict(orientation='h', y=-0.15),
                margin=dict(l=0, r=0, t=40, b=60),
            )
            st.plotly_chart(fig_corr, width='stretch')

            # Pearson r interpretación
            abs_r = abs(pearson_r)
            if abs_r > 0.5:
                corr_label = "Correlación FUERTE"
                corr_badge = "badge-green" if pearson_r > 0 else "badge-red"
            elif abs_r > 0.3:
                corr_label = "Correlación MODERADA"
                corr_badge = "badge-amber"
            else:
                corr_label = "Correlación DÉBIL"
                corr_badge = "badge-red"

            corr_sign = "positiva" if pearson_r > 0 else "negativa"

            crr_c1, crr_c2 = st.columns([1, 2])
            with crr_c1:
                st.markdown(f"""
                <div class="ap-card" style="text-align:center;">
                    <div class="kpi-value" style="font-size:3rem; color:#00A34F;">{pearson_r:.2f}</div>
                    <div class="kpi-label">Pearson r</div>
                    <div style="margin-top:0.5rem;">
                        <span class="{corr_badge}">{corr_label}</span>
                    </div>
                    <div class="kpi-sub" style="margin-top:0.4rem;">Correlación {corr_sign}</div>
                </div>
                """, unsafe_allow_html=True)

            with crr_c2:
                # Panel ENSO actual
                enso_estado = enso_actual['estado']
                enso_oni = enso_actual['indice_oni']
                enso_prob = enso_actual['probabilidad']
                enso_imp_key = f"implicancia_{cultivo_global.lower()}"
                enso_imp = enso_actual.get(enso_imp_key, enso_actual.get('implicancia_soja', ''))

                # Badge ENSO
                if 'Niña' in enso_estado:
                    enso_badge_cls = "badge-green"
                elif 'Niño' in enso_estado:
                    enso_badge_cls = "badge-amber"
                else:
                    enso_badge_cls = "badge-blue"

                st.markdown(f"""
                <div class="ap-card">
                    <strong>Estado ENSO Actual</strong><br>
                    <span class="{enso_badge_cls}">{enso_estado}</span>
                    <span style="margin-left:0.5rem; font-size:0.8rem; color:#6b7280;">ONI: {enso_oni}</span>
                    <div style="margin-top:0.8rem; font-size:0.85rem; color:#374151;">
                        <strong>Implicancia para {cultivo_global}:</strong><br>
                        {enso_imp}
                    </div>
                    <div style="margin-top:0.6rem; font-size:0.78rem; color:#9ca3af;">
                        Prob. Neutro: {enso_prob['Neutro']}% ·
                        El Niño: {enso_prob['El Niño']}% ·
                        La Niña: {enso_prob['La Niña']}%
                        <br>Fuente: {enso_actual['fuente']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Stats ENSO
            st.markdown("---")
            if 'enso' in corr_df.columns and 'rendimiento' in corr_df.columns:
                nina_rend   = corr_df[corr_df['enso'] == 'La Niña']['rendimiento'].mean()
                nino_rend   = corr_df[corr_df['enso'] == 'El Niño']['rendimiento'].mean()
                neutro_rend = corr_df[corr_df['enso'] == 'neutro']['rendimiento'].mean()

                if neutro_rend > 0:
                    nina_delta  = (nina_rend  - neutro_rend) / neutro_rend * 100
                    nino_delta  = (nino_rend  - neutro_rend) / neutro_rend * 100
                else:
                    nina_delta = nino_delta = 0

                st.markdown(f"""
                <div class="info-box">
                    <strong>Resumen ENSO — {cultivo_global}</strong><br>
                    Años <strong>La Niña</strong>: rendimiento promedio <strong>{nina_rend:.2f} tn/ha</strong>
                    ({nina_delta:+.1f}% vs neutro) ·
                    Años <strong>El Niño</strong>: <strong>{nino_rend:.2f} tn/ha</strong>
                    ({nino_delta:+.1f}% vs neutro) ·
                    Años <strong>neutros</strong>: <strong>{neutro_rend:.2f} tn/ha</strong>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 5 — PULSO DE CAMPAÑA
# ══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-title">⚡ Pulso de Campaña 2024/25</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Avance semanal BCR · Consumo fertilizantes CIAFA 2015-2024 · Calendario de ventanas de fertilización</p>', unsafe_allow_html=True)

    # ── CALENDARIO DE VENTANAS DE FERTILIZACIÓN ──────────
    st.markdown('<p class="section-title">📅 Calendario de Ventanas de Fertilización</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-subtitle">Estado al día de hoy · Verde = ventana abierta ahora · Amarillo = próxima en &lt;60 días · Rojo = cerrada esta campaña</p>',
        unsafe_allow_html=True
    )

    vent_df, vent_meta = engine.get_ventanas_fertilizacion()

    # Resumen de urgencia
    va = vent_meta['ventanas_activas']
    vp = vent_meta['ventanas_proximas']
    pc = vent_meta['productos_criticos']

    vu1, vu2, vu3 = st.columns(3)
    with vu1:
        color_va = "#00A34F" if va > 0 else "#6b7280"
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value" style="color:{color_va};">{va}</div>
            <div class="kpi-label">Ventanas activas ahora</div>
            <div class="kpi-sub">🟢 Abiertas hoy</div>
        </div>""", unsafe_allow_html=True)
    with vu2:
        color_vp = "#f59e0b" if vp > 0 else "#6b7280"
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value" style="color:{color_vp};">{vp}</div>
            <div class="kpi-label">Próximas en &lt;60 días</div>
            <div class="kpi-sub">🟡 Preparar inventario</div>
        </div>""", unsafe_allow_html=True)
    with vu3:
        pc_str = ", ".join(pc) if pc else "—"
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value" style="font-size:1rem;">{pc_str if pc_str != '—' else '—'}</div>
            <div class="kpi-label">Productos críticos</div>
            <div class="kpi-sub">Con ventana activa o próxima</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="{'info-box' if va > 0 or vp > 0 else 'alert-box'}">
        {vent_meta['mensaje']}
    </div>
    """, unsafe_allow_html=True)

    # Tabla calendario color-coded
    if not vent_df.empty:
        estado_color = {
            '🟢 ACTIVA':  'background-color: rgba(0,163,79,0.15)',
            '🟡 PRÓXIMA': 'background-color: rgba(245,158,11,0.15)',
            '⭕ CERRADA': 'background-color: rgba(220,38,38,0.08)',
            '⚪ FUTURA':  'background-color: rgba(150,150,150,0.08)',
        }
        vent_display = vent_df[['cultivo', 'estadio', 'fertilizante', 'ventana', 'estado', 'descripcion']].copy()
        vent_display.columns = ['Cultivo', 'Estadio', 'Fertilizante', 'Ventana', 'Estado', 'Descripción']

        def style_vent(row):
            bg = estado_color.get(row['Estado'], '')
            return [bg] * len(row)

        st.dataframe(
            vent_display.style.apply(style_vent, axis=1),
            width='stretch', hide_index=True, height=350
        )

    st.markdown("---")

    with st.spinner("Cargando datos de campaña..."):
        bcr_data = load_bcr()
        ciafa_df = load_ciafa()

    # Selector de cultivo campaña
    crop_bcr = st.radio(
        "Cultivo",
        options=['soja', 'maiz', 'trigo'],
        format_func=lambda x: {'soja': 'Soja', 'maiz': 'Maíz', 'trigo': 'Trigo'}[x],
        horizontal=True,
        key="bcr_cultivo",
    )

    crop_data = bcr_data.get(crop_bcr, {})
    crop_nombre = crop_data.get('nombre', crop_bcr.capitalize())

    # KPI campaña
    pk1, pk2, pk3, pk4 = st.columns(4)
    with pk1:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{crop_data.get('area_nacional_mha', 0):.1f} M ha</div>
            <div class="kpi-label">Área nacional</div>
            <div class="kpi-sub">Campaña 2024/25</div>
        </div>""", unsafe_allow_html=True)
    with pk2:
        av_siem = crop_data.get('avance_siembra_pct', 0)
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{av_siem}%</div>
            <div class="kpi-label">Avance siembra</div>
            <div class="kpi-sub">BCR semana actual</div>
        </div>""", unsafe_allow_html=True)
    with pk3:
        av_cos = crop_data.get('avance_cosecha_pct', 0)
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{av_cos}%</div>
            <div class="kpi-label">Avance cosecha</div>
            <div class="kpi-sub">BCR semana actual</div>
        </div>""", unsafe_allow_html=True)
    with pk4:
        prod_esp = crop_data.get('produccion_esp_mtn', 0)
        rend_esp = crop_data.get('rendimiento_esp_tn_ha', 0)
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-value">{prod_esp:.1f} M tn</div>
            <div class="kpi-label">Producción esperada</div>
            <div class="kpi-sub">{rend_esp:.2f} tn/ha rendimiento</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    bcr_col1, bcr_col2 = st.columns([1, 1])

    with bcr_col1:
        # Gráfico avance de siembra semanal
        hist_sem = crop_data.get('historico_semanal', {})
        semanas = hist_sem.get('semanas', [])
        actual_list = hist_sem.get('actual', [])
        prom5y_list = hist_sem.get('prom5y', [])

        if semanas and actual_list:
            fig_bcr = go.Figure()
            fig_bcr.add_trace(go.Scatter(
                x=semanas, y=actual_list,
                mode='lines+markers',
                name='2024/25',
                line=dict(color='#00A34F', width=2.5),
                marker=dict(size=6),
            ))
            fig_bcr.add_trace(go.Scatter(
                x=semanas, y=prom5y_list,
                mode='lines+markers',
                name='Prom. 5 años',
                line=dict(color='#9ca3af', width=1.5, dash='dash'),
                marker=dict(size=4),
            ))
            fig_bcr.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white',
                height=280,
                title=f"{crop_nombre} — Avance Siembra vs Histórico",
                xaxis_title="Semana",
                yaxis_title="Avance (%)",
                yaxis=dict(range=[0, 105]),
                legend=dict(orientation='h', y=-0.2),
                margin=dict(l=0, r=0, t=40, b=50),
            )
            st.plotly_chart(fig_bcr, width='stretch')
        else:
            st.info("Sin datos de avance semanal para este cultivo.")

    with bcr_col2:
        # Progreso bars siembra y cosecha
        st.markdown('<p class="section-title">Estado de Campaña</p>', unsafe_allow_html=True)
        st.markdown(f"**Siembra** ({av_siem}%)")
        st.progress(av_siem / 100)
        st.markdown(f"**Cosecha** ({av_cos}%)")
        st.progress(av_cos / 100)

        st.markdown(f"""
        <div class="info-box" style="margin-top:1rem;">
            <strong>{crop_nombre}</strong><br>
            Área: <strong>{crop_data.get('area_nacional_mha', 0):.1f} M ha</strong> ·
            Rend. esp.: <strong>{rend_esp:.2f} tn/ha</strong> ·
            Producción esp.: <strong>{prod_esp:.1f} M tn</strong>
        </div>
        """, unsafe_allow_html=True)

    # Gráfico CIAFA consumo
    st.markdown("---")
    st.markdown('<p class="section-title">Consumo Nacional de Fertilizantes — CIAFA 2015-2024</p>', unsafe_allow_html=True)

    fig_ciafa = go.Figure()
    ciafa_colors = {
        'Urea': '#00A34F',
        'MAP': '#3b82f6',
        'MOP': '#f59e0b',
        'Otros': '#9ca3af',
    }

    for fert_c in ['Urea', 'MAP', 'MOP', 'Otros']:
        if fert_c in ciafa_df.columns:
            fig_ciafa.add_trace(go.Bar(
                x=ciafa_df['año'],
                y=ciafa_df[fert_c],
                name=fert_c,
                marker_color=ciafa_colors.get(fert_c, '#374151'),
            ))

    # Línea total
    if 'Total' in ciafa_df.columns:
        fig_ciafa.add_trace(go.Scatter(
            x=ciafa_df['año'],
            y=ciafa_df['Total'],
            mode='lines+markers',
            name='Total',
            line=dict(color='#1f2937', width=2),
            marker=dict(size=6),
        ))

    fig_ciafa.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_white',
        height=340,
        barmode='stack',
        title='Consumo de Fertilizantes Argentina (millones de tn)',
        xaxis_title='Año',
        yaxis_title='Millones de toneladas',
        legend=dict(orientation='h', y=-0.15),
        margin=dict(l=0, r=0, t=40, b=50),
    )
    st.plotly_chart(fig_ciafa, width='stretch')

    # Variación interanual
    if not ciafa_df.empty and 'Total' in ciafa_df.columns:
        ult_val = ciafa_df['Total'].iloc[-1]
        prev_val = ciafa_df['Total'].iloc[-2]
        delta_ciafa = (ult_val - prev_val) / prev_val * 100
        box_class = "info-box" if delta_ciafa >= 0 else "alert-box"
        st.markdown(f"""
        <div class="{box_class}">
            <strong>Tendencia CIAFA:</strong> El consumo total 2024 fue
            <strong>{ult_val:.2f} M tn</strong>, un
            <strong>{delta_ciafa:+.1f}%</strong> vs 2023 ({prev_val:.2f} M tn).
            {'Recuperación del mercado tras la caída de 2023.' if delta_ciafa >= 0 else 'Contracción del mercado. Oportunidad para posicionamiento diferenciado.'}
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 6 — SIMULADOR DE CAMPAÑA
# ══════════════════════════════════════════════════════════
with tab6:
    st.markdown('<p class="section-title">🎯 Simulador de Campaña</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Modelado reactivo de demanda y valor de mercado bajo distintos escenarios de precios y área</p>', unsafe_allow_html=True)

    sim_left, sim_right = st.columns([1, 2])

    with sim_left:
        st.markdown('<p class="section-title">Parámetros del Escenario</p>', unsafe_allow_html=True)

        # Presets
        preset_col1, preset_col2, preset_col3 = st.columns(3)
        with preset_col1:
            pess_btn = st.button("📉 Pesimista", key="btn_pess")
        with preset_col2:
            base_btn = st.button("📊 Base", key="btn_base")
        with preset_col3:
            opt_btn = st.button("📈 Optimista", key="btn_opt")

        # Inicializar defaults en session state
        if 'sim_soja' not in st.session_state:
            st.session_state.sim_soja = 345
        if 'sim_maiz' not in st.session_state:
            st.session_state.sim_maiz = 188
        if 'sim_urea' not in st.session_state:
            st.session_state.sim_urea = 480
        if 'sim_map' not in st.session_state:
            st.session_state.sim_map = 685
        if 'sim_area' not in st.session_state:
            st.session_state.sim_area = 0
        if 'sim_adopt' not in st.session_state:
            st.session_state.sim_adopt = 85

        # Manejar presets
        if pess_btn:
            st.session_state.sim_soja  = 280
            st.session_state.sim_maiz  = 150
            st.session_state.sim_urea  = 550
            st.session_state.sim_map   = 750
            st.session_state.sim_area  = -10
            st.session_state.sim_adopt = 70
            st.info("📉 Pesimista: Soja $280 · Maíz $150 · Urea $550 · MAP $750 · Área -10% · Adopción 70%")

        if base_btn:
            st.session_state.sim_soja  = 345
            st.session_state.sim_maiz  = 188
            st.session_state.sim_urea  = 480
            st.session_state.sim_map   = 685
            st.session_state.sim_area  = 0
            st.session_state.sim_adopt = 85
            st.info("📊 Base: Soja $345 · Maíz $188 · Urea $480 · MAP $685 · Área 0% · Adopción 85%")

        if opt_btn:
            st.session_state.sim_soja  = 420
            st.session_state.sim_maiz  = 230
            st.session_state.sim_urea  = 400
            st.session_state.sim_map   = 580
            st.session_state.sim_area  = 10
            st.session_state.sim_adopt = 95
            st.info("📈 Optimista: Soja $420 · Maíz $230 · Urea $400 · MAP $580 · Área +10% · Adopción 95%")

        st.markdown("---")
        st.markdown("**Precios de granos (USD/tn)**")

        precio_soja_sim = st.slider(
            "Precio Soja", min_value=200, max_value=600,
            value=st.session_state.sim_soja, step=5, key="sl_soja"
        )
        precio_maiz_sim = st.slider(
            "Precio Maíz", min_value=100, max_value=400,
            value=st.session_state.sim_maiz, step=5, key="sl_maiz"
        )

        st.markdown("**Precios de fertilizantes (USD/tn)**")
        precio_urea_sim = st.slider(
            "Precio Urea", min_value=200, max_value=800,
            value=st.session_state.sim_urea, step=10, key="sl_urea"
        )
        precio_map_sim = st.slider(
            "Precio MAP", min_value=300, max_value=1000,
            value=st.session_state.sim_map, step=10, key="sl_map"
        )

        st.markdown("**Variables de escenario**")
        var_area_sim = st.slider(
            "Variación Área (%)", min_value=-20, max_value=20,
            value=st.session_state.sim_area, step=1, key="sl_area"
        )
        adopcion_sim = st.slider(
            "Adopción tecnológica (%)", min_value=60, max_value=100,
            value=st.session_state.sim_adopt, step=1, key="sl_adopt"
        )

    with sim_right:
        # Calcular escenario
        with st.spinner("Calculando escenario..."):
            sim_result = engine.simulate_scenario(
                precio_soja=precio_soja_sim,
                precio_maiz=precio_maiz_sim,
                precio_urea=precio_urea_sim,
                precio_map=precio_map_sim,
                var_area_pct=var_area_sim,
                adopcion_pct=adopcion_sim,
            )

        total_dem_sim = sim_result['total_dem_tn']
        total_val_sim = sim_result['total_valor_musd']
        delta_dem     = sim_result['delta_dem_pct']
        delta_val     = sim_result['delta_val_pct']
        gauge_val     = sim_result['gauge_compra']
        ratios_sim_df = sim_result['ratios_sim_df']
        top5_cambios  = sim_result['top5_cambios']

        # KPI row simulador
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
            delta_color = "#00A34F" if delta_dem >= 0 else "#dc2626"
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value" style="color:{delta_color};">{delta_dem:+.1f}%</div>
                <div class="kpi-label">Delta vs base</div>
                <div class="kpi-sub">demanda potencial</div>
            </div>""", unsafe_allow_html=True)
        with sk4:
            gauge_color = "#00A34F" if gauge_val >= 70 else ("#f59e0b" if gauge_val >= 40 else "#dc2626")
            st.markdown(f"""<div class="kpi-box">
                <div class="kpi-value" style="color:{gauge_color};">{gauge_val}/100</div>
                <div class="kpi-label">Índice de compra</div>
                <div class="kpi-sub">gauge momento mercado</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Gauge chart
        gcol1, gcol2 = st.columns([1, 2])

        with gcol1:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=gauge_val,
                title={'text': "Momento de Compra", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 100], 'tickfont': {'size': 10}},
                    'bar': {'color': gauge_color},
                    'steps': [
                        {'range': [0, 40],  'color': 'rgba(220,38,38,0.15)'},
                        {'range': [40, 70], 'color': 'rgba(245,158,11,0.15)'},
                        {'range': [70, 100],'color': 'rgba(0,163,79,0.15)'},
                    ],
                    'threshold': {
                        'line': {'color': '#374151', 'width': 2},
                        'thickness': 0.75,
                        'value': gauge_val,
                    },
                },
                number={'font': {'size': 28, 'color': gauge_color}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                height=250,
                margin=dict(l=20, r=20, t=40, b=0),
            )
            st.plotly_chart(fig_gauge, width='stretch')

        with gcol2:
            # Tabla ratios simulados
            st.markdown('<p class="section-title">Ratios Simulados vs Base</p>', unsafe_allow_html=True)

            if not ratios_sim_df.empty:
                ratios_display = ratios_sim_df[
                    (ratios_sim_df['grano'].isin([cultivo_global, 'Soja', 'Maíz'])) &
                    (ratios_sim_df['fertilizante'].isin(['Urea', 'MAP']))
                ].copy()

                if ratios_display.empty:
                    ratios_display = ratios_sim_df.head(10).copy()

                ratios_display['ratio_sim']  = ratios_display['ratio_sim'].apply(lambda x: f"{x:.2f}")
                ratios_display['ratio_base'] = ratios_display['ratio_base'].apply(lambda x: f"{x:.2f}")
                ratios_display['delta']      = ratios_display['delta'].apply(lambda x: f"{x:+.2f}")
                ratios_display = ratios_display.rename(columns={
                    'grano': 'Grano',
                    'fertilizante': 'Fertilizante',
                    'ratio_sim': 'Ratio Sim.',
                    'ratio_base': 'Ratio Base',
                    'delta': 'Delta',
                })

                def highlight_delta(val):
                    try:
                        v = float(val)
                        if v < 0:
                            return 'color: #00A34F; font-weight:600'
                        elif v > 0:
                            return 'color: #dc2626; font-weight:600'
                    except Exception:
                        pass
                    return ''

                styled_ratios = ratios_display.style.map(
                    highlight_delta, subset=['Delta']
                )
                st.dataframe(styled_ratios, width='stretch', hide_index=True)

        # Top 5 zonas que más cambian
        st.markdown("---")
        st.markdown('<p class="section-title">Top 5 Zonas con Mayor Cambio</p>', unsafe_allow_html=True)

        if not top5_cambios.empty:
            t5 = top5_cambios.copy()
            t5['delta_pct'] = t5['delta_pct'].apply(lambda x: f"{x:+.1f}%")
            t5['dem_sim_tn'] = t5['dem_sim_tn'].apply(lambda x: f"{x:,.0f}")
            t5 = t5.rename(columns={
                'departamento': 'Departamento',
                'provincia': 'Provincia',
                'cultivo': 'Cultivo',
                'dem_sim_tn': 'Demanda sim. (tn)',
                'delta_pct': 'Delta vs base',
            })
            st.dataframe(t5, width='stretch', hide_index=True)

        # Resumen escenario
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
            (<strong>{delta_dem:+.1f}%</strong> vs base) ·
            Valor de mercado <strong>USD {total_val_sim:.0f}M</strong>
            (<strong>{delta_val:+.1f}%</strong> vs base) ·
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
    <span class="source-tag">Dosis técnicas</span> INTA EEA Marcos Juárez
    <span class="source-tag">Clima</span> NASA POWER API
    <span class="source-tag">Precios</span> MATBA-ROFEX / CIAFA Marzo 2025
    <span class="source-tag">Campaña</span> BCR 2024/25
    <span class="source-tag">ENSO</span> NOAA CPC<br>
    Datos de referencia actualizados a Marzo 2025 ·
    Proyecciones con fines comerciales exclusivamente ·
    No constituyen asesoramiento de inversión.<br>
    <em>Generado: {today_str} · Stack: Python 3.12 · Streamlit 1.55 · Plotly 6.x · Pandas 2.3</em>
</div>
""", unsafe_allow_html=True)
