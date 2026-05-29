# areas/recepcion_presidenta.py
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
GRIS_BORDES = "#e5e7eb"
TEXTO_DARK = "#1f2937"

def analizar_recepcion_presidenta(df):
    """Análisis estructurado protegido políticamente para Presidencia."""
    columnas_reales = df.columns.tolist()
    
    col_categoria = next((c for c in columnas_reales if "CAT" in str(c).upper().replace("Í", "I")), None)
    col_inversion = next((c for c in columnas_reales if "INV" in str(c).upper().replace("Ó", "O")), None)
    col_beneficiarios = next((c for c in columnas_reales if "BENEF" in str(c).upper()), None)
    col_detalle = next((c for c in columnas_reales if "DETALLE" in str(c).upper()), None)
    col_desc = next((c for c in columnas_reales if "DESC" in str(c).upper().replace("Ó", "O")), None)

    if not all([col_categoria, col_inversion, col_beneficiarios]):
        return dbc.Alert("⚠️ Columnas faltantes para análisis global.", color="danger", className="m-3")

    df_limpio = pd.DataFrame()
    df_limpio['Categoria'] = df[col_categoria].astype(str).str.strip().str.upper()
    df_limpio['Inversión'] = pd.to_numeric(df[col_inversion], errors='coerce').fillna(0)
    df_limpio['Beneficiarios'] = pd.to_numeric(df[col_beneficiarios], errors='coerce').fillna(0)
    df_limpio['Detalle'] = df[col_detalle].astype(str).str.strip() if col_detalle else "Gestión Ordinaria"

    df_global = df_limpio.groupby('Categoria').agg({
        'Inversión': 'sum',
        'Beneficiarios': 'sum',
        'Detalle': 'count'
    }).reset_index()

    df_global = df_global[df_global['Inversión'] > 0].sort_values(by='Inversión', ascending=True)

    if df_global.empty:
        return dbc.Alert("No hay datos de inversión válidos.", color="warning", className="m-3")

    # Gráfica 1: Barras Horizontales
    fig_barras = go.Figure(go.Bar(
        y=df_global['Categoria'], x=df_global['Inversión'], orientation='h',
        marker=dict(color=GUINDA_INST, line=dict(color=DORADO_INST, width=1)),
        text=df_global['Inversión'].apply(lambda x: f" ${x:,.0f} "), textposition='outside'
    ))
    fig_barras.update_layout(
        title=dict(text="<b>INVERSIÓN FINANCIERA TOTAL POR RUBRO SECTORIAL</b>", font=dict(size=11, color=TEXTO_DARK)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, b=20, l=150, r=80), height=300,
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6")
    )

    # Gráfica 2: Burbujas Eficiencia Costo-Beneficio
    df_global['Costo_Por_Beneficiario'] = df_global['Inversión'] / df_global['Beneficiarios'].replace(0, 1)
    ref_size = (df_global['Costo_Por_Beneficiario'].max() / 50) if df_global['Costo_Por_Beneficiario'].max() > 0 else 1

    fig_burbujas = go.Figure(go.Scatter(
        x=df_global['Beneficiarios'], y=df_global['Inversión'], mode='markers+text',
        text=df_global['Categoria'], textposition="top center",
        marker=dict(size=df_global['Costo_Por_Beneficiario'], sizemode='diameter', sizeref=ref_size, sizemin=10, 
                    color=df_global['Inversión'], colorscale=[[0, DORADO_INST], [1, GUINDA_INST]])
    ))
    fig_burbujas.update_layout(
        title=dict(text="<b>CORRELACIÓN: PRESUPUESTO VS ALCANCE SOCIAL</b>", font=dict(size=11, color=TEXTO_DARK)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=55, b=40, l=60, r=40), height=300,
        xaxis=dict(title=dict(text="Ciudadanos Beneficiados", font=dict(size=9)), showgrid=True, gridcolor="#f3f4f6"),
        yaxis=dict(title=dict(text="Presupuesto Ejercido ($)", font=dict(size=9)), showgrid=True, gridcolor="#f3f4f6")
    )

    tarjetas_records = []
    for _, row in df_global.sort_values(by='Inversión', ascending=False).iterrows():
        tarjetas_records.append(
            dbc.Col(html.Div([
                html.Div(style={"backgroundColor": GUINDA_INST, "height": "4px", "position": "absolute", "top": "0", "left": "0", "width": "100%", "borderTopLeftRadius": "14px", "borderTopRightRadius": "14px"}),
                html.Div([
                    html.Div([html.I(className="bi bi-pie-chart-fill me-2", style={"color": DORADO_INST}), html.Span(row['Categoria'], className="font-weight-bold", style={"size": "0.75rem"})], style={"borderBottom": f"1px solid {GRIS_BORDES}", "paddingBottom": "5px"}),
                    html.H4(f"${row['Inversión']:,.2f}", style={"color": GUINDA_INST, "fontWeight": "bold", "fontSize": "1.2rem", "margin": "4px 0"}),
                    html.P([html.I(className="bi bi-people-fill me-1"), f"Beneficiarios: {int(row['Beneficiarios']):,} civ."], style={"fontSize": "0.72rem"}),
                    html.Small([html.B("Costo Promedio p/p: "), f"${row['Costo_Por_Beneficiario']:,.2f}"], className="text-secondary font-italic")
                ], style={"padding": "14px 12px"})
            ], className="bg-white border h-100 shadow-sm position-relative", style={"borderRadius": "14px"}), width=12, sm=6, md=4, lg=3, className="mb-3")
        )

    return html.Div([
        dbc.Row([dbc.Col(html.Div([dcc.Graph(figure=fig_barras, config={'displayModeBar': False})]), md=6),
                 dbc.Col(html.Div([dcc.Graph(figure=fig_burbujas, config={'displayModeBar': False})]), md=6)]),
        dbc.Row(tarjetas_records)
    ])
