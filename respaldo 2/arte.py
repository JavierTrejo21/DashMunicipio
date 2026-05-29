import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc

def cargar_datos():
    try:
        conn = sqlite3.connect('municipio.db')
        df = pd.read_sql_query("SELECT * FROM arte_cultura", conn)
        conn.close()
        
        # 1. Limpieza de nombres de columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 2. LIMPIEZA DE MES: Forzar a texto y eliminar filas vacías
        # Esto elimina el error de comparación entre números (NaN) y letras
        df['MES'] = df['MES'].astype(str).str.strip().str.upper()
        df = df[~df['MES'].isin(['NAN', 'NONE', '', '0', 'S/D', 'S/C'])]

        # 3. CONVERSIÓN NUMÉRICA: Inversión y Beneficiarios
        # Al tener una sola columna, es más directo
        df['I_TOTAL'] = pd.to_numeric(df.get('INVERSION', 0), errors='coerce').fillna(0)
        
        # Sumamos beneficiarios si existen las columnas, si no, ponemos 0
        fem = pd.to_numeric(df.get('FEMENINOS', 0), errors='coerce').fillna(0)
        mas = pd.to_numeric(df.get('MASCULINOS', 0), errors='coerce').fillna(0)
        df['B_TOTAL'] = fem + mas
        
        # 4. MAPEO DE TRIMESTRES
        mapa_trim = {
            'ENERO': '1er Trim', 'FEBRERO': '1er Trim', 'MARZO': '1er Trim',
            'ABRIL': '2do Trim', 'MAYO': '2do Trim', 'JUNIO': '2do Trim',
            'JULIO': '3er Trim', 'AGOSTO': '3er Trim', 'SEPTIEMBRE': '3er Trim',
            'OCTUBRE': '4to Trim', 'NOVIEMBRE': '4to Trim', 'DICIEMBRE': '4to Trim'
        }
        df['TRIMESTRE'] = df['MES'].map(mapa_trim).fillna('S/C')
        
        return df
    except Exception as e:
        print(f"Error en cargar_datos: {e}")
        return None

def layout_arte():
    df = cargar_datos()
    if df is None or df.empty:
        return dbc.Alert("No hay datos disponibles. Revisa el CSV y ejecuta cargar_arte.py", color="danger")
    
    # Lista de meses limpia para el filtro
    meses_lista = sorted(df['MES'].unique().tolist())
    
    return html.Div([
        html.H2("3.4 ARTE Y CULTURA", style={'color': '#691c32', 'textAlign': 'center', 'fontWeight': 'bold'}),
        html.Hr(style={'borderTop': '3px solid #bc955c'}),
        
        dbc.Row([
            dbc.Col([
                html.Label("📅 Mes:", className="fw-bold"),
                dcc.Dropdown(id='sel-mes-a', options=[{'label': m, 'value': m} for m in meses_lista], multi=True)
            ], md=6),
            dbc.Col([
                html.Label("⏱️ Trimestre:", className="fw-bold"),
                dcc.Dropdown(id='sel-trim-a', options=[{'label': t, 'value': t} for t in ['1er Trim', '2do Trim', '3er Trim', '4to Trim']], multi=True)
            ], md=6),
        ], className="mb-4"),

        # TARJETAS
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Inversión Total"),
                html.H2(id='ind-inv', style={'color': '#691c32', 'fontWeight': 'bold'})
            ]), color="light", style={'borderLeft': '10px solid #691c32'}), md=4),
            
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Actividades"),
                html.H2(id='ind-act', style={'color': '#bc955c', 'fontWeight': 'bold'})
            ]), color="light", style={'borderLeft': '10px solid #bc955c'}), md=4),
            
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Beneficiarios"),
                html.H2(id='ind-ben', style={'color': '#1a5276', 'fontWeight': 'bold'})
            ]), color="light", style={'borderLeft': '10px solid #1a5276'}), md=4),
        ], className="mb-4"),

        dbc.Card([
            dbc.CardHeader("DETALLE DE ACCIONES", className="bg-dark text-white fw-bold"),
            dbc.CardBody(id='tabla-final-arte')
        ], className="shadow-sm")
    ], className="p-4")

@callback(
    [Output('ind-inv', 'children'), Output('ind-act', 'children'), 
     Output('ind-ben', 'children'), Output('tabla-final-arte', 'children')],
    [Input('sel-mes-a', 'value'), Input('sel-trim-a', 'value')]
)
def update_dashboard(mes, trim):
    df = cargar_datos()
    if df is None: return "$0.00", "0", "0", "Error"
    
    dff = df.copy()
    if mes: dff = dff[dff['MES'].isin(mes)]
    if trim: dff = dff[dff['TRIMESTRE'].isin(trim)]
    
    # Resultados
    val_inv = f"${dff['I_TOTAL'].sum():,.2f}"
    val_act = str(len(dff))
    val_ben = f"{int(dff['B_TOTAL'].sum()):,}"
    
    # Tabla
    cols = [{"name": i, "id": i} for i in ['MES', 'EVENTO', 'UBICACION'] if i in dff.columns]
    
    tabla = dash_table.DataTable(
        data=dff.to_dict('records'),
        columns=cols,
        page_size=10,
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
    )
    
    return val_inv, val_act, val_ben, tabla
