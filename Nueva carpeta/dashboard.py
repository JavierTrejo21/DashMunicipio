import pandas as pd
import sqlite3
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px
from dash.dash_table.Format import Format, Scheme, Symbol

# 1. FUNCIÓN DE CARGA Y LIMPIEZA CON CORRECCIÓN DE COLUMNAS
def cargar_datos():
    # Conexión a la base de datos de obras
    conn = sqlite3.connect('municipio.db')
    try:
        df = pd.read_sql_query("SELECT * FROM proyectos", conn)
    except Exception as e:
        print(f"Error al leer la tabla 'proyectos': {e}")
        return pd.DataFrame()
    finally:
        conn.close()

    # MAPEO FLEXIBLE: Evita el KeyError buscando palabras clave en los nombres de las columnas
    for col in df.columns:
        col_lower = col.lower()
        if 'ubicacion' in col_lower:
            df = df.rename(columns={col: 'ubicacion'})
        elif 'monto' in col_lower:
            df = df.rename(columns={col: 'monto_total'})
        elif 'estatus' in col_lower:
            df = df.rename(columns={col: 'estatus_obra'})
        elif 'beneficiarios' in col_lower:
            df = df.rename(columns={col: 'beneficiarios'})
        elif 'avance' in col_lower:
            df = df.rename(columns={col: 'avance'})
        elif 'nombre' in col_lower and 'proyecto' in col_lower:
            df = df.rename(columns={col: 'nombre_proyecto'})

    # Limpieza numérica de moneda, comas y porcentajes
    for col in ['monto_total', 'beneficiarios', 'avance']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '', regex=False)\
                             .str.replace(',', '', regex=False)\
                             .str.replace('%', '', regex=False)\
                             .str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Rellenar valores vacíos para evitar errores en gráficas
    if 'estatus_obra' in df.columns:
        df['estatus_obra'] = df['estatus_obra'].replace(['', 'None', 'nan'], 'SIN ESTATUS')
    
    df = df.fillna('SIN ESPECIFICAR')
    return df

# Carga inicial de datos
df_inicial = cargar_datos()

app = Dash(__name__)

# 2. DISEÑO DE LA INTERFAZ (LAYOUT)
app.layout = html.Div(style={'padding': '40px', 'backgroundColor': '#f2f5f8', 'fontFamily': 'Arial, sans-serif'}, children=[
    
    # Encabezado Institucional
    html.Div([
        html.H1("SISTEMA ESTRATÉGICO DE GESTIÓN MUNICIPAL", style={'color': '#691c32', 'margin': '0', 'fontWeight': 'bold'}),
        html.H4("Monitoreo de Obra Pública - Informe 2026", style={'color': '#bc955c', 'marginTop': '5px'}),
    ], style={'textAlign': 'center', 'borderBottom': '4px solid #bc955c', 'paddingBottom': '20px', 'marginBottom': '30px'}),

    # PANEL DE FILTROS
    html.Div([
        html.Div([
            html.Label("📍 Filtro por Ubicación:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='dropdown-ubicacion',
                options=[{'label': i, 'value': i} for i in sorted(df_inicial['ubicacion'].unique())] if 'ubicacion' in df_inicial.columns else [],
                multi=True, placeholder="Todas las ubicaciones..."
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("📊 Filtro por Estatus:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='dropdown-estatus',
                options=[{'label': i, 'value': i} for i in sorted(df_inicial['estatus_obra'].unique())] if 'estatus_obra' in df_inicial.columns else [],
                multi=True, placeholder="Todos los estatus..."
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px', 'marginBottom': '30px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}),

    # TARJETAS DE INDICADORES
    html.Div(id='contenedor-indicadores', style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),

    # BLOQUE DE GRÁFICAS
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}, children=[
        html.Div([dcc.Graph(id='grafico-estatus-recurso')], style={'width': '50%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px'}),
        html.Div([dcc.Graph(id='grafico-top-localidades')], style={'width': '50%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px'}),
    ]),

    # TABLA DE DATOS
    html.Div([
        html.H3("Cédula de Información de Obra Pública", style={'color': '#691c32', 'paddingLeft': '10px'}),
        dash_table.DataTable(
            id='tabla-proyectos',
            columns=[
                {"name": i.upper().replace('_', ' '), "id": i, "type": "numeric", 
                 "format": Format(symbol=Symbol.yes, symbol_prefix='$', group=',', scheme=Scheme.fixed, precision=2)} if i == 'monto_total' else 
                {"name": i.upper().replace('_', ' '), "id": i} for i in df_inicial.columns
            ],
            page_size=10,
            style_header={'backgroundColor': '#691c32', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_data_conditional=[
                {'if': {'column_id': 'avance', 'filter_query': '{avance} < 30'}, 'backgroundColor': '#ffcccc', 'color': '#cc0000'},
                {'if': {'column_id': 'avance', 'filter_query': '{avance} >= 80'}, 'backgroundColor': '#d4edda', 'color': '#155724'},
            ]
        )
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px'})
])

# 3. CALLBACK DE INTERACTIVIDAD
@app.callback(
    [Output('contenedor-indicadores', 'children'),
     Output('grafico-estatus-recurso', 'figure'),
     Output('grafico-top-localidades', 'figure'),
     Output('tabla-proyectos', 'data')],
    [Input('dropdown-ubicacion', 'value'),
     Input('dropdown-estatus', 'value')]
)
def filtrar_dashboard(ub_sel, es_sel):
    df = cargar_datos()
    pob_max = 22903
    
    if ub_sel: df = df[df['ubicacion'].isin(ub_sel)]
    if es_sel: df = df[df['estatus_obra'].isin(es_sel)]

    # Indicadores
    presupuesto = df['monto_total'].sum()
    total_obras = len(df)
    avance_medio = df['avance'].mean()
    suma_ben = int(df['beneficiarios'].sum())
    display_ben = f"{min(suma_ben, pob_max):,}"

    indicadores = [
        html.Div([html.P("Inversión Social"), html.H2(f"${presupuesto:,.2f}", style={'color': '#28a745'})], 
                 style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center'}),
        html.Div([html.P("Beneficiarios"), html.H2(display_ben, style={'color': '#691c32'})], 
                 style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center'}),
        html.Div([html.P("Total Obras"), html.H2(total_obras)], 
                 style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center'}),
        html.Div([html.P("Avance Medio"), html.H2(f"{avance_medio:.1f}%")], 
                 style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center'}),
    ]

    # Gráficas
    fig_estatus = px.bar(df.groupby('estatus_obra')['monto_total'].sum().reset_index(), 
                         x="estatus_obra", y="monto_total", title="Recurso por Estatus", template="plotly_white")
    
    df_top_loc = df.groupby('ubicacion')['monto_total'].sum().nlargest(10).reset_index()
    fig_top_loc = px.bar(df_top_loc, y="ubicacion", x="monto_total", orientation='h', 
                         title="Top 10 Localidades", color_discrete_sequence=['#bc955c'], template="plotly_white")

    return indicadores, fig_estatus, fig_top_loc, df.to_dict('records')

if __name__ == '__main__':
    # Puerto diferente para no chocar con el dashboard principal si ambos corren a la vez
    app.run(debug=True, port=8051)
