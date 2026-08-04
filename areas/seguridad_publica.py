# areas/seguridad_publica.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

# Colorimetría institucional unificada
GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
TEXTO_DARK = "#1f2937"
TEXTO_SECUNDARIO = "#374151"

def analizar_seguridad_publica(df):
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Seguridad Pública no contiene registros válidos.", color="warning", className="m-3")

    df_seg = df.copy()
    df_seg.columns = [str(c).strip().upper() for c in df_seg.columns]
    
    # Identificación segura de columnas
    col_actividad = next((c for c in df_seg.columns if "ACTIVIDAD" in c or "CONCEPTO" in c), "ACTIVIDAD")
    col_atendidos = next((c for c in df_seg.columns if "ATEND" in c or "TOTAL" in c or "CANTIDAD" in c), "ATENDIDOS")
    col_mes = next((c for c in df_seg.columns if "MES" in c), "MES")
    col_variable = next((c for c in df_seg.columns if "VAR" in c), "VARIABLE")

    # Limpieza numérica
    df_seg[col_atendidos] = pd.to_numeric(df_seg[col_atendidos], errors='coerce').fillna(0)

    # Métricas clave para las tarjetas KPI
    total_acciones = df_seg[col_atendidos].sum()
    recorridos_prevencion = df_seg[df_seg[col_actividad].str.upper().str.contains("RECORRIDOS", na=False)][col_atendidos].sum()
    reportes_ciudadanos = df_seg[df_seg[col_actividad].str.upper().str.contains("REPORTES", na=False)][col_atendidos].sum()
    puesta_disposicion = df_seg[df_seg[col_actividad].str.upper().str.contains("DISPOSICION", na=False)][col_atendidos].sum()

    estilo_kpi = {
        "borderRadius": "8px", 
        "transition": "all 0.25s ease-in-out"
    }

    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": GUINDA_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("TOTAL ACCIONES Y OPERATIVOS", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"{total_acciones:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": TEXTO_DARK, "fontSize": "1.25rem"}),
                html.Small("Registros operativos acumulados", className="d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px", "color": GUINDA_INST})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": DORADO_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("RECORRIDOS DE PREVENCIÓN", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"{recorridos_prevencion:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": GUINDA_INST, "fontSize": "1.25rem"}),
                html.Small("Presencia policial constante", className="d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px", "color": DORADO_INST})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": GUINDA_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("REPORTES CIUDADANOS ATENDIDOS", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"{reportes_ciudadanos:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": TEXTO_DARK, "fontSize": "1.25rem"}),
                html.Small("Atención oportuna a llamadas", className="d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px", "color": GUINDA_INST})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": DORADO_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("PUESTAS A DISPOSICIÓN", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"{puesta_disposicion:,.0f}", className="m-0 font-weight-bold mt-1", style={"color": GUINDA_INST, "fontSize": "1.25rem"}),
                html.Small("Coordinación con instancias legales", className="d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px", "color": DORADO_INST})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
    ], className="mb-2")

    # Agrupaciones para gráficos
    df_actividad = df_seg.groupby(col_actividad, as_index=False)[col_atendidos].sum().sort_values(by=col_atendidos, ascending=True)
    
    fig_actividades = px.bar(
        df_actividad,
        x=col_atendidos,
        y=col_actividad,
        orientation='h',
        title="<b>Volumen de Acciones por Tipo de Actividad Policial</b>",
        labels={col_atendidos: "Total de Atenciones", col_actividad: "Actividad"},
        color_discrete_sequence=[GUINDA_INST]
    )
    fig_actividades.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color=TEXTO_DARK),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
        yaxis=dict(showgrid=False)
    )

    df_variable = df_seg.groupby(col_variable, as_index=False)[col_atendidos].sum()
    
    fig_variable = px.pie(
        df_variable,
        names=col_variable,
        values=col_atendidos,
        title="<b>Distribución Estratégica por Variable de Seguridad</b>",
        color_discrete_sequence=[GUINDA_INST, DORADO_INST, "#115e59", "#d97706", "#2563eb"],
        hole=0.4
    )
    fig_variable.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color=TEXTO_DARK),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )

    # Tabla detallada para el informe
    columnas_tabla = [
        {"name": "Actividad Operativa", "id": col_actividad},
        {"name": "Variable Estratégica", "id": col_variable},
        {"name": "Mes de Registro", "id": col_mes},
        {"name": "Total Atendidos / Acciones", "id": col_atendidos}
    ]

    tabla_detallada = html.Div([
        html.Div([
            html.I(className="bi bi-table me-2"), "REGISTROS DETALLADOS DE SEGURIDAD PÚBLICA MUNICIPAL"
        ], style={"backgroundColor": GUINDA_INST, "color": "white", "padding": "8px 12px", "fontWeight": "bold", "fontSize": "0.75rem", "borderRadius": "6px 6px 0 0"}),
        html.Div([
            dash_table.DataTable(
                data=df_seg.to_dict('records'),
                columns=columnas_tabla,
                page_size=8,
                filter_action='native',
                sort_action='native',
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': '#f3f4f6', 'color': TEXTO_DARK, 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'},
                style_cell={'padding': '10px 8px', 'fontSize': '11px', 'fontFamily': 'sans-serif', 'textAlign': 'left', 'borderBottom': '1px solid #f9fafb', 'color': TEXTO_DARK},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}
                ]
            )
        ], className="border border-top-0 p-2 bg-white", style={"borderRadius": "0 0 6px 6px"})
    ], className="mb-3 shadow-sm")

    return html.Div([
        tarjetas_kpi,
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_actividades, config={"displayModeBar": False})], className="bg-white border p-2 shadow-sm mb-3", style={"borderRadius": "6px"}), md=7),
            dbc.Col(html.Div([dcc.Graph(figure=fig_variable, config={"displayModeBar": False})], className="bg-white border p-2 shadow-sm mb-3", style={"borderRadius": "6px"}), md=5),
        ]),
        dbc.Row([
            dbc.Col(tabla_detallada, md=12)
        ])
    ], style={"padding": "5px"})