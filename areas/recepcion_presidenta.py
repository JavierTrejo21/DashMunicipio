import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

# Paleta institucional unificada (Verde Petróleo + Guinda/Dorado)
VERDE_INST = "#115e59"
VERDE_CLARO = "#14b8a6"
GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
GRIS_BORDES = "#e5e7eb"
TEXTO_DARK = "#1f2937"

def analizar_recepcion_presidenta(df):
    """Análisis estructurado con paleta institucional unificada."""
    
    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip()

    columnas_reales = df.columns.tolist()
    
    col_categoria = next((c for c in columnas_reales if "CAT" in str(c).upper().replace("Í", "I")), None)
    col_inversion = next((c for c in columnas_reales if "INV" in str(c).upper().replace("Ó", "O")), None)
    col_beneficiarios = next((c for c in columnas_reales if "BENEF" in str(c).upper()), None)
    col_mes = next((c for c in columnas_reales if "MES" in str(c).upper()), None)
    col_tipo = next((c for c in columnas_reales if "TIPO" in str(c).upper()), None)

    if not all([col_categoria, col_inversion, col_beneficiarios]):
        return dbc.Alert("⚠️ Columnas faltantes para análisis global.", color="danger", className="m-3")

    df_limpio = pd.DataFrame()
    df_limpio['Categoria'] = df[col_categoria].astype(str).str.strip().str.title()
    df_limpio['Inversión'] = pd.to_numeric(df[col_inversion], errors='coerce').fillna(0)
    df_limpio['Beneficiarios'] = pd.to_numeric(df[col_beneficiarios], errors='coerce').fillna(0)
    df_limpio['Mes'] = df[col_mes].astype(str).str.strip().str.capitalize() if col_mes else "General"
    df_limpio['Tipo'] = df[col_tipo].astype(str).str.strip().str.title() if col_tipo else "General"

    df_limpio = df_limpio[
        (df_limpio['Categoria'] != '') & 
        (df_limpio['Categoria'] != 'Nan') & 
        (df_limpio['Inversión'] > 0)
    ]

    total_inversion = df_limpio['Inversión'].sum()
    total_beneficiarios = df_limpio['Beneficiarios'].sum()
    total_registros = len(df_limpio)

    # --- KPI CARDS SUPERIORES ---
    kpis_row = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("INVERSIÓN TOTAL", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"${total_inversion:,.2f}", style={"color": VERDE_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {VERDE_INST}"}), width=12, md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("BENEFICIARIOS TOTALES", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_beneficiarios):,} civ.", style={"color": DORADO_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {DORADO_INST}"}), width=12, md=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("GESTIONES ATENDIDAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{total_registros:,}", style={"color": TEXTO_DARK, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {VERDE_CLARO}"}), width=12, md=4),
    ], className="mb-2")

    df_global = df_limpio.groupby('Categoria')['Inversión'].sum().reset_index()
    df_global['Porcentaje'] = (df_global['Inversión'] / total_inversion) * 100
    df_global = df_global.sort_values(by='Inversión', ascending=False).reset_index(drop=True)

    df_top = df_global.head(5).copy()

    # Gráfica de Barras Superiores con la Paleta Institucional (Verde Petróleo)
    fig_bloques = go.Figure()
    colores_barras = [VERDE_INST, "#0f766e", "#0d9488", DORADO_INST, "#4b5563"]
    
    for i, row in df_top.iterrows():
        fig_bloques.add_trace(go.Bar(
            x=[row['Categoria']],
            y=[row['Inversión']],
            name=row['Categoria'],
            marker=dict(color=colores_barras[i % len(colores_barras)]),
            text=f"<b>${row['Inversión']:,.0f}</b><br><span style='font-size:11px;'>{row['Porcentaje']:.1f}%</span>",
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+text'
        ))

    fig_bloques.update_layout(
        title=dict(text="<b>DISTRIBUCIÓN Y PORCENTAJE DE PRINCIPALES RUBROS</b>", font=dict(size=12, color=TEXTO_DARK)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=30, l=40, r=20), height=350,
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color=TEXTO_DARK)),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", rangemode='tozero'),
        showlegend=False
    )

    # Gráfica de Líneas Históricas unificada con el tono Verde Institucional
    orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df_meses = df_limpio.groupby('Mes').agg({'Inversión': 'sum', 'Beneficiarios': 'count'}).reset_index().rename(columns={'Beneficiarios': 'Gestiones'})
    df_meses['Mes_Ord'] = pd.Categorical(df_meses['Mes'], categories=orden_meses, ordered=True)
    df_meses = df_meses.sort_values('Mes_Ord').dropna(subset=['Mes_Ord'])

    fig_lineas = go.Figure()
    fig_lineas.add_trace(go.Scatter(
        x=df_meses['Mes'], y=df_meses['Inversión'],
        mode='lines+markers+text',
        name='Inversión ($)',
        line=dict(color=VERDE_INST, width=3),
        marker=dict(size=8, color=DORADO_INST),
        text=df_meses['Inversión'].apply(lambda x: f"${x:,.0f}"),
        textposition="top center"
    ))
    fig_lineas.update_layout(
        title=dict(text="<b>HISTÓRICO GENERAL DE INVERSIÓN POR MES</b>", font=dict(size=12, color=TEXTO_DARK)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=30, l=40, r=40), height=350,
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", rangemode='tozero'),
        showlegend=False
    )

    # Tarjetas Detalladas por Categoría (Borde superior con Verde Institucional)
    tarjetas_records = []
    for _, row in df_global.iterrows():
        beneficiarios_cat = df_limpio[df_limpio['Categoria'] == row['Categoria']]['Beneficiarios'].sum()
        tarjetas_records.append(
            dbc.Col(html.Div([
                html.Div(style={"backgroundColor": VERDE_INST, "height": "4px", "position": "absolute", "top": "0", "left": "0", "width": "100%", "borderTopLeftRadius": "14px", "borderTopRightRadius": "14px"}),
                html.Div([
                    html.Div([html.I(className="bi bi-tag-fill me-2", style={"color": DORADO_INST}), html.Span(row['Categoria'], className="font-weight-bold", style={"fontSize": "0.78rem"})], style={"borderBottom": f"1px solid {GRIS_BORDES}", "paddingBottom": "6px"}),
                    html.H4(f"${row['Inversión']:,.2f}", style={"color": VERDE_INST, "fontWeight": "bold", "fontSize": "1.15rem", "margin": "10px 0 6px 0"}),
                    html.P([html.I(className="bi bi-people-fill me-1 text-muted"), f"Beneficiarios: {int(beneficiarios_cat):,} civ."], style={"fontSize": "0.75rem", "marginBottom": "0px"})
                ], style={"padding": "14px 12px"})
            ], className="bg-white border h-100 shadow-sm position-relative", style={"borderRadius": "14px"}), width=12, sm=6, md=4, lg=3, className="mb-3")
        )

    return html.Div([
        kpis_row,
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_bloques, config={'displayModeBar': False})], className="bg-white p-2 border shadow-sm mb-3", style={"borderRadius": "14px"}), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_lineas, config={'displayModeBar': False})], className="bg-white p-2 border shadow-sm mb-3", style={"borderRadius": "14px"}), md=6)
        ]),
        dbc.Row(tarjetas_records, className="mt-2")
    ])