import pandas as pd
import sqlite3
from dash import Dash, html, dcc, dash_table, Input, Output, ctx
import plotly.express as px
from dash.dash_table.Format import Format, Scheme, Symbol

# 1. FUNCIÓN DE CARGA Y LIMPIEZA REFORZADA
def cargar_datos():
    conn = sqlite3.connect('municipio.db')
    df = pd.read_sql_query("SELECT * FROM proyectos", conn)
    conn.close()

    # Mapeo de columnas largas a cortas (Basado en tu DB)
    mapeo = {
        'nombre_del_proyecto': 'nombre_proyecto',
        'tipo_de_obra_(infraestructura_vial,_hidraulica,_educativa,_etc.).': 'tipo_obra',
        'ubicacion_(colonia,_comunidad_o_localidad).': 'ubicacion',
        'monto_total_invertido': 'monto_total',
        'numero_de_beneficiarios': 'beneficiarios',
        'estatus_de_obra': 'estatus_obra'
    }
    df = df.rename(columns=mapeo)

    # Limpieza numérica profunda (Eliminar $, comas y % para cálculos)
    for col in ['monto_total', 'beneficiarios', 'avance']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '', regex=False)\
                             .str.replace(',', '', regex=False)\
                             .str.replace('%', '', regex=False)\
                             .str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Asegurar que ESTATUS no esté vacío para las gráficas
    if 'estatus_obra' in df.columns:
        df['estatus_obra'] = df['estatus_obra'].replace(['', 'None', 'nan'], 'SIN ESTATUS')
    
    # Rellenar textos vacíos
    df = df.fillna('SIN ESPECIFICAR')
    return df

df_inicial = cargar_datos()

app = Dash(__name__)

# 2. DISEÑO DE LA INTERFAZ (LAYOUT)
app.layout = html.Div(style={'padding': '40px', 'backgroundColor': '#f2f5f8', 'fontFamily': 'Arial, sans-serif'}, children=[
    
    # Encabezado Institucional
    html.Div([
        html.H1("SISTEMA ESTRATÉGICO DE GESTIÓN MUNICIPAL", style={'color': '#691c32', 'margin': '0', 'fontWeight': 'bold'}),
        html.H4("Monitoreo de Obra Pública y Alineación PBR - Informe 2026", style={'color': '#bc955c', 'marginTop': '5px'}),
    ], style={'textAlign': 'center', 'borderBottom': '4px solid #bc955c', 'paddingBottom': '20px', 'marginBottom': '30px'}),

    # PANEL DE FILTROS (2 filtros para mayor amplitud)
    html.Div([
        html.Div([
            html.Label("📍 Filtro por Ubicación (Comunidad/Colonia):", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='dropdown-ubicacion',
                options=[{'label': i, 'value': i} for i in sorted(df_inicial['ubicacion'].unique())],
                multi=True, placeholder="Todas las ubicaciones..."
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("📊 Filtro por Estatus de Obra:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='dropdown-estatus',
                options=[{'label': i, 'value': i} for i in sorted(df_inicial['estatus_obra'].unique())],
                multi=True, placeholder="Todos los estatus..."
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px', 'marginBottom': '30px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}),

    # BOTÓN DE DESCARGA
    html.Div([
        html.Button("📥 Descargar Reporte Excel", id="btn-excel", n_clicks=0, 
                    style={'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
        dcc.Download(id="download-dataframe-excel"),
    ], style={'textAlign': 'right', 'marginBottom': '20px'}),

    # TARJETAS DE INDICADORES (Actualizadas vía Callback)
    html.Div(id='contenedor-indicadores', style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),

    # BLOQUE DE GRÁFICAS (Estatus y Top 10 Localidades)
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}, children=[
        html.Div([
            dcc.Graph(id='grafico-estatus-recurso')
        ], style={'width': '50%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}),
        
        html.Div([
            dcc.Graph(id='grafico-top-localidades')
        ], style={'width': '50%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}),
    ]),

    # TABLA DE DATOS DETALLADA (Con semáforo y formato de moneda)
    html.Div([
        html.H3("Cédula de Información de Obra Pública", style={'color': '#691c32', 'paddingLeft': '10px'}),
        dash_table.DataTable(
            id='tabla-proyectos',
            # Definimos las columnas y aplicamos formato de moneda a 'MONTO TOTAL'
            columns=[
                {"name": i.upper().replace('_', ' '), "id": i, "type": "numeric", "format": Format(symbol=Symbol.yes, symbol_prefix='$', group=',', scheme=Scheme.fixed, precision=2)} if i == 'monto_total' else 
                {"name": i.upper().replace('_', ' '), "id": i} for i in df_inicial.columns
            ],
            sort_action="native",
            filter_action="native",
            page_size=10,
            style_header={'backgroundColor': '#691c32', 'color': 'white', 'fontWeight': 'bold', 'textAlign': 'center'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '12px'},
            style_table={'overflowX': 'auto', 'borderRadius': '10px'},
            # --- MEJORA: SEMÁFORO DE AVANCE ---
            style_data_conditional=[
                {
                    'if': {
                        'column_id': 'avance',
                        'filter_query': '{avance} < 30'
                    },
                    'backgroundColor': '#ffcccc', # Rojo suave
                    'color': '#cc0000',
                    'fontWeight': 'bold'
                },
                {
                    'if': {
                        'column_id': 'avance',
                        'filter_query': '{avance} >= 30 && {avance} < 80'
                    },
                    'backgroundColor': '#fff3cd', # Amarillo suave
                    'color': '#856404',
                    'fontWeight': 'bold'
                },
                {
                    'if': {
                        'column_id': 'avance',
                        'filter_query': '{avance} >= 80'
                    },
                    'backgroundColor': '#d4edda', # Verde suave
                    'color': '#155724',
                    'fontWeight': 'bold'
                },
            ]
        )
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}),
])

# 3. CALLBACKS (INTERACTIVIDAD)

# Callback 1: Actualizar Dashboard (Tarjetas, Gráficas y Tabla)
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
    
    # Filtrado combinando ambos filtros
    if ub_sel: df = df[df['ubicacion'].isin(ub_sel)]
    if es_sel: df = df[df['estatus_obra'].isin(es_sel)]

    # Cálculo de métricas filtradas
    presupuesto = df['monto_total'].sum()
    total_obras = len(df)
    avance_medio = df['avance'].mean()
    
    # Lógica de Beneficiarios con TOPE municipal
    suma_ben = int(df['beneficiarios'].sum())
    display_ben = f"{min(suma_ben, pob_max):,}"
    sub_ben = "Cobertura Total Municipal" if suma_ben >= pob_max else "Habitantes impactados"

    indicadores = [
        html.Div([html.P("Inversión Social"), html.H2(f"${presupuesto:,.2f}", style={'color': '#28a745'})], 
                 style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center'}),
        
        html.Div([
            html.P("Beneficiarios Únicos"), 
            html.H2(display_ben, style={'color': '#691c32'}),
            html.Small(sub_ben, style={'color': '#7f8c8d'})
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center', 'border': '1px solid #bc955c'}),
        
        html.Div([html.P("Total Obras"), html.H2(total_obras)], 
                 style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center'}),
        
        html.Div([html.P("Avance Físico Promedio"), html.H2(f"{avance_medio:.1f}%")], 
                 style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'width': '23%', 'textAlign': 'center'}),
    ]

    # Gráfico 1: Barras por Estatus
    fig_estatus = px.bar(
        df.groupby('estatus_obra')['monto_total'].sum().reset_index(), 
        x="estatus_obra", y="monto_total", text_auto='.2s', color="estatus_obra",
        template="plotly_white", title="Recurso por Estatus de Obra",
        labels={'estatus_obra': 'Estatus de Obra', 'monto_total': 'Presupuesto ($)'}
    )
    fig_estatus.update_layout(showlegend=False)

    # --- MEJORA: GRÁFICO TOP 10 LOCALIDADES ---
    # Agrupamos por ubicación y sumamos monto, ordenamos y tomamos las top 10
    df_top_loc = df.groupby('ubicacion')['monto_total'].sum().nlargest(10).reset_index()
    fig_top_loc = px.bar(
        df_top_loc, 
        y="ubicacion", x="monto_total", orientation='h', # Barras horizontales
        text_auto='.2s',
        template="plotly_white", title="Top 10 Localidades con Mayor Inversión",
        labels={'ubicacion': 'Localidad', 'monto_total': 'Presupuesto Total ($)'},
        color_discrete_sequence=['#bc955c'] # Color dorado institucional
    )
    fig_top_loc.update_layout(yaxis={'categoryorder':'total ascending'}) # Ordenar de mayor a menor inversión

    return indicadores, fig_estatus, fig_top_loc, df.to_dict('records')

# Callback 2: Descarga Excel (Independiente)
@app.callback(
    Output("download-dataframe-excel", "data"),
    Input("btn-excel", "n_clicks"),
    [Input('dropdown-ubicacion', 'value'),
     Input('dropdown-estatus', 'value')],
    prevent_initial_call=True
)
def descargar_excel(n, ub, es):
    if n > 0:
        df = cargar_datos()
        if ub: df = df[df['ubicacion'].isin(ub)]
        if es: df = df[df['estatus_obra'].isin(es)]
        
        # Generar Excel y enviar
        return dcc.send_data_frame(df.to_excel, "Reporte_Obras_Filtrado_2026.xlsx", index=False)

# Al final de dashboard.py
if __name__ == '__main__':
    app.run(debug=True, port=8051)
