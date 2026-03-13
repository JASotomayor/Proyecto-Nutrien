# AgriPulse Argentina 🌾
**Campaign Intelligence Platform · Nutrien Ag Solutions Argentina**

Plataforma de inteligencia comercial para el equipo de ventas de Nutrien Argentina.
Combina datos reales de SIIA/MAGyP, NASA POWER, CIAFA y BCR para identificar oportunidades, calcular ratios insumo/grano y optimizar la ventana de aplicación de fertilizantes.

---

## Inicio rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Correr la app (desde la carpeta src/)
streamlit run app.py
```

La app se abre en `http://localhost:8501`

---

## Deploy en Streamlit Cloud

1. Hacer fork/push del repo a GitHub
2. Ir a [share.streamlit.io](https://share.streamlit.io) → New app
3. Seleccionar el repo y como **Main file path**: `src/app.py`
4. Click **Deploy** — no requiere ninguna API key

> **Sin variables de entorno requeridas.** NASA POWER API es completamente gratuita y sin autenticación.

---

## Fuentes de datos

| Módulo | Fuente | Endpoint / URL | Costo |
|--------|--------|----------------|-------|
| Mapa de Oportunidad | SIIA/MAGyP | https://datosestimaciones.magyp.gob.ar/ | Gratis |
| Dosis técnica | INTA EEA Marcos Juárez | https://inta.gob.ar | Gratis |
| Consumo fertilizantes | CIAFA | https://www.ciafa.org.ar/estadisticas | Gratis |
| Clima / GDD | **NASA POWER API** | https://power.larc.nasa.gov/api/temporal/daily/point | Gratis, sin key |
| Precios granos | MATBA-ROFEX | https://www.matbarofex.com.ar/ | Referencia pública |
| Avance campaña | BCR | https://bcr.com.ar/es/mercados/granos | Gratis |

---

## Arquitectura del proyecto

```
Proyecto-Nutrien/
├── src/
│   ├── app.py                 # UI Streamlit — tabs, visualizaciones, sliders
│   ├── agripulse_engine.py    # Motor de datos y lógica de negocio
│   ├── requirements.txt       # Dependencias Python
│   └── README.md              # Este archivo
└── data/
    ├── nutrien_locations.csv  # Sucursales Nutrien
    └── competitor_locations.csv
```

---

## Módulos en detalle

### 🗺️ Tab 1 — Mapa de Oportunidad

**Qué hace:**
- Muestra un mapa interactivo (Plotly `scatter_map` con tiles Carto Dark) con 33+ departamentos clave de la pampa húmeda
- Calcula la demanda potencial de fertilizantes aplicando la **dosis técnica INTA** sobre la superficie sembrada real (campaña 2023/24 de SIIA/MAGyP)
- Filtra por cultivo (Maíz, Soja, Trigo, Girasol), provincia y fertilizante (Urea, MAP, MOP)

**KPIs mostrados:**
- Superficie total en selección (M ha)
- Demanda potencial (K tn fertilizante)
- Valor de mercado estimado (USD M)
- Número de departamentos

**Argumento comercial automático:** El sistema genera un texto listo para usar con el departamento top del ranking.

---

### 📊 Tab 2 — Ratio Insumo/Grano

**Qué hace:**
- Calcula el ratio histórico `precio_fertilizante / precio_grano` para todos los pares posibles (5 fertilizantes × 4 granos = 20 combinaciones)
- Muestra la serie histórica 2020–2025 con el pico de la guerra de Ucrania (2022)
- Determina el percentil histórico del ratio actual

**Simulador de Escenarios (nuevo):**
- Dos sliders independientes: variación % del precio del grano y del fertilizante
- Muestra el ratio simulado en el gráfico histórico como línea punteada
- Genera automáticamente el script de venta adaptado al escenario

**Business Case Argumentator:**
- Script listo para usar con el productor
- Badge de color: verde (percentil < 40 = compra barata), ámbar, rojo

---

### 🌦️ Tab 3 — Inteligencia Climática

**Qué hace:**
- Llama a la **NASA POWER API** (sin key) para obtener datos diarios de los últimos 30 días:
  - `T2M` — temperatura media a 2m
  - `PRECTOTCORR` — precipitación corregida
  - `RH2M` — humedad relativa
  - `ALLSKY_SFC_SW_DWN` — radiación solar
- Filtra automáticamente el fill value `-999` de NASA (error presente en versión original, corregido)
- Calcula GDD acumulados (base 10°C)
- Detecta el estadio fenológico según GDD y avisa si hay **ventana óptima de aplicación de N**

**Fallback sin conexión:**
- Si NASA no responde, usa normales climatológicas del SMN/INTA (totalmente determinístico, sin valores aleatorios)

**7 zonas predefinidas:** Zona Núcleo, Marcos Juárez, Castellanos, Trenque Lauquen, Gral. Obligado, Anta (Salta), Río Cuarto

---

### ⚡ Tab 4 — Pulso de Campaña

**Qué hace:**
- Muestra el avance de siembra/cosecha de la campaña 2024/25 vs. promedio histórico 5 años (BCR)
- Gráfico de barras apiladas con consumo histórico de fertilizantes 2015–2024 (CIAFA)
- Estima la producción total y el valor bruto de cosecha

---

## Dependencias

```
streamlit>=1.32
pandas>=2.0
numpy>=1.24
plotly>=6.0          # Requiere 6.0+ para scatter_map (reemplaza scatter_mapbox deprecado)
requests>=2.31
python-dateutil>=2.8
```

> **Nota:** Plotly 6.x depreca `scatter_mapbox` en favor de `scatter_map`. Esta app ya usa la nueva API.

---

## Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| Mapa no renderiza | Plotly < 6.0 | `pip install plotly>=6.0` |
| Temperatura -999°C | Fill value NASA no filtrado | Ya corregido en `agripulse_engine.py` |
| `🟡 Datos estimados` en clima | NASA POWER sin conexión | Normal — usa fallback climatológico |
| Error `scatter_mapbox` deprecated | Plotly < 6.0 | Actualizar a `plotly>=6.0` |

---

## Roadmap — Próxima iteración

- [ ] Integración directa con API REST de SIIA/MAGyP (scraping estructurado campaña actual)
- [ ] Precios de granos en tiempo real via BCR API o scraping MATBA-ROFEX
- [ ] Exportar el Business Case Argumentator como PDF
- [ ] Mapa de competidores superpuesto con datos de sucursales
- [ ] Alertas automáticas por email cuando el ratio cae a percentil < 30
- [ ] Dashboard de seguimiento de visitas comerciales por departamento

---

*Desarrollado para Nutrien Ag Solutions Argentina · Datos oficiales públicos · Sin API keys requeridas*
