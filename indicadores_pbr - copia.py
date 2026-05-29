import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

def calcular_indicadores_pbr(df):
    if df is None or df.empty:
        return [dbc.Col(dbc.Card(dbc.CardBody("Esperando datos..."), className="text-center"))]

    # Columnas según tu archivo
    col_inv = 'Inversión'
    col_ben = 'Beneficiarios'
    col_com = 'Comunidad'

    # 1. Cálculo de Inversión Total
    if col_inv in df.columns:
        inv_limpia = pd.to_numeric(df[col_inv].astype(str).replace(r'[\$,]', '', regex=True), errors='coerce').fillna(0)
        total_inv = inv_limpia.sum()
    else:
        total_inv = 0

    # 2. Total de Beneficiarios (Impacto Social)
    if col_ben in df.columns:
        ben_limpios = pd.to_numeric(df[col_ben], errors='coerce').fillna(0)
        total_ben = ben_limpios.sum()
    else:
        total_ben = 0

    # 3. Comunidades Atendidas (Relevancia Política: Cobertura Territorial)
    if col_com in df.columns:
        total_comunidades = df[col_com].nunique() # Cuenta cuántas comunidades únicas hay
    else:
        total_comunidades = 0

    return [
        # Tarjeta de Inversión
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("PRESUPUESTO EJERCIDO", className="text-muted small"),
                html.H2(f"${total_inv:,.2f}", className="text-danger font-weight-bold")
            ])
        ], className="shadow-sm border-start border-danger border-4"), md=4),
        
        # Tarjeta de Beneficiarios
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("POBLACIÓN BENEFICIADA", className="text-muted small"),
                html.H2(f"{int(total_ben):,}", className="text-primary font-weight-bold")
            ])
        ], className="shadow-sm border-start border-primary border-4"), md=4),

        # Tarjeta de Cobertura Territorial (Nueva - Relevancia Política)
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("COBERTURA TERRITORIAL", className="text-muted small"),
                html.H2(f"{total_comunidades} Localidades", className="text-warning font-weight-bold")
            ])
        ], className="shadow-sm border-start border-warning border-4"), md=4),
    ]
