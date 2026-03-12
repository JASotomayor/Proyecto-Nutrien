# AgriPulse Argentina 🌾
**Campaign Intelligence Platform · Nutrien Ag Solutions**

## Instalación y uso

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fuentes de datos (todas públicas/gratuitas)

| Módulo | Fuente | URL | Costo |
|--------|--------|-----|-------|
| Mapa de Oportunidad | SIIA/MAGyP | https://datosestimaciones.magyp.gob.ar/ | Gratis |
| Dosis técnica | INTA | https://inta.gob.ar | Gratis |
| Consumo fertilizantes | CIAFA | https://www.ciafa.org.ar/estadisticas | Gratis |
| Clima / GDD | NASA POWER API | https://power.larc.nasa.gov/api/ | Gratis, sin key |
| Precios granos | MATBA-ROFEX | https://www.matbarofex.com.ar/ | Referencia pública |
| Avance campaña | BCR | https://bcr.com.ar/es/mercados/granos | Gratis |

## Arquitectura

```
agripulse/
├── app.py                 # UI Streamlit (tabs, visualizaciones)
├── agripulse_engine.py    # Motor de datos y lógica de negocio
├── requirements.txt
└── README.md
```

## Módulos

### 1. 🗺️ Mapa de Oportunidad
- Superficie sembrada real por departamento (SIIA 2023/24)
- Cálculo de demanda potencial con dosis técnica INTA
- Filtros por cultivo, provincia, fertilizante
- Coordenadas reales de cada departamento

### 2. 📊 Ratio Insumo/Grano
- Ratios actuales y serie histórica 2020-2025
- Matriz calor: todos los pares fertilizante/grano
- Business Case Argumentator: script listo para usar
- Percentil histórico del ratio actual

### 3. 🌦️ Inteligencia Climática
- API NASA POWER: T2M, PRECTOTCORR, RH2M (sin key)
- GDD acumulados y estadio fenológico
- Detección automática de ventana óptima N
- 7 zonas productivas predefinidas

### 4. ⚡ Pulso de Campaña
- Avance de siembra/cosecha vs. promedio histórico (BCR)
- Consumo histórico de fertilizantes por tipo (CIAFA)
- Estimación de valor bruto de cosecha
