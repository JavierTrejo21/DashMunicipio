import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, callback, Input, Output

# Paleta institucional unificada (Verde Petróleo + Guinda/Dorado)
VERDE_INST = "#115e59"
VERDE_CLARO = "#14b8a6"
GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
GRIS_BORDES = "#e5e7eb"
TEXTO_DARK = "#1f2937"

# Variable global interna para mantener el DataFrame limpio disponible para el callback
_df_desayunos_cache = None

def analizar_desayunos_escolares(df):
    """Análisis estructurado para DIF Desayunos Escolares con enfoque institucional, tarjeta de beneficiarios en guinda y tabla filtrable."""
    global _df_desayunos_cache
    
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Desayunos Escolares no contiene registros válidos.", color="danger", className="m-3")

    df_clean = df.copy()
    df_clean.columns = [str(c).strip() for c in df_clean.columns]
    
    # Mapeo exacto de columnas
    col_mes = next((c for c in df_clean.columns if "MES" in c.upper()), "Mes")
    col_comunidad = next((c for c in df_clean.columns if "COMUNIDAD" in c.upper()), "Comunidad")
    col_beneficiarios = next((c for c in df_clean.columns if "BENEFICIARIO" in c.upper()), "Beneficiarios")
    col_escuelas = next((c for c in df_clean.columns if "ESCUELA" in c.upper()), "Escuelas beneficiadas")
    col_cantidad = next((c for c in df_clean.columns if "CANTIDAD" in c.upper() or "TOTAL" in c.upper()), "Cantidad")
    col_actividad = next((c for c in df_clean.columns if "ACTIVIDAD" in c.upper() or "CONCEPTO" in c.upper()), "Actividad")

    # Limpieza y normalización
    df_limpio = pd.DataFrame()
    df_limpio['Mes'] = df_clean[col_mes].astype(str).str.strip().str.capitalize()
    df_limpio['Comunidad'] = df_clean[col_comunidad].astype(str).str.strip().str.title()
    df_limpio['Beneficiarios'] = pd.to_numeric(df_clean[col_beneficiarios], errors='coerce').fillna(0)
    df_limpio['Escuelas'] = pd.to_numeric(df_clean[col_escuelas], errors='coerce').fillna(0)
    df_limpio['Cantidad'] = pd.to_numeric(df_clean[col_cantidad], errors='coerce').fillna(0)
    df_limpio['Actividad'] = df_clean[col_actividad].astype(str).str.strip().str.title()

    # Guardamos en caché para el callback
    _df_desayunos_cache = df_limpio.copy()

    # Métricas Globales
    total_desayunos = df_limpio['Cantidad'].sum()
    
    # Cálculo exacto de Beneficiarios (Máximo por comunidad y mes, luego suma de máximos)
    df_benef_mes = df_limpio.groupby(['Comunidad', 'Mes'], as_index=False)['Beneficiarios'].max()
    max_benef_por_comunidad = df_benef_mes.groupby('Comunidad')['Beneficiarios'].max()
    total_beneficiarios = int(max_benef_por_comunidad.sum())

    # Cálculo exacto de Escuelas (Máximo por comunidad y mes, luego suma de máximos)
    df_escuelas_mes = df_limpio.groupby(['Comunidad', 'Mes'], as_index=False)['Escuelas'].max()
    max_escuelas_por_comunidad = df_escuelas_mes.groupby('Comunidad')['Escuelas'].max()
    total_escuelas_acumulado = int(max_escuelas_por_comunidad.sum())

    comunidades_disponibles = sorted(df_limpio['Comunidad'].unique())

    # --- TARJETA DE ENFOQUE DEL MÓDULO ---
    enfoque_card = html.Div([
        html.Div("ENFOQUE DEL PROGRAMA DE DESAYUNOS ESCOLARES", className="text-white px-4 py-3 font-weight-bold", style={"backgroundColor": VERDE_INST, "borderTopLeftRadius": "14px", "borderTopRightRadius": "14px", "letterSpacing": "0.5px", "fontSize": "0.9rem"}),
        html.Div([
            html.P("El programa opera mediante la entrega permanente de desayunos fríos y calientes destinados a más de 118 escuelas en el municipio y más de 2,114 alumnos, asegurando una nutrición infantil adecuada y el rendimiento escolar.", className="text-muted mb-3", style={"fontSize": "0.85rem", "lineHeight": "1.5"}),
            html.Ul([
                html.Li("Operación continua de modalidades en desayunos escolares fríos y calientes.", className="mb-2 text-dark", style={"fontSize": "0.83rem"}),
                html.Li("Control geográfico y seguimiento operativo enfocado en más de 118 escuelas del municipio.", className="mb-2 text-dark", style={"fontSize": "0.83rem"}),
                html.Li(f"Volumen general acumulado en el periodo: {int(total_desayunos):,} porciones entregadas a más de 2,114 alumnos.", className="text-dark", style={"fontSize": "0.83rem", "fontWeight": "600"}),
            ], className="mb-0 ps-3")
        ], className="p-4")
    ], className="bg-white border shadow-sm mb-4", style={"borderRadius": "14px"})

    # --- KPI CARDS SUPERIORES (Beneficiarios en color GUINDA_INST) ---
    kpis_row = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("TOTAL DE PORCIONES", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_desayunos):,} porciones", style={"color": VERDE_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {VERDE_INST}"}), width=12, md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("BENEFICIARIOS ATENDIDOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_beneficiarios):,} alumnos", style={"color": GUINDA_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {GUINDA_INST}"}), width=12, md=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("ESCUELAS BENEFICIADAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{total_escuelas_acumulado:,} escuelas", style={"color": TEXTO_DARK, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {VERDE_CLARO}"}), width=12, md=4),
    ], className="mb-2")

    # --- GRÁFICA HISTÓRICA EXTENDIDA (LÍNEA COLOR GUINDA) ---
    orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df_meses = df_limpio.groupby('Mes', as_index=False)['Cantidad'].sum()
    df_meses['Mes_Ord'] = pd.Categorical(df_meses['Mes'], categories=orden_meses, ordered=True)
    df_meses = df_meses.sort_values('Mes_Ord').dropna(subset=['Mes_Ord'])

    fig_lineas = go.Figure()
    fig_lineas.add_trace(go.Scatter(
        x=df_meses['Mes'], y=df_meses['Cantidad'],
        mode='lines+markers+text',
        name='Porciones',
        line=dict(color=GUINDA_INST, width=3),
        marker=dict(size=8, color=DORADO_INST),
        text=df_meses['Cantidad'].apply(lambda x: f"{int(x):,}"),
        textposition="top center"
    ))
    fig_lineas.update_layout(
        title=dict(text="<b>HISTÓRICO DE ENTREGA DE PORCIONES POR MES</b>", font=dict(size=12, color=TEXTO_DARK)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=30, l=40, r=40), height=350,
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6", tickangle=0),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", rangemode='tozero'),
        showlegend=False
    )

    grafica_larga_row = dbc.Row([
        dbc.Col(
            html.Div([
                dcc.Graph(figure=fig_lineas, config={'displayModeBar': False})
            ], className="bg-white p-2 border shadow-sm mb-3", style={"borderRadius": "14px"}),
            width=12
        )
    ])

    # --- TABLA INTERACTIVA (DATOS INICIALES COMPLETOS) ---
    df_tabla_inicial = df_limpio[['Comunidad', 'Mes', 'Actividad', 'Escuelas', 'Beneficiarios', 'Cantidad']].copy()
    df_tabla_inicial.columns = ['Comunidad', 'Mes', 'Modalidad', 'Escuelas', 'Beneficiarios', 'Porciones']

    tabla_detallada = dash_table.DataTable(
        id='tabla-comunidades-desayunos',
        data=df_tabla_inicial.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df_tabla_inicial.columns],
        page_size=5,
        style_table={
            'overflowX': 'auto', 
            'overflowY': 'auto', 
            'maxHeight': '320px',
            'borderRadius': '8px'
        },
        style_header={
            'backgroundColor': VERDE_INST,
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'fontSize': '0.8rem',
            'border': 'none'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px 12px',
            'fontSize': '0.78rem',
            'fontFamily': 'sans-serif',
            'color': TEXTO_DARK,
            'borderBottom': f'1px solid {GRIS_BORDES}'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}
        ],
        sort_action='native'
    )

    # --- SECCIÓN DE FILTRO INTERACTIVO CIUDADANO (TÍTULO EN COLOR GUINDA) ---
    filtro_seccion = html.Div([
        html.Div([
            html.H6("CONSULTA DETALLADA POR COMUNIDAD", className="font-weight-bold mb-2", style={"fontSize": "0.9rem", "color": GUINDA_INST}),
            html.P("Selecciona o busca una comunidad para verificar el detalle de las escuelas beneficiadas, alumnos y porciones entregadas:", className="text-muted mb-3", style={"fontSize": "0.78rem"}),
            dcc.Dropdown(
                id='dropdown-filtro-comunidad-desayunos',
                options=[{'label': c, 'value': c} for c in comunidades_disponibles],
                placeholder="Selecciona una comunidad (muestra todos si está vacío)...",
                clearable=True,
                className="mb-3",
                style={"fontSize": "0.85rem"}
            ),
        ], className="p-3 bg-white border shadow-sm mb-3", style={"borderRadius": "14px"}),
        html.Div([
            tabla_detallada
        ], className="p-3 bg-white border shadow-sm mb-4", style={"borderRadius": "14px"})
    ])

    return html.Div([
        enfoque_card,
        kpis_row,
        grafica_larga_row,
        filtro_seccion
    ])

# --- CALLBACK PARA FILTRAR LA TABLA EN TIEMPO REAL ---
@callback(
    Output('tabla-comunidades-desayunos', 'data'),
    Input('dropdown-filtro-comunidad-desayunos', 'value')
)
def filtrar_tabla_comunidad(comunidad_seleccionada):
    global _df_desayunos_cache
    if _df_desayunos_cache is None or _df_desayunos_cache.empty:
        return []
    
    df_tabla = _df_desayunos_cache[['Comunidad', 'Mes', 'Actividad', 'Escuelas', 'Beneficiarios', 'Cantidad']].copy()
    df_tabla.columns = ['Comunidad', 'Mes', 'Modalidad', 'Escuelas', 'Beneficiarios', 'Porciones']
    
    if comunidad_seleccionada:
        df_tabla = df_tabla[df_tabla['Comunidad'] == comunidad_seleccionada]
        
    return df_tabla.to_dict('records')