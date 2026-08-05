# areas/seguridad_publica.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

# Colorimetría institucional unificada
GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
VERDE_OSCURO = "#0f4c3a"
TEXTO_DARK = "#1f2937"

def analizar_seguridad_publica(df):
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Seguridad Pública no contiene registros válidos.", color="warning", className="m-3")

    df_seg = df.copy()
    df_seg.columns = [str(c).strip().upper() for c in df_seg.columns]
    
    # Identificación segura de columnas
    col_actividad = next((c for c in df_seg.columns if "ACTIVIDAD" in c or "CONCEPTO" in c), df_seg.columns[0])
    col_atendidos = next((c for c in df_seg.columns if "ATEND" in c or "TOTAL" in c or "CANTIDAD" in c), df_seg.columns[1])
    col_mes = next((c for c in df_seg.columns if "MES" in c), df_seg.columns[2])
    col_variable = next((c for c in df_seg.columns if "VAR" in c), df_seg.columns[3])

    # Limpieza numérica de atenciones
    df_seg[col_atendidos] = pd.to_numeric(df_seg[col_atendidos].astype(str).str.replace(r"[^\d.]", "", regex=True), errors='coerce').fillna(0)

    # Tarjetas KPI basadas exactamente en las actividades del Excel
    accidentes = df_seg[df_seg[col_actividad].str.upper().str.contains("ACCIDENTES DE TRANSITO", na=False)][col_atendidos].sum()
    reportes = df_seg[df_seg[col_actividad].str.upper().str.contains("REPORTES CIUDADANOS", na=False)][col_atendidos].sum()
    catastrofes = df_seg[df_seg[col_actividad].str.upper().str.contains("CATASTROFES", na=False)][col_atendidos].sum()
    
    # Suma de ambas puestas a disposición para una tarjeta resumen general limpia
    puestas_disposicion = df_seg[df_seg[col_actividad].str.upper().str.contains("PUESTAS A DISPOSICIÓN", na=False)][col_atendidos].sum()

    estilo_kpi = {
        "backgroundColor": "white",
        "border": "1px solid #e5e7eb",
        "borderRadius": "8px",
        "padding": "15px 20px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.05)"
    }

    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Small("ACCIDENTES DE TRÁNSITO", className="d-block font-weight-bold text-muted", style={"fontSize": "0.7rem", "letterSpacing": "0.5px"}),
                html.H3(f"{accidentes:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": GUINDA_INST, "fontSize": "1.25rem"})
            ], style=estilo_kpi), md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Small("REPORTES CIUDADANOS", className="d-block font-weight-bold text-muted", style={"fontSize": "0.7rem", "letterSpacing": "0.5px"}),
                html.H3(f"{reportes:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": GUINDA_INST, "fontSize": "1.25rem"})
            ], style=estilo_kpi), md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Small("CATÁSTROFES ATENDIDAS", className="d-block font-weight-bold text-muted", style={"fontSize": "0.7rem", "letterSpacing": "0.5px"}),
                html.H3(f"{catastrofes:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": GUINDA_INST, "fontSize": "1.25rem"})
            ], style=estilo_kpi), md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Small("PUESTAS A DISPOSICIÓN", className="d-block font-weight-bold text-muted", style={"fontSize": "0.7rem", "letterSpacing": "0.5px"}),
                html.H3(f"{puestas_disposicion:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": TEXTO_DARK, "fontSize": "1.25rem"})
            ], style=estilo_kpi), md=3, className="mb-3"
        ),
    ], className="mb-3")

    # Gráficos principales
    df_actividad = df_seg.groupby(col_actividad, as_index=False)[col_atendidos].sum().sort_values(by=col_atendidos, ascending=True)
    
    fig_actividades = px.bar(
        df_actividad,
        x=col_atendidos,
        y=col_actividad,
        orientation='h',
        text=col_atendidos,
        title="<b>VOLUMEN DE ACCIONES POR TIPO DE ACTIVIDAD POLICIAL</b>",
        color_discrete_sequence=[VERDE_OSCURO]
    )
    fig_actividades.update_traces(texttemplate='%{text:,.0f}', textposition='inside', insidetextanchor='middle')
    fig_actividades.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color=TEXTO_DARK),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6", title=""),
        yaxis=dict(showgrid=False, title="")
    )

    df_variable = df_seg.groupby(col_variable, as_index=False)[col_atendidos].sum()
    
    fig_variable = px.pie(
        df_variable,
        names=col_variable,
        values=col_atendidos,
        title="<b>DISTRIBUCIÓN ESTRATÉGICA POR VARIABLE</b>",
        color_discrete_sequence=[VERDE_OSCURO, DORADO_INST, GUINDA_INST, "#2563eb", "#d97706"],
        hole=0.4
    )
    fig_variable.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color=TEXTO_DARK),
        margin=dict(l=20, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )

    # Tabla detallada interactiva
    columnas_tabla = [
        {"name": "Actividad Operativa", "id": col_actividad},
        {"name": "Variable Estratégica", "id": col_variable},
        {"name": "Mes de Registro", "id": col_mes},
        {"name": "Total Atendidos / Acciones", "id": col_atendidos}
    ]

    tabla_detallada = html.Div([
        html.Div([
            html.H6("REGISTROS DETALLADOS DE SEGURIDAD PÚBLICA MUNICIPAL", className="m-0 font-weight-bold", style={"color": GUINDA_INST, "fontSize": "0.95rem"})
        ], className="mb-3 p-3 bg-white rounded-3 shadow-sm border"),
        html.Div([
            dash_table.DataTable(
                data=df_seg.to_dict('records'),
                columns=columnas_tabla,
                page_size=8,
                filter_action='native',
                sort_action='native',
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': '#f3f4f6', 'color': TEXTO_DARK, 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'left'},
                style_cell={'padding': '8px', 'fontSize': '11px', 'textAlign': 'left', 'fontFamily': 'sans-serif', 'color': TEXTO_DARK},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}]
            )
        ], className="p-3 bg-white rounded-3 shadow-sm border")
    ])

    return html.Div([
        html.Div([
            html.H5("EVALUACIÓN Y ACCIONES DE SEGURIDAD PÚBLICA", className="m-0 font-weight-bold", style={"color": GUINDA_INST, "fontSize": "1.1rem"}),
            html.P("Reporte operativo de vigilancia, prevención y atención ciudadana.", className="text-muted m-0", style={"fontSize": "0.82rem"})
        ], className="mb-3"),

        tarjetas_kpi,

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_actividades, config={"displayModeBar": False})], className="bg-white border p-2 shadow-sm mb-3 rounded-3"), md=7),
            dbc.Col(html.Div([dcc.Graph(figure=fig_variable, config={"displayModeBar": False})], className="bg-white border p-2 shadow-sm mb-3 rounded-3"), md=5),
        ]),

        tabla_detallada

    ], style={"padding": "10px"})