import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

def renderizar_pueblos_indigenas(df):
    """Dashboard especializado para Pueblos Indígenas con detección de columnas"""
    
    if df is None or df.empty:
        return html.Div("No hay datos disponibles para esta área.", className="p-5 text-center text-muted")

    # --- 1. DETECCIÓN DINÁMICA DE COLUMNAS ---
    def buscar_col(keywords):
        for col in df.columns:
            if any(k in col.upper() for k in keywords):
                return col
        return None

    c_inv = buscar_col(['INVERSION', 'MONTO', 'COSTO', 'EJERCIDO'])
    c_ben = buscar_col(['BENEFICIARIO', 'PERSONA', 'POBLACION', 'ATENDIDOS'])
    c_prog = buscar_col(['PROGRAMA', 'ACTIVIDAD', 'CONCEPTO', 'NOMBRE'])
    c_com = buscar_col(['COMUNIDAD', 'LOCALIDAD', 'BARRIO'])
    c_mes = buscar_col(['MES', 'FECHA'])
    c_lengua = buscar_col(['LENGUA', 'MATERNA', 'INDIGENA'])

    # --- 2. LIMPIEZA DE DATOS ---
    dff = df.copy()
    if c_inv: dff[c_inv] = pd.to_numeric(dff[c_inv], errors='coerce').fillna(0)
    if c_ben: dff[c_ben] = pd.to_numeric(dff[c_ben], errors='coerce').fillna(0)

    # Filtrar filas sin actividad significativa
    dff = dff[(dff[c_ben] > 0) | (dff[c_inv] > 0 if c_inv else False)]

    # --- 3. CÁLCULO DE KPIs ---
    total_inv = dff[c_inv].sum() if c_inv else 0
    total_ben = dff[c_ben].sum() if c_ben else 0
    num_com = dff[c_com].nunique() if c_com else 0
    
    alcance_pct = 0
    if c_lengua and total_ben > 0:
        ben_ind = dff[dff[c_lengua].astype(str).str.upper().str.contains('SI', na=False)][c_ben].sum()
        alcance_pct = (ben_ind / total_ben) * 100

    # --- 4. GRÁFICOS ---
    # Gráfico de Barras: Inversión por Programa
    fig_prog = go.Figure()
    if c_inv and c_prog:
        df_p = dff.groupby(c_prog)[c_inv].sum().reset_index().sort_values(c_inv)
        fig_prog = px.bar(df_p, x=c_inv, y=c_prog, orientation='h', 
                          color_discrete_sequence=['#10b981'], template="plotly_white")
        fig_prog.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)

    # Gráfico de Área: Tendencia Mensual
    fig_area = go.Figure()
    if c_inv and c_mes:
        meses_ord = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        dff[c_mes] = pd.Categorical(dff[c_mes].str.upper(), categories=meses_ord, ordered=True)
        df_m = dff.groupby(c_mes)[c_inv].sum().reset_index()
        fig_area = px.area(df_m, x=c_mes, y=c_inv, color_discrete_sequence=['#6366f1'], template="plotly_white")
        fig_area.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)

    # --- 5. DISEÑO DEL TABLERO ---
    return html.Div([
        # Fila de Tarjetas (KPIs)
        dbc.Row([
            dbc.Col(kpi_card("INVERSIÓN TOTAL", f"${total_inv:,.2f}", "success"), width=3),
            dbc.Col(kpi_card("BENEFICIARIOS", f"{int(total_ben):,}", "primary"), width=3),
            dbc.Col(kpi_card("ALCANCE INDÍGENA", f"{alcance_pct:.1f}%", "info"), width=3),
            dbc.Col(kpi_card("LOCALIDADES", f"{num_com}", "warning"), width=3),
        ], className="mb-4 g-2"),

        # Fila de Gráficos
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.B("DISTRIBUCIÓN POR PROGRAMA")),
                dbc.CardBody(dcc.Graph(figure=fig_prog, config={'displayModeBar': False}))
            ]), width=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.B("TENDENCIA DE GASTO")),
                dbc.CardBody(dcc.Graph(figure=fig_area, config={'displayModeBar': False}))
            ]), width=6),
        ]),
    ], className="animate__animated animate__fadeIn")

def kpi_card(titulo, valor, color):
    """Crea tarjetas de indicadores con colores institucionales"""
    colores = {"success": "#10b981", "primary": "#6366f1", "info": "#06b6d4", "warning": "#f59e0b"}
    return dbc.Card([
        dbc.CardBody([
            html.Small(titulo, className="text-white-50 fw-bold"),
            html.H3(valor, className="text-white mb-0 fw-bold")
        ])
    ], style={"backgroundColor": colores.get(color, "#333"), "border": "none"}, className="shadow-sm")
