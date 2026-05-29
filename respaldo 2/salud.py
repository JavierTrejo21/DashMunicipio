import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc

def cargar_datos():
    conn = sqlite3.connect('municipio.db')
    df = pd.read_sql_query("SELECT * FROM enlace_salud", conn)
    conn.close()
    
    # 1. Limpieza total de nombres de columnas a Mayúsculas
    df.columns = [c.strip().upper() for c in df.columns]
    
    # 2. Asegurar que las columnas existan para evitar errores
    if 'MES' not in df.columns: df['MES'] = 'SIN DATO'
    if 'ACTIVIDAD' not in df.columns: df['ACTIVIDAD'] = 'SIN ACTIVIDAD'
    if 'BENEFICIARIOS' not in df.columns: df['BENEFICIARIOS'] = 0

    # 3. Limpieza de datos de texto
    for col in ['MES', 'ACTIVIDAD']:
        df[col] = df[col].astype(str).str.upper().str.strip().replace(['NAN', 'NONE', ''], 'SIN DATO')
    
    # 4. Mapeo de Trimestres
    mapa_trimestres = {
        'ENERO': '1er Trimestre', 'FEBRERO': '1er Trimestre', 'MARZO': '1er Trimestre',
        'ABRIL': '2do Trimestre', 'MAYO': '2do Trimestre', 'JUNIO': '2do Trimestre',
        'JULIO': '3er Trimestre', 'AGOSTO': '3er Trimestre', 'SEPTIEMBRE': '3er Trimestre',
        'OCTUBRE': '4to Trimestre', 'NOVIEMBRE': '4to Trimestre', 'DICIEMBRE': '4to Trimestre'
    }
    df['TRIMESTRE'] = df['MES'].map(mapa_trimestres).fillna('Sin Clasificar')
    
    # 5. Beneficiarios a número
    df['CANT_BENEFICIARIOS'] = pd.to_numeric(df['BENEFICIARIOS'], errors='coerce').fillna(0)
    
    return df

def layout_salud():
    try:
        df = cargar_datos()
        # Opciones para dropdowns
        opt_mes = [{'label': m, 'value': m} for m in sorted(df['MES'].unique())]
        opt_act = [{'label': a, 'value': a} for a in sorted(df['ACTIVIDAD'].unique())]
    except Exception as e:
        return dbc.Alert(f"Error al cargar Salud: {e}", color="danger")
    
    return html.Div([
        html.H2("2.3 ENLACE DE SALUD - INFORME DE ACTIVIDADES", 
                style={'color': '#1a5276', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Hr(style={'borderTop': '3px solid #bc955c'}),

        # --- FILTROS ---
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("⏱️ Trimestre:", className="fw-bold"),
                        dcc.Dropdown(
                            id='f-trim-salud', 
                            options=[{'label': t, 'value': t} for t in ['1er Trimestre', '2do Trimestre', '3er Trimestre', '4to Trimestre']],
                            multi=True, placeholder="Filtrar por Trimestre"
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("📆 Mes:", className="fw-bold"),
                        dcc.Dropdown(id='f-mes-salud', options=opt_mes, multi=True, placeholder="Filtrar por Mes")
                    ], md=4),
                    dbc.Col([
                        html.Label("🏥 Actividad:", className="fw-bold"),
                        dcc.Dropdown(id='f-act-salud', options=opt_act, multi=True, placeholder="Filtrar por Actividad")
                    ], md=4),
                ])
            ])
        ], className="mb-4 shadow-sm"),

        # --- TARJETAS (KPIs) ---
        dbc.Row([
            dbc.Col(id='kpi-sal-ben', md=6),
            dbc.Col(id='kpi-sal-acc', md=6),
        ], className="mb-4"),

        # --- TABLA DE INFORME ---
        dbc.Card([
            dbc.CardHeader("DETALLE DE ACCIONES DE SALUD", className="bg-primary text-white fw-bold"),
            dbc.CardBody([
                html.Div(id='table-salud-container')
            ])
        ], className="shadow-sm")
    ], className="p-4")

@callback(
    [Output('kpi-sal-ben', 'children'), Output('kpi-sal-acc', 'children'),
     Output('table-salud-container', 'children')],
    [Input('f-trim-salud', 'value'), Input('f-mes-salud', 'value'), Input('f-act-salud', 'value')]
)
def actualizar_salud(trim, mes, act):
    df = cargar_datos()

    # Aplicar filtros
    if trim: df = df[df['TRIMESTRE'].isin(trim)]
    if mes:  df = df[df['MES'].isin(mes)]
    if act:  df = df[df['ACTIVIDAD'].isin(act)]

    # Cálculo para Tarjetas
    total_ben = int(df['CANT_BENEFICIARIOS'].sum())
    total_act = len(df)
    
    card_ben = dbc.Card(dbc.CardBody([
        html.H6("Total de Beneficiarios Atendidos", className="text-muted"),
        html.H2(f"{total_ben:,}", style={'color': '#1a5276', 'fontWeight': 'bold'})
    ]), color="light", style={'borderLeft': '10px solid #1a5276'})
    
    card_act = dbc.Card(dbc.CardBody([
        html.H6("Número de Actividades / Jornadas", className="text-muted"),
        html.H2(f"{total_act}", style={'color': '#bc955c', 'fontWeight': 'bold'})
    ]), color="light", style={'borderLeft': '10px solid #bc955c'})

    # Preparar tabla (seleccionamos las columnas clave del CSV)
    # Usamos nombres exactos basados en el CSV proporcionado
    columnas_tabla = ['MES', 'ACTIVIDAD', 'FECHA', 'BENEFICIARIOS']
    
    tabla = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in columnas_tabla],
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_header={'backgroundColor': '#f8f9fa', 'color': '#1a5276', 'fontWeight': 'bold', 'border': '1px solid #dee2e6'},
        style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'sans-serif', 'fontSize': '14px'},
        style_table={'overflowX': 'auto'},
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f2f2f2'
        }]
    )

    return card_ben, card_act, tabla
