"""
AgriPulse Argentina — Campaign Intelligence Platform
Desarrollado para Nutrien Ag Solutions
Fuentes: SIIA/MAGyP · CIAFA · NASA POWER · MATBA-ROFEX · BCR
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from agripulse_engine import AgriPulseEngine

# ──────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriPulse Argentina | Nutrien",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────
# THEME & CSS
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Dark background */
.stApp { background-color: #0a0f0e; }
section[data-testid="stSidebar"] { background: #0d1412; }

/* Cards */
.ap-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(16,185,129,0.12);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.ap-card:hover {
    border-color: rgba(16,185,129,0.35);
    background: rgba(16,185,129,0.03);
}

/* KPI tiles */
.kpi-box {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(5,150,105,0.04));
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.kpi-value { font-size: 2rem; font-weight: 800; color: #10b981; line-height: 1.1; }
.kpi-label { font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }
.kpi-sub   { font-size: 0.85rem; color: #64748b; margin-top: 2px; }

/* Section title */
.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #10b981;
    margin-bottom: 18px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(16,185,129,0.15);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; padding: 4px 0; }
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 600;
    color: #94a3b8;
    font-size: 0.88rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    border-color: #10b981 !important;
    color: white !important;
}

/* Badges */
.badge-green { background: rgba(16,185,129,0.15); color: #10b981; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.badge-amber { background: rgba(245,158,11,0.15); color: #f59e0b; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.badge-red   { background: rgba(239,68,68,0.15); color: #ef4444; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }

/* Source tag */
.source-tag { font-size: 0.72rem; color: #475569; text-align: right; margin-top: 6px; }

/* Metric override */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px !important;
}

/* Info box */
.info-box {
    background: rgba(16,185,129,0.06);
    border-left: 3px solid #10b981;
    border-radius: 0 10px 10px 0;
    padding: 14px 16px;
    margin: 12px 0;
    font-size: 0.9rem;
    color: #cbd5e1;
}

/* Header */
.ap-header {
    background: linear-gradient(135deg, rgba(5,150,105,0.08), rgba(0,0,0,0));
    border: 1px solid rgba(16,185,129,0.12);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 32px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# INIT
# ──────────────────────────────────────────────────────────
engine = AgriPulseEngine()


@st.cache_data(ttl=3600)
def load_market(cultivo, provincia):
    return engine.get_market_potential(cultivo, provincia)


@st.cache_data(ttl=3600)
def load_ratios():
    return engine.get_price_ratios()


@st.cache_data(ttl=86400)
def load_ciafa():
    return engine.get_ciafa_consumption()


@st.cache_data(ttl=900)     # 15 min cache para clima
def load_weather(lat, lon):
    return engine.get_weather_intel(lat, lon, days_back=30)


# ──────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────
st.markdown("""
<div class="ap-header">
  <div style="display:flex; align-items:center; gap:16px; margin-bottom:10px">
    <span style="font-size:2.5rem">🌾</span>
    <div>
      <h1 style="margin:0; font-size:2.4rem; font-weight:800; color:#f1f5f9; line-height:1.1">
        AgriPulse Argentina
      </h1>
      <p style="margin:0; color:#10b981; font-weight:600; font-size:1.05rem; letter-spacing:0.03em">
        Campaign Intelligence Platform · Nutrien Ag Solutions
      </p>
    </div>
  </div>
  <p style="color:#64748b; margin:0; font-size:0.9rem">
    Datos reales: SIIA/MAGyP · CIAFA · NASA POWER API · MATBA-ROFEX · BCR
  </p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️  Mapa de Oportunidad",
    "📊  Ratio Insumo/Grano",
    "🌦️  Inteligencia Climática",
    "⚡  Pulso de Campaña",
])


# ══════════════════════════════════════════════════════════
# TAB 1 — MAPA DE OPORTUNIDAD
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">🗺️ Potencial de Mercado por Departamento</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
    with col_f1:
        cultivo_sel = st.selectbox("Cultivo", ['Todos', 'Maíz', 'Soja', 'Trigo', 'Girasol'], key='cult_map')
    with col_f2:
        provincias_disp = ['Todas'] + sorted(set(d['provincia'] for d in engine.SIIA_DATA))
        provincia_sel = st.selectbox("Provincia", provincias_disp, key='prov_map')
    with col_f3:
        fert_map = st.selectbox("Fertilizante", ['Todos', 'Urea', 'MAP', 'MOP'], key='fert_map')

    detail_df, map_df = load_market(cultivo_sel, provincia_sel)

    if fert_map != 'Todos':
        detail_df = detail_df[detail_df['fertilizante'] == fert_map]
        # Re-aggregate map
        map_df = (
            detail_df.groupby(['provincia', 'departamento', 'cultivo', 'lat', 'lon', 'area_ha'])
            .agg(demanda_total_tn=('demanda_potencial_tn', 'sum'),
                 valor_total_musd=('valor_mercado_musd', 'sum'))
            .reset_index()
        )

    # ── KPI Row ──────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    total_ha     = detail_df['area_ha'].sum() if not detail_df.empty else 0
    total_dem_tn = detail_df['demanda_potencial_tn'].sum() if not detail_df.empty else 0
    total_musd   = detail_df['valor_mercado_musd'].sum() if not detail_df.empty else 0
    n_deptos     = detail_df['departamento'].nunique() if not detail_df.empty else 0

    for col, val, lab, sub in zip(
        [k1, k2, k3, k4],
        [f"{total_ha/1e6:.2f} M ha", f"{total_dem_tn/1e3:.0f} K tn", f"USD {total_musd:.0f} M", f"{n_deptos}"],
        ["Superficie Total", "Demanda Potencial", "Valor de Mercado", "Departamentos"],
        ["área sembrada", "fertilizante aplicable", "a precio actual", "en selección"],
    ):
        col.markdown(f"""
        <div class="kpi-box">
          <div class="kpi-value">{val}</div>
          <div class="kpi-label">{lab}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MAPA con coordenadas reales ───────────────────────
    col_mapa, col_tabla = st.columns([3, 2])

    with col_mapa:
        if not map_df.empty:
            size_col = map_df['demanda_total_tn']
            fig_map = px.scatter_mapbox(
                map_df,
                lat='lat', lon='lon',
                size='demanda_total_tn',
                color='valor_total_musd',
                hover_name='departamento',
                hover_data={
                    'provincia': True,
                    'cultivo': True,
                    'area_ha': ':,.0f',
                    'demanda_total_tn': ':,.0f',
                    'valor_total_musd': ':.2f',
                    'lat': False, 'lon': False,
                },
                color_continuous_scale='Greens',
                size_max=40,
                zoom=4.5,
                center={"lat": -33.0, "lon": -62.5},
                mapbox_style='carto-darkmatter',
                labels={
                    'demanda_total_tn': 'Demanda (tn)',
                    'valor_total_musd': 'Valor (M USD)',
                    'area_ha': 'Área (ha)',
                },
                title='',
                template='plotly_dark',
                height=520,
            )
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_colorbar=dict(
                    title="USD M",
                    tickfont=dict(color='#94a3b8'),
                    title_font=dict(color='#94a3b8'),
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.markdown('<div class="source-tag">Fuente: SIIA/MAGyP 2023/24 · Dosis técnica: INTA</div>', unsafe_allow_html=True)
        else:
            st.info("Sin datos para la selección actual.")

    with col_tabla:
        st.markdown("**Top 15 — Departamentos por Demanda Potencial**")
        top_df = (
            map_df.sort_values('demanda_total_tn', ascending=False)
            .head(15)[['departamento', 'provincia', 'cultivo', 'area_ha', 'demanda_total_tn', 'valor_total_musd']]
            .rename(columns={
                'departamento': 'Depto',
                'provincia': 'Provincia',
                'cultivo': 'Cultivo',
                'area_ha': 'Ha',
                'demanda_total_tn': 'Dem. (tn)',
                'valor_total_musd': 'USD M',
            })
        )
        st.dataframe(
            top_df.style.format({'Ha': '{:,.0f}', 'Dem. (tn)': '{:,.0f}', 'USD M': '{:.2f}'}),
            use_container_width=True,
            height=480,
        )

    # ── Argumento comercial ───────────────────────────────
    if not detail_df.empty:
        top_depto = map_df.sort_values('demanda_total_tn', ascending=False).iloc[0]
        st.markdown(f"""
        <div class="info-box">
        💡 <strong>Argumento SIIA para el equipo comercial:</strong> {top_depto['departamento']} ({top_depto['provincia']}) 
        encabeza el ranking con <strong>{top_depto['demanda_total_tn']:,.0f} tn</strong> de demanda potencial 
        sobre <strong>{top_depto['area_ha']:,.0f} ha</strong> sembradas. 
        Valor de mercado estimado: <strong>USD {top_depto['valor_total_musd']:.1f} M</strong> por campaña.
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 2 — RATIO INSUMO / GRANO
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">📊 Ratio Insumo/Grano — El argumento de venta más poderoso</div>', unsafe_allow_html=True)

    ratios_df = load_ratios()

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        grano_sel = st.selectbox("Grano", list(engine.GRAIN_PRICES.keys()), key='grain_r')
    with col_sel2:
        fert_sel = st.selectbox("Fertilizante", list(engine.FERTILIZER_PRICES.keys()), key='fert_r')

    hist_df, ratio_actual, percentil = engine.get_price_history(grano_sel, fert_sel)

    # ── KPI Ratio ──────────────────────────────────────────
    kr1, kr2, kr3, kr4 = st.columns(4)
    precio_grano = engine.GRAIN_PRICES.get(grano_sel, 0)
    precio_fert  = engine.FERTILIZER_PRICES.get(fert_sel, 0)
    kg_bolsa     = round(ratio_actual * 50, 1)

    kr1.metric("Ratio Actual (tn/tn)", f"{ratio_actual:.2f}", help="tn de grano para 1 tn de fertilizante")
    kr2.metric("Precio Grano", f"USD {precio_grano}/tn", help="Referencia MATBA-ROFEX")
    kr3.metric("Precio Fertilizante", f"USD {precio_fert}/tn", help="Referencia CIAFA")
    kr4.metric("Kg grano × bolsa 50 kg", f"{kg_bolsa} kg")

    st.markdown("<br>", unsafe_allow_html=True)

    col_hist, col_matrix = st.columns([3, 2])

    with col_hist:
        # ── Serie histórica ────────────────────────────────
        fig_hist = go.Figure()

        fig_hist.add_trace(go.Scatter(
            x=hist_df['fecha'], y=hist_df['ratio'],
            mode='lines+markers',
            line=dict(color='#10b981', width=2.5),
            marker=dict(size=5),
            name='Ratio histórico',
            fill='tozeroy',
            fillcolor='rgba(16,185,129,0.06)',
        ))

        # Línea ratio actual
        fig_hist.add_hline(
            y=ratio_actual,
            line_dash='dash',
            line_color='#f59e0b',
            annotation_text=f"Actual: {ratio_actual:.2f}",
            annotation_font_color='#f59e0b',
        )

        # Zona pico 2022 (sombreado)
        fig_hist.add_vrect(
            x0='2022-01-01', x1='2022-12-31',
            fillcolor='rgba(239,68,68,0.06)',
            line_width=0,
            annotation_text="Pico Guerra\nUcrania",
            annotation_font_color='#ef4444',
            annotation_font_size=10,
        )

        fig_hist.update_layout(
            title=f"Ratio {fert_sel} / {grano_sel} — Serie histórica 2020-2025",
            xaxis_title="",
            yaxis_title="tn grano / tn fertilizante",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=380,
            legend=dict(font=dict(color='#94a3b8')),
            font=dict(color='#cbd5e1'),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown('<div class="source-tag">Referencia precios: MATBA-ROFEX / CIAFA</div>', unsafe_allow_html=True)

    with col_matrix:
        # ── Matriz calor todos los ratios ──────────────────
        st.markdown("**Ratio actual — todos los pares (tn grano/tn fert)**")
        pivot = ratios_df.pivot(index='grano', columns='fertilizante', values='ratio')

        fig_heat = px.imshow(
            pivot,
            text_auto=True,
            color_continuous_scale='RdYlGn_r',
            aspect='auto',
            template='plotly_dark',
            height=340,
        )
        fig_heat.update_coloraxes(showscale=False)
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(color='#cbd5e1', size=11),
            xaxis=dict(tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('<div class="source-tag">Verde = barato (buena ventana de compra) · Rojo = caro</div>', unsafe_allow_html=True)

    # ── Business Case Argumentator ────────────────────────
    pct_badge = 'badge-green' if percentil < 40 else ('badge-amber' if percentil < 70 else 'badge-red')
    pct_msg   = 'HISTÓRICO BARATO ✓' if percentil < 40 else ('PRECIO MEDIO' if percentil < 70 else 'CARO VS HISTÓRICO')

    st.markdown(f"""
    <div class="ap-card">
      <strong style="color:#10b981; font-size:1rem">💬 Business Case Argumentator</strong><br><br>
      <span class="{pct_badge}">{pct_msg} — Percentil {percentil}° histórico</span>
      <br><br>
      <strong>Script para el productor:</strong><br>
      <em style="color:#cbd5e1">
      "Hoy, para comprar 1 tonelada de <strong>{fert_sel}</strong> necesitás vender 
      <strong>{ratio_actual:.1f} toneladas de {grano_sel}</strong> (o {kg_bolsa:.0f} kg por bolsa de 50 kg). 
      Esto está en el percentil {percentil}° de los últimos 5 años — {'históricamente barato, hay ventana de compra hoy' if percentil < 40 else 'en precio medio histórico' if percentil < 70 else 'por encima del promedio histórico'}."
      </em>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabla completa de ratios ──────────────────────────
    with st.expander("📋 Ver tabla completa de ratios"):
        display_cols = ['grano', 'fertilizante', 'precio_grano_usd_tn', 'precio_fert_usd_tn',
                        'kg_grano_x_kg_fert', 'kg_grano_x_bolsa_50kg']
        st.dataframe(
            ratios_df[display_cols].sort_values('kg_grano_x_kg_fert')
            .rename(columns={
                'grano': 'Grano', 'fertilizante': 'Fertilizante',
                'precio_grano_usd_tn': 'Grano USD/tn',
                'precio_fert_usd_tn': 'Fert USD/tn',
                'kg_grano_x_kg_fert': 'kg grano/kg fert',
                'kg_grano_x_bolsa_50kg': 'kg grano/bolsa 50kg',
            }),
            use_container_width=True,
        )


# ══════════════════════════════════════════════════════════
# TAB 3 — INTELIGENCIA CLIMÁTICA (NASA POWER)
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">🌦️ Inteligencia Climática — Ventana óptima de aplicación</div>', unsafe_allow_html=True)

    col_z1, col_z2, col_z3 = st.columns([2, 1, 1])
    with col_z1:
        zona_sel = st.selectbox("Zona de análisis", list(engine.ZONES.keys()), key='zona_w')
    with col_z2:
        cultivo_w = st.selectbox("Cultivo", ['Maíz', 'Trigo'], key='cult_w')
    with col_z3:
        siembra_date = st.date_input("Fecha estimada de siembra", value=pd.Timestamp('2024-10-15'), key='sow_w')

    zone_coords = engine.ZONES[zona_sel]
    weather     = load_weather(zone_coords['lat'], zone_coords['lon'])

    # Fuente indicator
    fuente_color = '#10b981' if weather['success'] else '#f59e0b'
    fuente_label = '🟢 NASA POWER (datos reales)' if weather['success'] else '🟡 Datos estimados (NASA sin conexión)'
    st.markdown(f'<span style="font-size:0.8rem; color:{fuente_color}">{fuente_label} · Lat: {zone_coords["lat"]} · Lon: {zone_coords["lon"]}</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI Climáticos ────────────────────────────────────
    wk1, wk2, wk3, wk4, wk5 = st.columns(5)
    wk1.metric("Precip. 30d", f"{weather['precip_total']} mm")
    wk2.metric("Temp. Promedio", f"{weather['temp_avg']} °C")
    wk3.metric("Temp. Máx/Mín", f"{weather['temp_max']}/{weather['temp_min']} °C")
    wk4.metric("GDD Acumulados", f"{int(weather['gdd_acum'])}")
    wk5.metric("Días con lluvia", f"{weather['dias_lluvia']}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_clim1, col_clim2 = st.columns([3, 2])
    wdf = weather['df']

    with col_clim1:
        # ── Gráfico dual temperatura + precipitación ───────
        fig_w = go.Figure()

        fig_w.add_trace(go.Bar(
            x=wdf['fecha'], y=wdf['precip_mm'],
            name='Precipitación (mm)',
            marker_color='rgba(59,130,246,0.6)',
            yaxis='y2',
        ))
        fig_w.add_trace(go.Scatter(
            x=wdf['fecha'], y=wdf['temp_c'],
            name='Temperatura (°C)',
            line=dict(color='#f59e0b', width=2),
            mode='lines',
        ))
        fig_w.add_hline(y=10, line_dash='dot', line_color='rgba(16,185,129,0.4)',
                        annotation_text='Base GDD 10°C')

        fig_w.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=340,
            title=f"Clima 30 días — {zona_sel}",
            legend=dict(font=dict(color='#94a3b8'), orientation='h', y=-0.15),
            font=dict(color='#cbd5e1'),
            yaxis=dict(title='Temp (°C)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis2=dict(title='Precip (mm)', overlaying='y', side='right',
                        gridcolor='rgba(255,255,255,0.0)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with col_clim2:
        # ── GDD Acumulados y fenología ─────────────────────
        gdd_acum = int(weather['gdd_acum'])
        stage    = engine.get_phenology_stage(cultivo_w, gdd_acum)

        is_window = 'V6' in stage or 'Macollaje' in stage

        st.markdown(f"""
        <div class="ap-card">
          <strong style="color:#10b981">Estado Fenológico — {cultivo_w}</strong><br><br>
          <div style="font-size:1.6rem; font-weight:700; color:{'#10b981' if is_window else '#cbd5e1'}">
            {stage}
          </div>
          <div style="color:#64748b; font-size:0.85rem; margin-top:8px">
            GDD acumulados desde siembra: <strong>{gdd_acum}</strong>
          </div>
          <br>
        """, unsafe_allow_html=True)

        if is_window:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.1); border:1px solid #10b981;
                        border-radius:10px; padding:12px; color:#10b981; font-weight:600;">
              ✅ VENTANA ÓPTIMA ACTIVA<br>
              <span style="font-weight:400; color:#cbd5e1; font-size:0.85rem">
              El nitrógeno aplicado hoy tiene absorción máxima.<br>
              Argumento de urgencia para el productor.
              </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(245,158,11,0.08); border:1px solid #f59e0b;
                        border-radius:10px; padding:12px; color:#f59e0b;">
              ⏳ Fuera de ventana óptima<br>
              <span style="font-weight:400; color:#94a3b8; font-size:0.85rem">
              Monitorear acumulación de GDD para anticipar la próxima ventana.
              </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── GDD Progress bar ───────────────────────────────
        gdd_target = 200 if cultivo_w == 'Maíz' else 150
        pct_gdd = min(100, int(gdd_acum / gdd_target * 100))
        st.markdown(f"""
        <div style="margin-top:12px">
          <div style="font-size:0.8rem; color:#64748b; margin-bottom:6px">
            GDD hacia ventana V6/Macollaje ({gdd_acum}/{gdd_target})
          </div>
          <div style="background:rgba(255,255,255,0.06); border-radius:20px; height:8px">
            <div style="background:linear-gradient(90deg,#059669,#10b981);
                        width:{pct_gdd}%; height:8px; border-radius:20px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── GDD Acumulado en el tiempo ─────────────────────────
    wdf['gdd_cum'] = wdf['gdd'].cumsum()
    fig_gdd = px.area(
        wdf, x='fecha', y='gdd_cum',
        title=f"GDD Acumulados — {zona_sel} (últimos 30 días)",
        labels={'gdd_cum': 'GDD acumulado', 'fecha': ''},
        template='plotly_dark',
        color_discrete_sequence=['#10b981'],
        height=250,
    )
    fig_gdd.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
    )
    fig_gdd.update_traces(fillcolor='rgba(16,185,129,0.12)', line_color='#10b981')
    st.plotly_chart(fig_gdd, use_container_width=True)
    st.markdown('<div class="source-tag">Fuente: NASA POWER API · parámetros T2M, PRECTOTCORR, RH2M</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 4 — PULSO DE CAMPAÑA
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">⚡ Pulso de Campaña — Avance vs. Histórico</div>', unsafe_allow_html=True)

    bcr = engine.get_bcr_campaign_data()
    ciafa = load_ciafa()

    # ── Selector campaña ───────────────────────────────────
    camp_sel = st.radio(
        "Campaña", ['soja', 'maiz', 'trigo'],
        format_func=lambda x: {'soja': '🫘 Soja', 'maiz': '🌽 Maíz', 'trigo': '🌾 Trigo'}[x],
        horizontal=True,
        key='camp_pulse',
    )
    c = bcr[camp_sel]

    # ── KPIs de campaña ────────────────────────────────────
    ck1, ck2, ck3, ck4 = st.columns(4)
    ck1.metric("Área Nacional", f"{c['area_nacional_mha']} M ha")
    ck2.metric("Avance Siembra", f"{c['avance_siembra_pct']}%")
    ck3.metric("Avance Cosecha", f"{c['avance_cosecha_pct']}%")
    ck4.metric("Rinde Esperado", f"{c['rendimiento_esp_tn_ha']} tn/ha")

    st.markdown("<br>", unsafe_allow_html=True)
    col_prog, col_ciafa = st.columns([3, 2])

    with col_prog:
        # ── Avance semanal vs histórico ────────────────────
        hist = c['historico_semanal']
        fig_prog = go.Figure()

        fig_prog.add_trace(go.Scatter(
            x=hist['semanas'], y=hist['prom5y'],
            name='Promedio 5 años',
            line=dict(color='#475569', dash='dash', width=2),
            mode='lines+markers',
            marker=dict(size=6),
        ))
        fig_prog.add_trace(go.Scatter(
            x=hist['semanas'], y=hist['actual'],
            name='Campaña actual',
            line=dict(color='#10b981', width=2.5),
            mode='lines+markers',
            marker=dict(size=8, symbol='circle'),
            fill='tonexty',
            fillcolor='rgba(16,185,129,0.06)',
        ))

        fig_prog.update_layout(
            title=f"Avance de {'Siembra' if camp_sel != 'trigo' else 'Cosecha'} — {c['nombre']}",
            xaxis_title="Semana",
            yaxis_title="% avance",
            yaxis=dict(range=[0, 110], gridcolor='rgba(255,255,255,0.05)'),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color='#94a3b8'), orientation='h', y=-0.2),
            font=dict(color='#cbd5e1'),
            height=360,
        )
        st.plotly_chart(fig_prog, use_container_width=True)
        st.markdown('<div class="source-tag">Fuente: BCR — Informes Semanales de Siembra y Cosecha</div>', unsafe_allow_html=True)

    with col_ciafa:
        # ── Consumo histórico CIAFA ────────────────────────
        fig_ciafa = go.Figure()
        for fert, color in [('Urea', '#10b981'), ('MAP', '#3b82f6'), ('MOP', '#f59e0b'), ('Otros', '#94a3b8')]:
            fig_ciafa.add_trace(go.Bar(
                x=ciafa['año'], y=ciafa[fert],
                name=fert,
                marker_color=color,
            ))

        fig_ciafa.update_layout(
            barmode='stack',
            title='Consumo de Fertilizantes Argentina (M tn)',
            xaxis_title="",
            yaxis_title="Millones de tn",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color='#94a3b8'), orientation='h', y=-0.2),
            font=dict(color='#cbd5e1'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            height=360,
        )
        st.plotly_chart(fig_ciafa, use_container_width=True)
        st.markdown('<div class="source-tag">Fuente: CIAFA — Estadísticas de consumo 2015-2024</div>', unsafe_allow_html=True)

    # ── Producción esperada y contexto ────────────────────
    prod_total = c['produccion_esp_mtn']
    fob_ref    = engine.GRAIN_PRICES.get(camp_sel.capitalize()[:4].rstrip('í') if camp_sel != 'maiz' else 'Maíz',
                                          engine.GRAIN_PRICES.get(camp_sel.capitalize(), 300))

    st.markdown(f"""
    <div class="ap-card" style="display:flex; gap:48px; align-items:center; flex-wrap:wrap">
      <div>
        <div class="kpi-value">{prod_total} M tn</div>
        <div class="kpi-label">Producción Estimada</div>
      </div>
      <div>
        <div class="kpi-value">USD {prod_total * fob_ref / 1000:.1f} B</div>
        <div class="kpi-label">Valor Bruto de Cosecha</div>
        <div class="kpi-sub">a USD {fob_ref}/tn referencia</div>
      </div>
      <div style="flex:1; min-width:260px; color:#94a3b8; font-size:0.88rem">
        <strong style="color:#10b981">Implicancia para Nutrien:</strong><br>
        Una campaña de {prod_total:.0f} M tn con rendimiento esperado de {c['rendimiento_esp_tn_ha']} tn/ha 
        implica demanda de fertilizante acorde al área sembrada. 
        El desafío comercial es capturar la ventana pre-siembra antes de que el productor compre a la competencia.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#334155; font-size:0.78rem; padding:16px 0">
  <strong style="color:#475569">AgriPulse Argentina</strong> · Developed for Nutrien Campaign Excellence<br>
  Datos: SIIA/MAGyP · CIAFA · NASA POWER API · BCR · MATBA-ROFEX<br>
  Todos los datos de superficie y producción son oficiales/públicos. Precios de fertilizantes: referencia CIAFA Marzo 2025.
</div>
""", unsafe_allow_html=True)
