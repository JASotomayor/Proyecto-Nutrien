"""
AgriPulse Engine v2 — Motor de datos para AgriPulse Argentina
Módulos: Mercado · Ratios · Clima · Campaña · Territorial · Brecha ·
         Simulador · Clima-Producción · Priority Score
Fuentes: SIIA/MAGyP · CIAFA · NASA POWER · MATBA-ROFEX · BCR · INTA
"""

import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Ruta base de datos
_DATA_DIR = Path(__file__).parent.parent / "data"


class AgriPulseEngine:

    # ─────────────────────────────────────────────
    # DOSIS TÉCNICA INTA (kg producto/ha por cultivo)
    # Fuente: INTA Córdoba / EEA Marcos Juárez
    # ─────────────────────────────────────────────
    TECH_DOSAGE = {
        'Maíz':    {'Urea': 180, 'MAP': 80,  'MOP': 60},
        'Soja':    {'Urea': 0,   'MAP': 90,  'MOP': 70},
        'Trigo':   {'Urea': 150, 'MAP': 100, 'MOP': 0},
        'Girasol': {'Urea': 80,  'MAP': 80,  'MOP': 0},
    }

    # ─────────────────────────────────────────────
    # URL para datos de Estimaciones Agrícolas
    # ─────────────────────────────────────────────
    SIIA_URL = "https://datos.magyp.gob.ar/dataset/9e1e77ba-267e-4eaa-a59f-3296e86b5f36/resource/95d066e6-8a0f-4a80-b59d-6f28f88eacd5/download/estimaciones-agricolas-2026-03.csv"

    # Partidos del AMBA sin producción agrícola real — excluidos de todos los cálculos
    _AMBA_URBAN = frozenset([
        'Almirante Brown', 'Avellaneda', 'Berazategui', 'Berisso', 'Ensenada',
        'Esteban Echeverría', 'Ezeiza', 'Florencio Varela', 'General San Martín',
        'Hurlingham', 'Ituzaingó', 'José C. Paz', 'La Matanza', 'Lanús',
        'Lomas de Zamora', 'Malvinas Argentinas', 'Merlo', 'Moreno', 'Morón',
        'Presidente Perón', 'Quilmes', 'San Fernando', 'San Isidro', 'San Miguel',
        'Tigre', 'Tres de Febrero', 'Vicente López',
    ])



    # ─────────────────────────────────────────────
    # PRECIOS FERTILIZANTES (USD/tn CIF Argentina)
    # Referencia CIAFA / mercado Marzo 2025
    # ─────────────────────────────────────────────
    FERTILIZER_PRICES = {
        'Urea':                 480,
        'MAP':                  685,
        'MOP':                  405,
        'UAN 32':               315,
        'Superfosfato Triple':  582,
    }

    # Precios de granos (USD/tn) - Actualizado 2026-03-13 desde https://www.ggsa.com.ar
    GRAIN_PRICES = {
        'Soja':    435.97,
        'Maíz':    170.47,
        'Trigo':   215.60,
        'Girasol': 395, # sin cambios
    }

    ZONES = {
        'Zona Núcleo (Pergamino)':      {'lat': -33.89, 'lon': -60.57},
        'Marcos Juárez (Córdoba)':      {'lat': -32.70, 'lon': -62.10},
        'Castellanos (Santa Fe)':       {'lat': -30.92, 'lon': -61.83},
        'Trenque Lauquen (BA)':         {'lat': -35.97, 'lon': -62.73},
        'Gral. Obligado (Santa Fe)':    {'lat': -28.46, 'lon': -59.67},
        'Anta (Salta)':                 {'lat': -24.84, 'lon': -63.28},
        'Río Cuarto (Córdoba)':         {'lat': -33.13, 'lon': -64.35},
    }

    # Rendimientos potenciales por zona agroclimática (tn/ha) — Fuente: INTA
    REND_POTENCIAL = {
        'Pampa Húmeda':   {'Soja': 4.2, 'Maíz': 11.0, 'Trigo': 4.5, 'Girasol': 2.8},
        'Pampa Semiárida':{'Soja': 2.8, 'Maíz':  7.5, 'Trigo': 3.0, 'Girasol': 2.2},
        'NEA':            {'Soja': 2.5, 'Maíz':  6.0, 'Trigo': 2.2, 'Girasol': 1.8},
        'NOA':            {'Soja': 2.6, 'Maíz':  8.5, 'Trigo': 2.8, 'Girasol': 2.0},
    }

    # Zona agroclimática por provincia (simplificado)
    ZONA_PROV = {
        'Buenos Aires':       'Pampa Húmeda',
        'Córdoba':            'Pampa Húmeda',
        'Santa Fe':           'Pampa Húmeda',
        'Entre Ríos':         'NEA',
        'La Pampa':           'Pampa Semiárida',
        'Salta':              'NOA',
        'Santiago del Estero':'NOA',
        'Tucumán':            'NOA',
        'Chaco':              'NEA',
        'Formosa':            'NEA',
        'Corrientes':         'NEA',
        'Misiones':           'NEA',
    }

    # Excepción departamental para zonas dentro de provincia mixta
    ZONA_DEPTO = {
        ('Buenos Aires', 'Trenque Lauquen'): 'Pampa Semiárida',
        ('Buenos Aires', 'Pehuajó'):         'Pampa Semiárida',
        ('Córdoba',      'Río Cuarto'):      'Pampa Semiárida',
        ('Córdoba',      'Río Primero'):     'Pampa Semiárida',
        ('La Pampa',     'Realicó'):         'Pampa Semiárida',
        ('La Pampa',     'Maracó'):          'Pampa Semiárida',
    }

    def _get_zona(self, provincia, departamento):
        return self.ZONA_DEPTO.get((provincia, departamento),
               self.ZONA_PROV.get(provincia, 'Pampa Húmeda'))

    # ─────────────────────────────────────────────
    # Fecha actual — conciencia de campaña
    # Hoy: Marzo 2026 → campaña gruesa 2025/26 en R5-R6
    # ─────────────────────────────────────────────
    TODAY = datetime.now()
    CURRENT_YEAR = TODAY.year    # 2026
    CURRENT_MONTH = TODAY.month  # 3 (Marzo)

    # Estado fenológico real por cultivo en Marzo (fin de verano Argentina)
    # Fuente: INTA — calendario de cultivos pampa húmeda
    ESTADO_ACTUAL_CULTIVOS = {
        'Maíz': {
            'estadio': 'R5-R6 — Llenado de grano / Madurez fisiológica',
            'ventana_activa': False,
            'mensaje': 'Sin ventana de fertilización activa. El ciclo actual está en etapa final.',
            'proxima_ventana': 'Septiembre-Octubre 2026 (siembra nueva campaña → MAP+MOP en línea)',
            'dias_proxima': 200,
        },
        'Soja': {
            'estadio': 'R5-R7 — Llenado de vainas / Pre-cosecha',
            'ventana_activa': False,
            'mensaje': 'La soja en Marzo está en madurez. Sin ventana de fertilización activa.',
            'proxima_ventana': 'Octubre-Noviembre 2026 (siembra nueva campaña → MAP+MOP)',
            'dias_proxima': 215,
        },
        'Trigo': {
            'estadio': 'Barbecho / Pre-siembra (cultivo no activo)',
            'ventana_activa': False,
            'mensaje': 'El trigo de invierno aún no fue sembrado. Siembra esperada Mayo-Junio.',
            'proxima_ventana': 'Mayo-Junio 2026 (siembra → MAP) · Julio-Agosto (macollaje → Urea)',
            'dias_proxima': 75,
        },
        'Girasol': {
            'estadio': 'R7-R9 — Madurez fisiológica / Cosecha',
            'ventana_activa': False,
            'mensaje': 'Girasol en etapa final de campaña. Próxima siembra en primavera.',
            'proxima_ventana': 'Septiembre-Octubre 2026 (siembra nueva campaña)',
            'dias_proxima': 200,
        },
    }

    _siia_df  = None
    _sup_df   = None   # Cache local siia_superficie.csv (columnas conocidas)
    _prod_df  = None
    _rend_df  = None

    def _load_siia_data(self):
        """Carga datos remotos (MAGyP URL). Solo para módulos que usen su estructura."""
        if self._siia_df is None:
            try:
                self.__class__._siia_df = pd.read_csv(self.SIIA_URL)
            except Exception as e:
                print(f"Error descargando SIIA URL: {e}")
                self.__class__._siia_df = self._load_sup()
        return self._siia_df

    def _load_sup(self):
        """Carga local siia_superficie.csv (año, provincia, departamento, cultivo, lat, lon, zona_agroclimatica, sup_sembrada_ha)."""
        if self._sup_df is None:
            p = _DATA_DIR / 'siia_superficie.csv'
            df = pd.read_csv(p)
            self.__class__._sup_df = df[
                ~((df['provincia'] == 'Buenos Aires') & (df['departamento'].isin(self._AMBA_URBAN)))
            ].reset_index(drop=True)
        return self._sup_df

    def _load_prod(self):
        """Carga local siia_produccion.csv."""
        if self._prod_df is None:
            p = _DATA_DIR / 'siia_produccion.csv'
            df = pd.read_csv(p)
            self.__class__._prod_df = df[
                ~((df['provincia'] == 'Buenos Aires') & (df['departamento'].isin(self._AMBA_URBAN)))
            ].reset_index(drop=True)
        return self._prod_df

    def _load_rend(self):
        """Carga local siia_rendimiento.csv."""
        if self._rend_df is None:
            p = _DATA_DIR / 'siia_rendimiento.csv'
            df = pd.read_csv(p)
            self.__class__._rend_df = df[
                ~((df['provincia'] == 'Buenos Aires') & (df['departamento'].isin(self._AMBA_URBAN)))
            ].reset_index(drop=True)
        return self._rend_df

    def get_estado_fenologico_actual(self, cultivo='Maíz'):
        """
        Retorna el estado fenológico real del cultivo para la fecha actual (Marzo 2026).
        Conciencia de campaña: fin de verano en Argentina.
        """
        return self.ESTADO_ACTUAL_CULTIVOS.get(cultivo, self.ESTADO_ACTUAL_CULTIVOS['Maíz'])

    def get_ventanas_fertilizacion(self):
        """
        Retorna el calendario de ventanas de fertilización para todos los cultivos.
        Estado calculado respecto a la fecha actual (Marzo 2026).
        """
        # Mes actual: 3 (Marzo)
        m = self.CURRENT_MONTH

        def estado(mes_ini, mes_fin):
            """Calcula estado de una ventana dado el mes actual."""
            # Ventanas que cruzan año (ej. Nov-Ene)
            if mes_ini <= mes_fin:
                activa = mes_ini <= m <= mes_fin
                proxima = (m < mes_ini) and (mes_ini - m <= 2)
                cerrada = m > mes_fin
            else:
                activa = m >= mes_ini or m <= mes_fin
                proxima = not activa and (mes_ini - m) % 12 <= 2
                cerrada = not activa and not proxima
            if activa:    return '🟢 ACTIVA'
            if proxima:   return '🟡 PRÓXIMA'
            if cerrada:   return '⭕ CERRADA'
            return '⚪ FUTURA'

        ventanas = [
            # cultivo, estadio, fertilizante, mes_ini, mes_fin, descripción
            ('Maíz',    'Siembra (V0)',         'MAP+MOP',  9,  10, 'Fertilización de arranque en línea'),
            ('Maíz',    'Cobertura (V4-V6)',    'Urea/UAN', 11, 12, 'Ventana óptima N: +40% absorción'),
            ('Maíz 2°', 'Siembra (V0)',         'MAP+MOP',  12, 1,  'Maíz de segunda fecha'),
            ('Maíz 2°', 'Cobertura (V4-V6)',    'Urea/UAN', 2,  3,  'Cobertura tardía 2da fecha'),
            ('Soja',    'Siembra',              'MAP+MOP',  10, 11, 'Fertilización de arranque soja'),
            ('Trigo',   'Siembra',              'MAP',      5,  6,  'Fertilización en línea trigo'),
            ('Trigo',   'Macollaje',            'Urea',     7,  8,  'Ventana N: mayor impacto en rendimiento'),
            ('Cebada',  'Siembra',              'MAP',      5,  6,  'Similar a trigo'),
            ('Cebada',  'Macollaje',            'Urea',     7,  7,  'Ventana N cebada'),
            ('Girasol', 'Siembra',              'MAP+Urea', 9,  10, 'Fertilización arranque girasol'),
            ('Sorgo',   'Siembra',              'MAP+Urea', 10, 11, 'Fertilización arranque sorgo'),
        ]

        rows = []
        for cultivo, estadio, fert, mi, mf, desc in ventanas:
            st = estado(mi, mf)
            meses_nombre = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',
                           7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}
            ventana_str = f"{meses_nombre[mi]}-{meses_nombre[mf]}"
            rows.append({
                'cultivo': cultivo,
                'estadio': estadio,
                'fertilizante': fert,
                'ventana': ventana_str,
                'mes_ini': mi,
                'mes_fin': mf,
                'estado': st,
                'descripcion': desc,
            })

        df = pd.DataFrame(rows)

        # Productos críticos en los próximos 30 días
        criticos = df[df['estado'].isin(['🟢 ACTIVA', '🟡 PRÓXIMA'])]['fertilizante'].unique().tolist()
        ventanas_activas = int((df['estado'] == '🟢 ACTIVA').sum())
        ventanas_proximas = int((df['estado'] == '🟡 PRÓXIMA').sum())

        return df, {
            'ventanas_activas': ventanas_activas,
            'ventanas_proximas': ventanas_proximas,
            'productos_criticos': criticos,
            'mensaje': (
                f"{'✅ ' + str(ventanas_activas) + ' ventana(s) ACTIVA(S)' if ventanas_activas else 'Sin ventanas activas en este momento'}. "
                f"{str(ventanas_proximas) + ' ventana(s) próxima(s) en < 60 días.' if ventanas_proximas else 'Próximas ventanas en más de 60 días.'}"
            )
        }

    def _build_market_df(self, cultivo_filter='Todos', provincia_filter='Todas'):
        """
        Construye el dataset de mercado desde los CSVs históricos (año 2024).
        Reemplaza el SIIA_DATA hardcodeado con datos reales para 300+ departamentos.
        """
        df_sup = self._load_sup()
        # Usar datos de 2024 (última campaña disponible)
        df = df_sup[df_sup['año'] == 2024].copy()

        if cultivo_filter not in ('Todos', 'Todas', '', None):
            df = df[df['cultivo'] == cultivo_filter]
        if provincia_filter not in ('Todas', 'Todos', '', None):
            df = df[df['provincia'] == provincia_filter]

        # Usar zona_agroclimatica del CSV
        if 'zona_agroclimatica' not in df.columns:
            zona_prov = self.ZONA_PROV
            df['zona_agroclimatica'] = df['provincia'].map(zona_prov).fillna('Pampa Húmeda')

        df = df.rename(columns={'sup_sembrada_ha': 'area_ha'})
        return df

    # ══════════════════════════════════════════════════════════
    # MÓDULO 1 — Potencial de Mercado (carga desde CSV real)
    # ══════════════════════════════════════════════════════════
    def get_market_potential(self, cultivo_filter='Todos', provincia_filter='Todas',
                             fertilizante_filter='Todos'):
        """
        Calcula demanda potencial de fertilizante por departamento.
        Fuente: CSVs SIIA/MAGyP 2024 + dosis técnica INTA.
        Cubre 300+ departamentos de 10 provincias clave.
        """
        df = self._build_market_df(cultivo_filter, provincia_filter)
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()

        records = []
        for _, row in df.iterrows():
            dosages = self.TECH_DOSAGE.get(row['cultivo'], {})
            for fert, dose_kg_ha in dosages.items():
                if dose_kg_ha == 0:
                    continue
                if fertilizante_filter != 'Todos' and fert != fertilizante_filter:
                    continue
                demanda_tn = row['area_ha'] * dose_kg_ha / 1000
                precio_fert = self.FERTILIZER_PRICES.get(fert, 500)
                records.append({
                    'provincia':            row['provincia'],
                    'departamento':         row['departamento'],
                    'lat':                  row['lat'],
                    'lon':                  row['lon'],
                    'cultivo':              row['cultivo'],
                    'area_ha':              row['area_ha'],
                    'zona_agroclimatica':   row.get('zona_agroclimatica', ''),
                    'fertilizante':         fert,
                    'dosis_kg_ha':          dose_kg_ha,
                    'demanda_potencial_tn': round(demanda_tn),
                    'valor_mercado_musd':   round(demanda_tn * precio_fert / 1_000_000, 3),
                })

        result = pd.DataFrame(records)
        if result.empty:
            return result, pd.DataFrame()

        map_df = (
            result.groupby(['provincia', 'departamento', 'cultivo', 'lat', 'lon', 'area_ha'])
            .agg(demanda_total_tn=('demanda_potencial_tn', 'sum'),
                 valor_total_musd=('valor_mercado_musd', 'sum'))
            .reset_index()
        )
        return result, map_df

    # ══════════════════════════════════════════════════════════
    # MÓDULO 2 — Ratios Insumo/Grano
    # ══════════════════════════════════════════════════════════
    def get_price_ratios(self):
        ratios = []
        for grain, g_price in self.GRAIN_PRICES.items():
            for fert, f_price in self.FERTILIZER_PRICES.items():
                ratio = f_price / g_price
                ratios.append({
                    'grano':                    grain,
                    'fertilizante':             fert,
                    'precio_grano_usd_tn':      g_price,
                    'precio_fert_usd_tn':       f_price,
                    'ratio':                    round(ratio, 2),
                    'kg_grano_x_kg_fert':       round(ratio, 2),
                    'kg_grano_x_bolsa_50kg':    round(ratio * 50, 1),
                })
        return pd.DataFrame(ratios)

    def get_price_history(self, grain='Soja', fertilizer='Urea'):
        historical_data = {
            ('Soja', 'Urea'): [
                ('2020-01', 1.45), ('2020-04', 1.38), ('2020-07', 1.52), ('2020-10', 1.48),
                ('2021-01', 1.31), ('2021-04', 1.28), ('2021-07', 1.85), ('2021-10', 2.10),
                ('2022-01', 2.45), ('2022-04', 2.68), ('2022-07', 2.35), ('2022-10', 1.98),
                ('2023-01', 1.72), ('2023-04', 1.65), ('2023-07', 1.58), ('2023-10', 1.52),
                ('2024-01', 1.48), ('2024-04', 1.44), ('2024-07', 1.42), ('2024-10', 1.40),
                ('2025-01', 1.39),
            ],
            ('Maíz', 'Urea'): [
                ('2020-01', 2.65), ('2020-04', 2.48), ('2020-07', 2.72), ('2020-10', 2.58),
                ('2021-01', 2.45), ('2021-04', 2.38), ('2021-07', 3.12), ('2021-10', 3.45),
                ('2022-01', 4.05), ('2022-04', 4.35), ('2022-07', 3.88), ('2022-10', 3.20),
                ('2023-01', 2.85), ('2023-04', 2.72), ('2023-07', 2.62), ('2023-10', 2.55),
                ('2024-01', 2.49), ('2024-04', 2.44), ('2024-07', 2.41), ('2024-10', 2.40),
                ('2025-01', 2.55),
            ],
            ('Trigo', 'Urea'): [
                ('2020-01', 1.95), ('2020-04', 1.85), ('2020-07', 1.98), ('2020-10', 1.92),
                ('2021-01', 1.80), ('2021-04', 1.75), ('2021-07', 2.45), ('2021-10', 2.68),
                ('2022-01', 3.05), ('2022-04', 3.25), ('2022-07', 2.90), ('2022-10', 2.42),
                ('2023-01', 2.15), ('2023-04', 2.05), ('2023-07', 1.98), ('2023-10', 1.95),
                ('2024-01', 1.91), ('2024-04', 1.88), ('2024-07', 1.85), ('2024-10', 1.82),
                ('2025-01', 2.11),
            ],
        }
        key = (grain, fertilizer)
        if key in historical_data:
            dates, values = zip(*historical_data[key])
            df = pd.DataFrame({'fecha': pd.to_datetime(dates), 'ratio': values})
        else:
            base_ratio = self.FERTILIZER_PRICES.get(fertilizer, 500) / self.GRAIN_PRICES.get(grain, 300)
            dates = pd.date_range('2020-01', '2025-03', freq='QS')
            ratios = []
            for i, _ in enumerate(dates):
                peak_factor = np.exp(-((i - 9) ** 2) / 15)
                ratios.append(round(base_ratio * (0.85 + 0.65 * peak_factor), 2))
            df = pd.DataFrame({'fecha': dates, 'ratio': ratios})

        current_ratio = self.FERTILIZER_PRICES.get(fertilizer, 500) / self.GRAIN_PRICES.get(grain, 300)
        df['es_actual'] = False
        df.loc[df.index[-1], 'es_actual'] = True
        df.loc[df.index[-1], 'ratio'] = round(current_ratio, 2)
        pct = round((df['ratio'] <= current_ratio).mean() * 100, 0)
        return df, current_ratio, int(pct)

    # ══════════════════════════════════════════════════════════
    # MÓDULO 3 — Inteligencia Climática (NASA POWER)
    # ══════════════════════════════════════════════════════════
    _CLIM_NORMALS = {
        1: (26.5, 115, 68, 22.0), 2: (25.8, 98, 70, 20.5),
        3: (22.5, 105, 72, 17.0), 4: (17.2, 68, 74, 13.0),
        5: (12.8, 48, 78, 9.5),  6: (9.5, 32, 80, 8.0),
        7: (9.0, 30, 79, 8.5),   8: (11.2, 35, 76, 11.0),
        9: (14.8, 52, 74, 14.5), 10: (19.5, 88, 70, 18.5),
        11: (23.2, 102, 67, 21.0), 12: (25.8, 118, 66, 23.0),
    }

    def get_weather_intel(self, lat, lon, days_back=30):
        end_dt   = datetime.now() - timedelta(days=2)
        start_dt = end_dt - timedelta(days=days_back)
        params = {
            'parameters': 'T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN',
            'community': 'AG', 'longitude': lon, 'latitude': lat,
            'start': start_dt.strftime('%Y%m%d'), 'end': end_dt.strftime('%Y%m%d'),
            'format': 'JSON',
        }
        try:
            r = requests.get('https://power.larc.nasa.gov/api/temporal/daily/point',
                             params=params, timeout=20)
            if r.status_code == 200:
                props = r.json()['properties']['parameter']
                dates  = list(props['T2M'].keys())
                NASA_FILL = -999.0

                def clean(vals):
                    return [v if v != NASA_FILL else float('nan') for v in vals]

                temps_c  = clean(list(props['T2M'].values()))
                precip_c = clean(list(props['PRECTOTCORR'].values()))
                hum_c    = clean(list(props['RH2M'].values()))
                rad_c    = clean(list(props['ALLSKY_SFC_SW_DWN'].values()))

                valid_temps  = [t for t in temps_c if t == t]
                valid_precip = [p for p in precip_c if p == p]
                valid_hum    = [h for h in hum_c if h == h]
                if not valid_temps:
                    raise ValueError('NASA POWER: sin datos válidos')

                df = pd.DataFrame({
                    'fecha':       pd.to_datetime(dates, format='%Y%m%d'),
                    'temp_c':      [round(t, 1) if t == t else float('nan') for t in temps_c],
                    'precip_mm':   [max(0, round(p, 1)) if p == p else 0.0 for p in precip_c],
                    'humedad_pct': [round(h, 0) if h == h else float('nan') for h in hum_c],
                    'radiacion':   [round(rd, 1) if rd == rd else float('nan') for rd in rad_c],
                    'gdd':         [max(0, round(t - 10, 1)) if t == t else 0.0 for t in temps_c],
                })
                return {
                    'fuente': 'NASA POWER (real)', 'success': True, 'df': df,
                    'precip_total': round(sum(p for p in valid_precip if p > 0), 1),
                    'temp_avg':     round(sum(valid_temps) / len(valid_temps), 1),
                    'temp_max':     round(max(valid_temps), 1),
                    'temp_min':     round(min(valid_temps), 1),
                    'gdd_acum':     round(sum(max(0, t - 10) for t in valid_temps), 0),
                    'dias_lluvia':  sum(1 for p in valid_precip if p > 1),
                    'hum_avg':      round(sum(valid_hum) / len(valid_hum), 0) if valid_hum else 0,
                }
        except Exception:
            pass
        return self._fallback_weather(lat, lon, days_back)

    def _fallback_weather(self, lat, lon, days_back=30):
        lat_adj = (abs(lat) - 33) * (-0.6)
        dates = pd.date_range(end=datetime.now() - timedelta(days=2), periods=days_back)
        temps, precips, hums, rads = [], [], [], []
        for i, d in enumerate(dates):
            t_base, p_month, h, rd = self._CLIM_NORMALS[d.month]
            day_frac = d.day / 30
            temps.append(round(t_base + lat_adj + 2.5 * np.sin(2 * np.pi * day_frac + i * 0.3), 1))
            precips.append(round(max(0, (p_month / 30) * (3.5 if (i % 7) < 2 else 0.2)), 1))
            hums.append(round(min(95, max(30, h + 5 * np.sin(2 * np.pi * day_frac))), 0))
            rads.append(round(max(0, rd * (0.85 + 0.3 * np.cos(2 * np.pi * day_frac))), 1))

        temps_arr, precips_arr, hums_arr = np.array(temps), np.array(precips), np.array(hums)
        df = pd.DataFrame({'fecha': dates, 'temp_c': temps_arr, 'precip_mm': precips_arr,
                           'humedad_pct': hums_arr, 'radiacion': rads,
                           'gdd': np.maximum(0, temps_arr - 10).round(1)})
        return {
            'fuente': 'Referencia climatológica SMN/INTA (NASA sin conexión)',
            'success': False, 'df': df,
            'precip_total': round(float(precips_arr.sum()), 1),
            'temp_avg':     round(float(temps_arr.mean()), 1),
            'temp_max':     round(float(temps_arr.max()), 1),
            'temp_min':     round(float(temps_arr.min()), 1),
            'gdd_acum':     round(float(np.maximum(0, temps_arr - 10).sum()), 0),
            'dias_lluvia':  int((precips_arr > 1).sum()),
            'hum_avg':      round(float(hums_arr.mean()), 0),
        }

    # ══════════════════════════════════════════════════════════
    # MÓDULO 3b — Historial Climático Multi-decadal (NASA POWER monthly)
    # ══════════════════════════════════════════════════════════
    def get_climate_history(self, lat, lon, start_year=2005, end_year=2024):
        """Monthly historical climate data from NASA POWER for multi-year analysis.

        Returns dict:
            success  : bool
            fuente   : str
            df       : DataFrame(year, month, date, temp_mean, temp_max, temp_min,
                                 precip[mm/month], humidity[%], radiation[MJ/m²/d], gdd)
        """
        import calendar
        params = {
            'parameters': 'T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN',
            'community': 'AG',
            'longitude': lon,
            'latitude':  lat,
            'start':     f'{start_year}01',
            'end':       f'{end_year}12',
            'format':    'JSON',
        }
        try:
            r = requests.get(
                'https://power.larc.nasa.gov/api/temporal/monthly/point',
                params=params, timeout=45,
            )
            if r.status_code == 200:
                props     = r.json()['properties']['parameter']
                NASA_FILL = -999.0

                def _cd(d):
                    return {k: (float(v) if float(v) != NASA_FILL else float('nan'))
                            for k, v in d.items()}

                t2m     = _cd(props.get('T2M', {}))
                t2m_max = _cd(props.get('T2M_MAX', {}))
                t2m_min = _cd(props.get('T2M_MIN', {}))
                prec    = _cd(props.get('PRECTOTCORR', {}))
                rh2m    = _cd(props.get('RH2M', {}))
                rad     = _cd(props.get('ALLSKY_SFC_SW_DWN', {}))

                records = []
                for key in sorted(t2m.keys()):
                    if len(key) == 6 and key.isdigit():
                        yr, mo = int(key[:4]), int(key[4:])
                        if not (start_year <= yr <= end_year and 1 <= mo <= 12):
                            continue
                        tm    = t2m.get(key, float('nan'))
                        ndays = calendar.monthrange(yr, mo)[1]
                        p_rt  = prec.get(key, float('nan'))
                        p_tot = (p_rt * ndays) if not np.isnan(p_rt) else float('nan')
                        records.append({
                            'year':      yr,
                            'month':     mo,
                            'date':      pd.Timestamp(yr, mo, 1),
                            'temp_mean': round(tm, 1) if not np.isnan(tm) else float('nan'),
                            'temp_max':  round(t2m_max.get(key, float('nan')), 1),
                            'temp_min':  round(t2m_min.get(key, float('nan')), 1),
                            'precip':    round(max(0, p_tot), 1) if not np.isnan(p_tot) else float('nan'),
                            'humidity':  round(rh2m.get(key, float('nan')), 1),
                            'radiation': round(rad.get(key, float('nan')), 2),
                            'gdd':       round(max(0, tm - 10) * ndays, 1) if not np.isnan(tm) else 0.0,
                        })
                if len(records) >= 12:
                    df = pd.DataFrame(records).sort_values('date').reset_index(drop=True)
                    return {'success': True, 'fuente': 'NASA POWER (real)', 'df': df}
        except Exception:
            pass
        return self._fallback_climate_history(lat, lon, start_year, end_year)

    def _fallback_climate_history(self, lat, lon, start_year=2005, end_year=2024):
        """Synthetic monthly climate history using climatological normals + interannual variability."""
        import calendar
        lat_adj    = (abs(lat) - 33) * (-0.6)
        precip_adj = 1.0 + (33 - abs(lat)) * 0.025
        seed       = int(abs(lat * 100) + abs(lon * 100)) % (2**31 - 1)
        rng        = np.random.RandomState(seed)
        records    = []
        for yr in range(start_year, end_year + 1):
            enso_phase   = np.sin(2 * np.pi * (yr - 2000) / 4.5)
            yr_temp_anom = rng.normal(0, 0.35) + 0.022 * (yr - 2000)
            yr_prec_fac  = rng.lognormal(0, 0.17) * (1 - 0.10 * enso_phase) * precip_adj
            for mo in range(1, 13):
                t_base, p_month, h_base, rd_base = self._CLIM_NORMALS[mo]
                ndays  = calendar.monthrange(yr, mo)[1]
                tm     = round(t_base + lat_adj + yr_temp_anom + rng.normal(0, 0.4), 1)
                precip = round(max(0, p_month * yr_prec_fac * (0.65 + 0.7 * rng.random())), 1)
                hum    = round(min(95, max(25, h_base + rng.normal(0, 3.2))), 1)
                rd     = round(max(0.5, rd_base * (0.78 + 0.44 * rng.random())), 2)
                records.append({
                    'year':      yr,
                    'month':     mo,
                    'date':      pd.Timestamp(yr, mo, 1),
                    'temp_mean': tm,
                    'temp_max':  round(tm + 6.5 + rng.normal(0, 0.6), 1),
                    'temp_min':  round(tm - 6.0 + rng.normal(0, 0.6), 1),
                    'precip':    precip,
                    'humidity':  hum,
                    'radiation': rd,
                    'gdd':       round(max(0, tm - 10) * ndays, 1),
                })
        df = pd.DataFrame(records).sort_values('date').reset_index(drop=True)
        return {'success': False, 'fuente': 'Climatología sintética SMN/INTA', 'df': df}

    def get_phenology_stage(self, crop, gdd_acum):
        stages = {
            'Maíz': [(0,'VE — Emergencia'),(100,'V3 — 3 hojas'),(200,'V6 — 6 hojas  ⭐ VENTANA N'),
                     (370,'V10 — 10 hojas'),(530,'VT — Panojamiento'),(670,'R1 — Floración'),
                     (830,'R2 — Grano lechoso'),(1000,'R4 — Masa dough'),(1200,'R6 — Madurez fisiológica')],
            'Trigo': [(0,'Emergencia'),(150,'Macollaje  ⭐ VENTANA N'),(350,'Encañazón'),
                      (500,'Espigazón'),(650,'Antesis'),(900,'Grano lechoso'),(1200,'Madurez fisiológica')],
        }
        crop_stages = stages.get(crop, stages['Maíz'])
        current = crop_stages[0][1]
        for threshold, name in crop_stages:
            if gdd_acum >= threshold:
                current = name
        return current

    # ══════════════════════════════════════════════════════════
    # MÓDULO 4 — Pulso de Campaña (BCR)
    # ══════════════════════════════════════════════════════════
    def get_bcr_campaign_data(self):
        return {
            'soja': {
                'nombre': 'Soja 2024/25', 'area_nacional_mha': 17.2,
                'avance_siembra_pct': 98, 'avance_cosecha_pct': 12,
                'rendimiento_esp_tn_ha': 3.2, 'produccion_esp_mtn': 55.0,
                'historico_semanal': {
                    'semanas': ['S35','S36','S37','S38','S39','S40','S41','S42','S43'],
                    'actual':  [2, 6, 14, 28, 48, 68, 84, 95, 98],
                    'prom5y':  [3, 7, 16, 31, 52, 71, 86, 96, 99],
                },
            },
            'maiz': {
                'nombre': 'Maíz 2024/25', 'area_nacional_mha': 8.4,
                'avance_siembra_pct': 100, 'avance_cosecha_pct': 8,
                'rendimiento_esp_tn_ha': 7.8, 'produccion_esp_mtn': 65.5,
                'historico_semanal': {
                    'semanas': ['S35','S36','S37','S38','S39','S40','S41','S42','S43'],
                    'actual':  [5, 12, 26, 45, 65, 82, 94, 99, 100],
                    'prom5y':  [4, 11, 24, 44, 63, 80, 93, 98, 100],
                },
            },
            'trigo': {
                'nombre': 'Trigo 2024/25', 'area_nacional_mha': 6.8,
                'avance_siembra_pct': 100, 'avance_cosecha_pct': 100,
                'rendimiento_esp_tn_ha': 2.98, 'produccion_esp_mtn': 18.6,
                'historico_semanal': {
                    'semanas': ['S20','S21','S22','S23','S24','S25','S26','S27'],
                    'actual':  [10, 28, 52, 73, 88, 97, 100, 100],
                    'prom5y':  [8,  25, 49, 70, 86, 96, 100, 100],
                },
            },
        }

    def get_ciafa_consumption(self):
        return pd.DataFrame([
            {'año': 2015, 'Urea': 1.28, 'MAP': 0.82, 'MOP': 0.41, 'Otros': 0.61, 'Total': 3.12},
            {'año': 2016, 'Urea': 1.35, 'MAP': 0.88, 'MOP': 0.43, 'Otros': 0.62, 'Total': 3.28},
            {'año': 2017, 'Urea': 1.48, 'MAP': 0.95, 'MOP': 0.45, 'Otros': 0.67, 'Total': 3.55},
            {'año': 2018, 'Urea': 1.52, 'MAP': 0.92, 'MOP': 0.44, 'Otros': 0.63, 'Total': 3.51},
            {'año': 2019, 'Urea': 1.38, 'MAP': 0.85, 'MOP': 0.40, 'Otros': 0.55, 'Total': 3.18},
            {'año': 2020, 'Urea': 1.45, 'MAP': 0.89, 'MOP': 0.42, 'Otros': 0.59, 'Total': 3.35},
            {'año': 2021, 'Urea': 1.68, 'MAP': 1.02, 'MOP': 0.48, 'Otros': 0.67, 'Total': 3.85},
            {'año': 2022, 'Urea': 1.55, 'MAP': 0.94, 'MOP': 0.44, 'Otros': 0.65, 'Total': 3.58},
            {'año': 2023, 'Urea': 1.22, 'MAP': 0.75, 'MOP': 0.38, 'Otros': 0.53, 'Total': 2.88},
            {'año': 2024, 'Urea': 1.48, 'MAP': 0.91, 'MOP': 0.44, 'Otros': 0.62, 'Total': 3.45},
        ])

    # ══════════════════════════════════════════════════════════
    # MÓDULO A — Clasificación Territorial (CAGR + proyección)
    # ══════════════════════════════════════════════════════════
    def get_territorial_classification(self, cultivo='Soja', periodo_anios=10):
        """
        Clasifica departamentos por CAGR de área sembrada.
        Categorías: EXPANSIÓN / MADUREZ / CONTRACCIÓN / EMERGENTE
        Incluye proyección polinómica a 2 campañas con R².
        """
        df = self._load_sup()
        df = df[df['cultivo'] == cultivo].copy()

        anio_fin = 2024
        anio_ini = max(2000, anio_fin - periodo_anios)

        # Serie corta para EMERGENTE (últimos 3 años)
        anio_emg = anio_fin - 3

        records = []
        for (prov, dept), g in df.groupby(['provincia', 'departamento']):
            g = g.sort_values('año')
            g_per = g[(g['año'] >= anio_ini) & (g['año'] <= anio_fin)]
            if len(g_per) < 4:
                continue

            ha_ini = g_per[g_per['año'] == g_per['año'].min()]['sup_sembrada_ha'].values[0]
            ha_fin = g_per[g_per['año'] == anio_fin]['sup_sembrada_ha'].values
            if len(ha_fin) == 0 or ha_ini <= 0:
                continue
            ha_fin = ha_fin[0]
            n = g_per['año'].max() - g_per['año'].min()
            cagr = (ha_fin / ha_ini) ** (1 / max(n, 1)) - 1 if ha_ini > 0 else 0

            # EMERGENTE: CAGR últimos 3 años > 5% desde base relativamente baja
            g_emg = g[g['año'] >= anio_emg]
            emg_ha_ini = g_emg['sup_sembrada_ha'].iloc[0] if len(g_emg) > 1 else ha_fin
            emg_ha_fin = g_emg['sup_sembrada_ha'].iloc[-1] if len(g_emg) > 1 else ha_fin
            cagr_emg = (emg_ha_fin / max(emg_ha_ini, 1)) ** (1 / 3) - 1

            if cagr_emg > 0.05 and ha_fin < 200_000:
                clasificacion = 'EMERGENTE'
                color = '#3b82f6'
            elif cagr > 0.02:
                clasificacion = 'EXPANSIÓN'
                color = '#00A34F'
            elif cagr < -0.01:
                clasificacion = 'CONTRACCIÓN'
                color = '#dc2626'
            else:
                clasificacion = 'MADUREZ'
                color = '#f59e0b'

            # Proyección polinómica
            g_full = g[g['año'] >= 2010]
            x = g_full['año'].values
            y = g_full['sup_sembrada_ha'].values
            if len(x) >= 5:
                coeffs = np.polyfit(x, y, deg=1)
                y_hat = np.polyval(coeffs, x)
                ss_res = np.sum((y - y_hat) ** 2)
                ss_tot = np.sum((y - y.mean()) ** 2)
                r2 = max(0, 1 - ss_res / ss_tot) if ss_tot > 0 else 0
                proj_2026 = max(0, round(np.polyval(coeffs, 2026)))
                proj_2027 = max(0, round(np.polyval(coeffs, 2027)))
                std_res = np.std(y - y_hat)
                ci80 = round(std_res * 1.28)
                ci95 = round(std_res * 1.96)
            else:
                r2, proj_2026, proj_2027, ci80, ci95 = 0, ha_fin, ha_fin, 0, 0

            # Metadata geo
            row_meta = g.iloc[-1]
            records.append({
                'provincia': prov, 'departamento': dept,
                'lat': row_meta['lat'], 'lon': row_meta['lon'],
                'zona_agroclimatica': row_meta.get('zona_agroclimatica', ''),
                'ha_actual': round(ha_fin),
                'ha_inicio_periodo': round(ha_ini),
                'cagr_pct': round(cagr * 100, 2),
                'cagr_emg_pct': round(cagr_emg * 100, 2),
                'clasificacion': clasificacion,
                'color': color,
                'proj_2026': proj_2026,
                'proj_2027': proj_2027,
                'ci80': ci80,
                'ci95': ci95,
                'r2': round(r2, 3),
                'cultivo': cultivo,
                'periodo_anios': periodo_anios,
            })

        df_out = pd.DataFrame(records)

        # Serie histórica completa para chart de detalle
        hist = df[df['año'] >= 2000][['año', 'provincia', 'departamento', 'sup_sembrada_ha']].copy()

        # Conteos por clasificación
        conteos = df_out['clasificacion'].value_counts().to_dict() if not df_out.empty else {}

        return df_out, hist, conteos

    # ══════════════════════════════════════════════════════════
    # MÓDULO B — Índice de Brecha Tecnológica
    # ══════════════════════════════════════════════════════════
    def get_technology_gap(self, cultivo='Soja', anios_prom=5):
        """
        Compara el rendimiento real promedio vs. el potencial INTA por zona.
        Calcula demanda adicional de fertilizante si se cierra la brecha.
        """
        df_rend = self._load_rend()
        df_sup  = self._load_sup()

        anio_fin = 2024
        anio_ini = anio_fin - anios_prom + 1

        rend_real = (
            df_rend[(df_rend['cultivo'] == cultivo) & (df_rend['año'].between(anio_ini, anio_fin))]
            .groupby(['provincia', 'departamento', 'lat', 'lon', 'zona_agroclimatica'])['rendimiento_tn_ha']
            .mean().reset_index()
            .rename(columns={'rendimiento_tn_ha': 'rend_real_avg'})
        )

        sup_act = (
            df_sup[(df_sup['cultivo'] == cultivo) & (df_sup['año'] == anio_fin)]
            [['provincia', 'departamento', 'sup_sembrada_ha']]
        )

        df = rend_real.merge(sup_act, on=['provincia', 'departamento'], how='left')
        df['sup_sembrada_ha'] = df['sup_sembrada_ha'].fillna(50_000)

        def pot(row):
            zona = row['zona_agroclimatica'] or self._get_zona(row['provincia'], row['departamento'])
            return self.REND_POTENCIAL.get(zona, self.REND_POTENCIAL['Pampa Húmeda']).get(cultivo, 3.0)

        df['rend_potencial'] = df.apply(pot, axis=1)
        df['brecha_tn_ha'] = (df['rend_potencial'] - df['rend_real_avg']).clip(lower=0)
        df['brecha_pct'] = (df['brecha_tn_ha'] / df['rend_potencial'] * 100).round(1)

        # Demanda adicional: si reduce brecha → más fertilizante necesario
        dosis_key = 'Urea' if cultivo in ('Maíz', 'Trigo') else 'MAP'
        dosis = self.TECH_DOSAGE.get(cultivo, {}).get(dosis_key, 80)
        precio_fert = self.FERTILIZER_PRICES.get(dosis_key, 500)

        df['demanda_adicional_tn'] = (
            df['brecha_pct'] / 100 * df['sup_sembrada_ha'] * dosis / 1000
        ).round(0)
        df['valor_oportunidad_usd_m'] = (
            df['demanda_adicional_tn'] * precio_fert / 1_000_000
        ).round(2)

        df['rend_real_avg']  = df['rend_real_avg'].round(2)
        df['rend_potencial'] = df['rend_potencial'].round(2)

        return df.sort_values('valor_oportunidad_usd_m', ascending=False).reset_index(drop=True)

    # ══════════════════════════════════════════════════════════
    # MÓDULO C — Simulador de Escenarios
    # ══════════════════════════════════════════════════════════
    def simulate_scenario(self,
                          precio_soja=345, precio_maiz=188,
                          precio_urea=480, precio_map=685,
                          var_area_pct=0, adopcion_pct=85):
        """
        Recalcula demanda de fertilizante y ratios bajo precios y área simulados.
        Retorna dict con todos los KPIs del escenario.
        """
        precios_grano = {
            'Soja': precio_soja, 'Maíz': precio_maiz,
            'Trigo': self.GRAIN_PRICES['Trigo'],
            'Girasol': self.GRAIN_PRICES['Girasol'],
        }
        precios_fert = {
            'Urea': precio_urea, 'MAP': precio_map,
            'MOP': self.FERTILIZER_PRICES['MOP'],
            'UAN 32': self.FERTILIZER_PRICES['UAN 32'],
            'Superfosfato Triple': self.FERTILIZER_PRICES['Superfosfato Triple'],
        }

        # _build_market_df filtra año=2024 y renombra sup_sembrada_ha -> area_ha
        df = self._build_market_df()
        factor_area = 1 + var_area_pct / 100
        factor_adopt = adopcion_pct / 100

        total_dem_tn = 0
        total_valor_musd = 0
        ratios_sim = []
        zona_cambios = []

        for _, row in df.iterrows():
            area_sim = row['area_ha'] * factor_area
            dosages = self.TECH_DOSAGE.get(row['cultivo'], {})
            dem_depto = 0
            val_depto = 0
            for fert, dose in dosages.items():
                if dose > 0:
                    dem = area_sim * dose / 1000 * factor_adopt
                    val = dem * precios_fert.get(fert, 500) / 1_000_000
                    dem_depto += dem
                    val_depto += val
            total_dem_tn += dem_depto
            total_valor_musd += val_depto

            # Cuánto cambia vs base
            base_dem = sum(
                row['area_ha'] * d / 1000 * 0.85
                for d in (self.TECH_DOSAGE.get(row['cultivo'], {}).values())
            )
            delta_pct = ((dem_depto - base_dem) / max(base_dem, 1)) * 100
            zona_cambios.append({
                'departamento': row['departamento'],
                'provincia': row['provincia'],
                'cultivo': row['cultivo'],
                'dem_sim_tn': round(dem_depto),
                'delta_pct': round(delta_pct, 1),
            })

        # Ratios simulados
        for grain, g_price in precios_grano.items():
            for fert, f_price in precios_fert.items():
                ratios_sim.append({
                    'grano': grain, 'fertilizante': fert,
                    'ratio_sim': round(f_price / max(g_price, 1), 2),
                    'ratio_base': round(self.FERTILIZER_PRICES.get(fert, 500) /
                                        max(self.GRAIN_PRICES.get(grain, 300), 1), 2),
                })
        ratios_sim_df = pd.DataFrame(ratios_sim)
        ratios_sim_df['delta'] = ratios_sim_df['ratio_sim'] - ratios_sim_df['ratio_base']

        # Gauge: momento de compra 0-100 (inverso del ratio Soja/Urea)
        ratio_soja_urea = precio_urea / max(precio_soja, 1)
        ratio_hist_min, ratio_hist_max = 1.28, 2.68
        gauge = int(100 * (1 - (ratio_soja_urea - ratio_hist_min) /
                             max(ratio_hist_max - ratio_hist_min, 0.01)))
        gauge = max(0, min(100, gauge))

        top5_cambios = (pd.DataFrame(zona_cambios)
                        .nlargest(5, 'delta_pct')
                        [['departamento', 'provincia', 'cultivo', 'dem_sim_tn', 'delta_pct']])

        # Base para comparación
        _, map_base = self.get_market_potential()
        base_total_tn = map_base['demanda_total_tn'].sum() * 0.85
        base_total_musd = map_base['valor_total_musd'].sum() * 0.85

        return {
            'total_dem_tn':      round(total_dem_tn),
            'total_valor_musd':  round(total_valor_musd, 1),
            'delta_dem_pct':     round((total_dem_tn - base_total_tn) / max(base_total_tn, 1) * 100, 1),
            'delta_val_pct':     round((total_valor_musd - base_total_musd) / max(base_total_musd, 1) * 100, 1),
            'ratios_sim_df':     ratios_sim_df,
            'gauge_compra':      gauge,
            'top5_cambios':      top5_cambios,
            'precio_grano':      precios_grano,
            'precio_fert':       precios_fert,
        }

    # ══════════════════════════════════════════════════════════
    # MÓDULO D — Correlación Clima-Producción
    # ══════════════════════════════════════════════════════════

    # Años ENSO conocidos — fuente: NOAA / IRI
    ENSO_YEARS = {
        'La Niña': [1988, 1999, 2000, 2008, 2011, 2012, 2022, 2023],
        'El Niño': [1983, 1987, 1992, 1998, 2003, 2010, 2016, 2024],
    }

    # Datos de correlación clima-producción precalculados
    # Fuente: análisis de series SIIA/MAGyP + normales climáticas SMN
    # Correlación precipitaciones Oct-Dic vs rendimiento soja (1991-2024)
    _CLIM_PROD_DATA = {
        'Soja': {
            'variable_clima': 'Precipitación Oct-Dic (mm)',
            'pearson_r': 0.61,
            'pendiente': 0.0052,  # tn/ha por mm adicional
            'intercepto': 1.85,
            'serie': [
                # (año, precip_oct_dic_mm, rend_tn_ha, enso)
                (2000, 285, 2.42, 'neutro'),(2001, 310, 2.61, 'neutro'),
                (2002, 195, 2.31, 'El Niño'),(2003, 320, 2.60, 'El Niño'),
                (2004, 290, 2.52, 'neutro'),(2005, 305, 2.64, 'neutro'),
                (2006, 215, 2.25, 'neutro'),(2007, 340, 2.75, 'neutro'),
                (2008, 355, 2.94, 'La Niña'),(2009, 280, 2.68, 'neutro'),
                (2010, 315, 2.74, 'El Niño'),(2011, 295, 2.84, 'La Niña'),
                (2012, 175, 2.43, 'La Niña'),(2013, 330, 2.84, 'neutro'),
                (2014, 310, 2.87, 'neutro'),(2015, 290, 2.85, 'neutro'),
                (2016, 155, 1.85, 'El Niño'),(2017, 345, 3.01, 'neutro'),
                (2018, 360, 3.10, 'neutro'),(2019, 370, 3.14, 'neutro'),
                (2020, 225, 2.92, 'neutro'),(2021, 380, 3.20, 'neutro'),
                (2022, 130, 1.65, 'La Niña'),(2023, 385, 3.30, 'neutro'),
                (2024, 360, 3.20, 'El Niño'),
            ],
        },
        'Maíz': {
            'variable_clima': 'Temperatura media Ene-Feb (°C)',
            'pearson_r': -0.54,
            'pendiente': -0.82,  # tn/ha por °C adicional (calor extremo = daño)
            'intercepto': 28.5,
            'serie': [
                (2000, 25.2, 6.12, 'neutro'),(2001, 24.8, 6.00, 'neutro'),
                (2002, 25.5, 5.80, 'El Niño'),(2003, 24.2, 6.40, 'El Niño'),
                (2004, 25.0, 6.10, 'neutro'),(2005, 25.8, 7.32, 'neutro'),
                (2006, 24.5, 7.55, 'neutro'),(2007, 24.1, 8.11, 'neutro'),
                (2008, 25.4, 7.78, 'La Niña'),(2009, 25.2, 7.61, 'neutro'),
                (2010, 25.9, 7.87, 'El Niño'),(2011, 27.1, 8.25, 'La Niña'),
                (2012, 27.8, 8.45, 'La Niña'),(2013, 25.0, 8.61, 'neutro'),
                (2014, 24.8, 7.92, 'neutro'),(2015, 26.2, 7.35, 'neutro'),
                (2016, 28.5, 5.72, 'El Niño'),(2017, 24.5, 8.73, 'neutro'),
                (2018, 24.2, 8.90, 'neutro'),(2019, 24.0, 9.10, 'neutro'),
                (2020, 25.5, 8.52, 'neutro'),(2021, 24.8, 9.25, 'neutro'),
                (2022, 28.2, 6.85, 'La Niña'),(2023, 24.1, 9.50, 'neutro'),
                (2024, 27.2, 9.30, 'El Niño'),
            ],
        },
        'Trigo': {
            'variable_clima': 'Precipitación May-Jul (mm)',
            'pearson_r': 0.48,
            'pendiente': 0.0038,
            'intercepto': 2.10,
            'serie': [
                (2000, 210, 2.41, 'neutro'),(2001, 225, 2.55, 'neutro'),
                (2002, 190, 2.35, 'El Niño'),(2003, 240, 2.62, 'El Niño'),
                (2004, 215, 2.70, 'neutro'),(2005, 195, 2.84, 'neutro'),
                (2006, 155, 2.12, 'neutro'),(2007, 250, 2.95, 'neutro'),
                (2008, 260, 2.78, 'La Niña'),(2009, 235, 3.01, 'neutro'),
                (2010, 220, 2.95, 'El Niño'),(2011, 230, 3.11, 'La Niña'),
                (2012, 175, 3.05, 'La Niña'),(2013, 245, 3.18, 'neutro'),
                (2014, 255, 3.35, 'neutro'),(2015, 215, 3.12, 'neutro'),
                (2016, 200, 2.75, 'El Niño'),(2017, 240, 3.00, 'neutro'),
                (2018, 250, 3.10, 'neutro'),(2019, 265, 3.25, 'neutro'),
                (2020, 235, 3.28, 'neutro'),(2021, 255, 3.20, 'neutro'),
                (2022, 145, 2.98, 'La Niña'),(2023, 270, 3.40, 'neutro'),
                (2024, 260, 3.30, 'El Niño'),
            ],
        },
    }

    # Estado ENSO actual (actualizar manualmente o conectar a NOAA en futuras versiones)
    ENSO_ACTUAL = {
        'estado': 'Neutro (tendencia El Niño débil)',
        'indice_oni': '+0.4',
        'probabilidad': {'Neutro': 45, 'El Niño': 35, 'La Niña': 20},
        'implicancia_soja': 'Condiciones normales a levemente favorables. Monitorear precipitaciones Oct-Dic.',
        'implicancia_maiz': 'Sin señal clara. Riesgo moderado de calor extremo en Ene-Feb.',
        'fuente': 'NOAA CPC — Marzo 2025',
    }

    def get_climate_production_correlation(self, cultivo='Soja'):
        """
        Retorna datos de correlación clima-producción con marcas ENSO.
        """
        data = self._CLIM_PROD_DATA.get(cultivo, self._CLIM_PROD_DATA['Soja'])
        df = pd.DataFrame(data['serie'], columns=['año', 'variable_clima', 'rendimiento', 'enso'])

        return {
            'df': df,
            'variable_clima': data['variable_clima'],
            'pearson_r': data['pearson_r'],
            'pendiente': data['pendiente'],
            'intercepto': data['intercepto'],
            'enso_actual': self.ENSO_ACTUAL,
        }

    # ══════════════════════════════════════════════════════════
    # MÓDULO E — Score de Prioridad Comercial (0-100)
    # ══════════════════════════════════════════════════════════
    def get_commercial_priority_score(self, cultivo='Soja'):
        """
        Score compuesto 0-100 por departamento.
        Pesos:
          Demanda potencial fertilizante:        25%
          Clasificación territorial:             20%
          Brecha tecnológica:                    20%
          Ratio insumo/grano (percentil):        15%
          Condición climática actual (NASA):     10%
          Tendencia producción últimos 5 años:   10%
        """
        # ── Componente 1: Demanda potencial ──────────────────
        _, map_df = self.get_market_potential(cultivo_filter=cultivo)
        if map_df.empty:
            _, map_df = self.get_market_potential()

        dem_df = map_df.groupby(['provincia', 'departamento', 'lat', 'lon'])[
            'demanda_total_tn'].sum().reset_index()
        dem_max = dem_df['demanda_total_tn'].max()
        dem_df['score_demanda'] = (dem_df['demanda_total_tn'] / max(dem_max, 1) * 100).round(1)

        # ── Componente 2: Clasificación territorial ───────────
        clasi_df, _, _ = self.get_territorial_classification(cultivo=cultivo, periodo_anios=10)
        clasi_map = {'EXPANSIÓN': 100, 'MADUREZ': 50, 'CONTRACCIÓN': 10, 'EMERGENTE': 80}
        if not clasi_df.empty:
            clasi_df['score_territorial'] = clasi_df['clasificacion'].map(clasi_map).fillna(50)
            clasi_df = clasi_df[['provincia', 'departamento', 'score_territorial', 'clasificacion',
                                  'cagr_pct', 'proj_2026', 'r2']]

        # ── Componente 3: Brecha tecnológica ─────────────────
        brecha_df = self.get_technology_gap(cultivo=cultivo)
        brecha_df['score_brecha'] = (brecha_df['brecha_pct']).clip(0, 100)

        # ── Componente 4: Ratio insumo/grano (percentil inverso) ─
        # Fertilizante clave por cultivo
        fert_key = {'Maíz': 'Urea', 'Trigo': 'Urea', 'Soja': 'MAP', 'Girasol': 'Urea'}.get(cultivo, 'Urea')
        _, ratio_actual, percentil = self.get_price_history(cultivo, fert_key)
        score_ratio = max(0, 100 - percentil)  # bajo percentil = barato = buena oportunidad

        # ── Componente 5: Clima (simplificado: 70 base ENSO neutro) ─
        score_clima_base = 70  # ajustar por ENSO actual
        if 'La Niña' in self.ENSO_ACTUAL['estado']:
            score_clima_base = 40
        elif 'El Niño' in self.ENSO_ACTUAL['estado']:
            score_clima_base = 60

        # ── Componente 6: Tendencia producción ──────────────
        df_siia = self._load_rend()
        rend_sub = df_siia[(df_siia['cultivo'] == cultivo) & (df_siia['año'] >= 2019)]
        tend_df = rend_sub.groupby(['provincia', 'departamento'])['rendimiento_tn_ha'].apply(
            lambda s: np.polyfit(range(len(s)), s, 1)[0] if len(s) >= 3 else 0
        ).reset_index()
        tend_df.columns = ['provincia', 'departamento', 'tendencia_rend']
        tend_max = tend_df['tendencia_rend'].abs().max()
        tend_df['score_tendencia'] = (
            (tend_df['tendencia_rend'] / max(tend_max, 0.01) + 1) / 2 * 100
        ).clip(0, 100).round(1)

        # ── Merge todo ────────────────────────────────────────
        result = dem_df.copy()
        if not clasi_df.empty:
            result = result.merge(clasi_df, on=['provincia', 'departamento'], how='left')
        else:
            result['score_territorial'] = 50
            result['clasificacion'] = 'MADUREZ'
            result['cagr_pct'] = 0
            result['proj_2026'] = 0
            result['r2'] = 0

        brecha_merge = brecha_df[['provincia', 'departamento', 'score_brecha',
                                   'brecha_pct', 'rend_real_avg', 'rend_potencial',
                                   'valor_oportunidad_usd_m', 'zona_agroclimatica']]
        result = result.merge(brecha_merge, on=['provincia', 'departamento'], how='left')
        result = result.merge(tend_df, on=['provincia', 'departamento'], how='left')

        result['score_territorial'] = result['score_territorial'].fillna(50)
        result['score_brecha']      = result['score_brecha'].fillna(30)
        result['score_tendencia']   = result['score_tendencia'].fillna(50)

        # Score compuesto
        result['score_ratio']  = score_ratio
        result['score_clima']  = score_clima_base
        result['score_final']  = (
            result['score_demanda']    * 0.25 +
            result['score_territorial']* 0.20 +
            result['score_brecha']     * 0.20 +
            result['score_ratio']      * 0.15 +
            result['score_clima']      * 0.10 +
            result['score_tendencia']  * 0.10
        ).round(1)

        result = result.sort_values('score_final', ascending=False).reset_index(drop=True)
        result['rank'] = result.index + 1

        # Argumento de venta automático
        # Capturar valores de closure explícitamente via default args
        def gen_argumento(row, _sr=score_ratio, _pct=percentil):
            cls = row.get('clasificacion', 'MADUREZ')
            brecha = row.get('brecha_pct', 0)
            dem = row.get('demanda_total_tn', 0)
            score = row.get('score_final', 0)
            proj = row.get('proj_2026', 0)
            momento = 'favorable' if _sr > 60 else ('neutro' if _sr > 40 else 'cuidadoso')

            return (
                f"{row['departamento']} ({row['provincia']}) — Score {score:.0f}/100. "
                f"Zona en {cls}. "
                f"Brecha tecnológica {brecha:.0f}% vs potencial INTA — "
                f"representa oportunidad de {dem/1000:.0f}K tn de fertilizante. "
                f"Proyección 2026: {proj:,} ha. "
                f"Momento de mercado: {momento} (ratio percentil {_pct}°)."
            )

        result['argumento_venta'] = result.apply(gen_argumento, axis=1)

        return result, {
            'score_ratio': score_ratio,
            'percentil_ratio': percentil,
            'fert_key': fert_key,
            'score_clima': score_clima_base,
            'enso': self.ENSO_ACTUAL['estado'],
        }
