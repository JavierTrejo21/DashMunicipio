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

def analizar_desayunos_escolares(df):
    """Análisis estructurado para DIF Desayunos Escolares con paleta institucional unificada."""
    
    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip().str.title()

    columnas_reales = df.columns.tolist()
    
    col_actividad = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["ACTIVIDAD", "CONCEPTO"])), columnas_reales[6] if len(columnas_reales) > 6 else None)
    col_beneficiarios = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["BENEF"])), None)
    col_escuelas = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["ESCUELAS"])), None)
    col_cantidad = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["CANTIDAD", "TOTAL"])), None)
    col_mes = next((c for c in columnas_reales if "MES" in str(c).upper()), None)

    if not col_actividad:
        return dbc.Alert("⚠️ No se encontró una columna de actividad válida para Desayunos Escolares.", color="danger", className="m-3")

    df_limpio = pd.DataFrame()
    df_limpio['Actividad'] = df[col_actividad].astype(str).str.strip().str.title()
    df_limpio['Beneficiarios'] = pd.to_numeric(df[col_beneficiarios], errors='coerce').fillna(0) if col_beneficiarios else 0
    df_limpio['Escuelas'] = pd.to_numeric(df[col_escuelas], errors='coerce').fillna(0) if col_escuelas else 0
    df_limpio['Cantidad'] = pd.to_numeric(df[col_cantidad], errors='coerce').fillna(0) if col_cantidad else 0
    df_limpio['Mes'] = df[col_mes].astype(str).str.strip().str.capitalize() if col_mes and col_mes in df.columns else "General"

    total_desayunos = df_limpio['Cantidad'].sum()
    total_beneficiarios = df_limpio['Beneficiarios'].sum()
    total_escuelas = df_limpio['Escuelas'].sum()

    # --- KPI CARDS SUPERIORES ---
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
                html.H4(f"{int(total_beneficiarios):,} alumnos", style={"color": DORADO_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {DORADO_INST}"}), width=12, md=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("ESCUELAS BENEFICIADAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_escuelas)} planteles", style={"color": TEXTO_DARK, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {VERDE_CLARO}"}), width=12, md=4),
    ], className="mb-2")

    df_grouped = df_limpio.groupby('Actividad').agg(
        Cantidad=('Cantidad', 'sum'),
        Beneficiarios=('Beneficiarios', 'sum'),
        Escuelas=('Escuelas', 'sum')
    ).reset_index()
    
    df_grouped['Porcentaje'] = (df_grouped['Cantidad'] / total_desayunos * 100) if total_desayunos > 0 else 0
    df_grouped = df_grouped.sort_values(by='Cantidad', ascending=False).reset_index(drop=True)

    # Gráfica de Barras por Actividad / Modalidad
    fig_bloques = go.Figure()
    colores_barras = [VERDE_INST, "#0f766e", "#0d9488", DORADO_INST, "#4b5563"]
    
    for i, row in df_grouped.iterrows():
        fig_bloques.add_trace(go.Bar(
            x=[row['Actividad']],
            y=[row['Cantidad']],
            name=row['Actividad'],
            marker=dict(color=colores_barras[i % len(colores_barras)]),
            text=f"<b>{int(row['Cantidad']):,}</b><br><span style='font-size:11px;'>{row['Porcentaje']:.1f}%</span>",
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+text'
        ))

    fig_bloques.update_layout(
        title=dict(text="<b>DISTRIBUCIÓN Y PORCENTAJE POR MODALIDAD</b>", font=dict(size=12, color=TEXTO_DARK)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=30, l=40, r=20), height=350,
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color=TEXTO_DARK)),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", rangemode='tozero'),
        showlegend=False
    )

    # Gráfica Histórica por Mes (si existe la columna de mes)
    orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    if 'Mes' in df_limpio.columns and not df_limpio['Mes'].eq("General").all():
        df_meses = df_limpio.groupby('Mes').agg({'Cantidad': 'sum'}).reset_index()
        df_meses['Mes_Ord'] = pd.Categorical(df_meses['Mes'], categories=orden_meses, ordered=True)
        df_meses = df_meses.sort_values('Mes_Ord').dropna(subset=['Mes_Ord'])
    else:
        df_meses = pd.DataFrame({'Mes': ['Octubre', 'Noviembre', 'Diciembre'], 'Cantidad': [total_desayunos/3, total_desayunos/3, total_desayunos/3]})

    fig_lineas = go.Figure()
    fig_lineas.add_trace(go.Scatter(
        x=df_meses['Mes'], y=df_meses['Cantidad'],
        mode='lines+markers+text',
        name='Porciones',
        line=dict(color=VERDE_INST, width=3),
        marker=dict(size=8, color=DORADO_INST),
        text=df_meses['Cantidad'].apply(lambda x: f"{int(x):,}"),
        textposition="top center"
    ))
    fig_lineas.update_layout(
        title=dict(text="<b>HISTÓRICO DE ENTREGA DE PORCIONES POR MES</b>", font=dict(size=12, color=TEXTO_DARK)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=30, l=40, r=40), height=350,
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", rangemode='tozero'),
        showlegend=False
    )

    # Tarjetas Detalladas por Actividad
    tarjetas_records = []
    for _, row in df_grouped.iterrows():
        tarjetas_records.append(
            dbc.Col(html.Div([
                html.Div(style={"backgroundColor": VERDE_INST, "height": "4px", "position": "absolute", "top": "0", "left": "0", "width": "100%", "borderTopLeftRadius": "14px", "borderTopRightRadius": "14px"}),
                html.Div([
                    html.Div([html.I(className="bi bi-tag-fill me-2", style={"color": DORADO_INST}), html.Span(row['Actividad'], className="font-weight-bold", style={"fontSize": "0.78rem"})], style={"borderBottom": f"1px solid {GRIS_BORDES}", "paddingBottom": "6px"}),
                    html.H4(f"{int(row['Cantidad']):,} porciones", style={"color": VERDE_INST, "fontWeight": "bold", "fontSize": "1.15rem", "margin": "10px 0 6px 0"}),
                    html.P([html.I(className="bi bi-people-fill me-1 text-muted"), f"Beneficiarios: {int(row['Beneficiarios']):,} | Escuelas: {int(row['Escuelas'])}"], style={"fontSize": "0.75rem", "marginBottom": "0px"})
                ], style={"padding": "14px 12px"})
            ], className="bg-white border h-100 shadow-sm position-relative", style={"borderRadius": "14px"}), width=12, sm=6, md=4, lg=6, className="mb-3")
        )

    return html.Div([
        kpis_row,
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_bloques, config={'displayModeBar': False})], className="bg-white p-2 border shadow-sm mb-3", style={"borderRadius": "14px"}), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_lineas, config={'displayModeBar': False})], className="bg-white p-2 border shadow-sm mb-3", style={"borderRadius": "14px"}), md=6)
        ]),
        dbc.Row(tarjetas_records, className="mt-2")
    ])