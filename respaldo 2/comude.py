import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

def cargar_datos_comude():
    conn = sqlite3.connect('municipio.db')
    df = pd.read_sql_query("SELECT * FROM comude", conn)
    conn.close()
    return df

def layout_comude():
    return html.Div([
        html.H2("🏆 PANEL DE IMPACTO DEPORTIVO - COMUDE", style={'color': '#1a472a', 'fontWeight': 'bold'}),
        html.Hr(),

        # --- SECCIÓN DE FILTROS ---
        dbc.Row([
            dbc.Col([
                html.Label("Seleccionar Mes(es):", className="fw-bold"),
                dcc.Dropdown(
                    id='com-mes', 
                    options=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'], 
                    multi=True, 
                    placeholder="Filtrar por mes..."
                )
            ], md=12),
        ], className="mb-4 p-3 bg-white shadow-sm rounded"),

        # --- TARJETAS DE INDICADORES ---
        dbc.Row([
            dbc.Col(id='com-card-participantes', md=4),
            dbc.Col(id='com-card-equipos', md=4),
            dbc.Col(id='com-card-inversion', md=4),
        ], className="mb-4"),

        # --- GRÁFICAS DE ALTO IMPACTO ---
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("PREFERENCIA DEPORTIVA (PARTICIPANTES)", className="fw-bold bg-success text-white"),
                    dbc.CardBody([dcc.Graph(id='graph-deportes-impacto')])
                ], className="shadow-sm h-100")
            ], md=7),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("EQUILIBRIO DE GÉNERO", className="fw-bold bg-success text-white"),
                    dbc.CardBody([dcc.Graph(id='graph-genero-donut')])
                ], className="shadow-sm h-100")
            ], md=5),
        ], className="mb-4"),

        # --- TABLAS DE RESUMEN VISUAL ---
        dbc.Row([
            # Tabla 1: Top Comunidades con más actividad
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("TOP 5 COMUNIDADES CON MAYOR ACTIVIDAD", className="fw-bold text-dark"),
                    dbc.CardBody(id='tabla-comunidades-resumen')
                ], className="shadow-sm")
            ], md=6),
            
            # Tabla 2: Resumen por Tipo de Actividad
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("RESUMEN OPERATIVO POR TIPO", className="fw-bold text-dark"),
                    dbc.CardBody(id='tabla-tipo-resumen')
                ], className="shadow-sm")
            ], md=6),
        ], className="mb-4"),

        # --- DETALLE COMPLETO (Colapsable) ---
        dbc.Accordion([
            dbc.AccordionItem(
                [html.Div(id='com-tabla-completa')],
                title="VER LISTADO DETALLADO DE REGISTROS",
            ),
        ], start_collapsed=True, className="mb-5")
    ], className="p-3")

@callback(
    [Output('com-card-participantes', 'children'),
     Output('com-card-equipos', 'children'),
     Output('com-card-inversion', 'children'),
     Output('graph-deportes-impacto', 'figure'),
     Output('graph-genero-donut', 'figure'),
     Output('tabla-comunidades-resumen', 'children'),
     Output('tabla-tipo-resumen', 'children'),
     Output('com-tabla-completa', 'children')],
    [Input('com-mes', 'value')]
)
def actualizar_comude(mes):
    df = cargar_datos_comude()
    if mes: df = df[df['mes'].isin(mes)]

    # 1. MÉTRICAS
    total_part = df['participantes'].sum()
    total_eq = df['cantidad_equipos'].sum()
    total_inv = df['inversion'].sum()

    # 2. GRÁFICA DEPORTES (Barras con Gradiente)
    resumen_act = df.groupby('actividad')['participantes'].sum().sort_values(ascending=True).reset_index()
    fig_dep = px.bar(resumen_act, x='participantes', y='actividad', orientation='h',
                     color='participantes', color_continuous_scale='Viridis')
    fig_dep.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), yaxis_title=None)

    # 3. GRÁFICA GÉNERO (Donut Estilizado)
    fig_gen = px.pie(df, names='genero', values='participantes', hole=.5,
                     color_discrete_sequence=['#1a472a', '#bc955c', '#691c32'])
    fig_gen.update_layout(margin=dict(l=20, r=20, t=20, b=20))

    # 4. TABLA TOP COMUNIDADES (Lógica de Resumen)
    top_com = df.groupby('comunidad_sede').agg({
        'participantes': 'sum',
        'actividad': 'count'
    }).sort_values('participantes', ascending=False).head(5).reset_index()
    top_com.columns = ['COMUNIDAD', 'PARTICIPANTES', 'EVENTOS']
    
    tabla_com = dash_table.DataTable(
        data=top_com.to_dict('records'),
        columns=[{"name": i, "id": i} for i in top_com.columns],
        style_cell={'textAlign': 'center', 'fontSize': '12px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
    )

    # 5. TABLA RESUMEN POR TIPO
    tipo_res = df.groupby('tipo_registro').agg({
        'participantes': 'sum',
        'inversion': 'sum'
    }).reset_index()
    tipo_res.columns = ['CATEGORÍA', 'TOTAL PERSONAS', 'INVERSIÓN']
    
    tabla_tipo = dash_table.DataTable(
        data=tipo_res.to_dict('records'),
        columns=[{"name": i, "id": i} for i in tipo_res.columns],
        style_cell={'textAlign': 'center', 'fontSize': '12px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
    )

    # TARJETAS
    def generar_tarjeta(titulo, valor, icono, color):
        return dbc.Card([
            dbc.CardBody([
                html.Div([html.I(className=f"bi bi-{icono} me-2"), html.Span(titulo)], className="text-muted small"),
                html.H2(valor, style={'color': color, 'fontWeight': 'bold', 'marginTop': '5px'})
            ])
        ], className="text-center shadow-sm border-0", style={'borderBottom': f'4px solid {color}'})

    card1 = generar_tarjeta("Alcance Social", f"{int(total_part):,} Pers.", "people-fill", "#1a472a")
    card2 = generar_tarjeta("Fuerza Deportiva", f"{int(total_eq)} Equipos", "trophy-fill", "#bc955c")
    card3 = generar_tarjeta("Presupuesto Ejercido", f"${total_inv:,.2f}", "cash-stack", "#691c32")

    # TABLA COMPLETA
    tabla_full = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i.upper(), "id": i} for i in df.columns if i not in ['id', 'anio', 'trimestre', 'tipo_registro']],
        page_size=10, style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#1a472a', 'color': 'white'},
        filter_action="native"
    )

    return card1, card2, card3, fig_dep, fig_gen, tabla_com, tabla_tipo, tabla_full
