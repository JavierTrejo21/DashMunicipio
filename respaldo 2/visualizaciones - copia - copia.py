import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

# Paleta Institucional - Gobierno del Estado de Hidalgo
GUINDA_INST = "#691c32"      # Color principal institucional
DORADO_INST = "#bc955c"      # Color de acento de gobierno
GRIS_TEXTO = "#4b5563"       # Texto secundario legible
GRIS_FONDO = "#f3f4f6"       # Fondo de página institucional

# Degradados de color modernos para gráficos
COLORS_GOV = ['#691c32', '#a61c3c', '#bc955c', '#8d7249', '#374151', '#4b5563']

def crear_tarjeta_estilo_acuerdo(titulo, valor, subtitulo, icono_class, color_borde):
    """
    Réplica de las filas de Acuerdos/Secciones de portales de Gobierno hidalguenses.
    Diseño horizontal compacto, limpio y de alto impacto formal.
    """
    return dbc.Col(
        html.Div([
            # Franja lateral de color institucional para dar estructura
            html.Div(style={
                'width': '6px', 
                'backgroundColor': color_borde, 
                'borderRadius': '4px 0 0 4px',
                'position': 'absolute',
                'top': '0', 'bottom': '0', 'left': '0'
            }),
            
            # Contenedor del Icono Izquierdo
            html.Div([
                html.I(className=f"{icono_class}", style={'color': color_borde, 'fontSize': '1.6rem'}),
            ], style={'padding': '15px 20px', 'display': 'flex', 'alignItems': 'center'}),
            
            # Cuerpo de texto central
            html.Div([
                html.H5(titulo, style={
                    'color': '#1f2937', 'fontWeight': '700', 'fontSize': '0.95rem', 
                    'marginBottom': '2px', 'textTransform': 'uppercase', 'letterSpacing': '0.3px'
                }),
                html.P(subtitulo, style={'color': GRIS_TEXTO, 'fontSize': '0.75rem', 'margin': '0'})
            ], style={'flexGrow': '1', 'padding': '15px 10px', 'alignSelf': 'center'}),
            
            # Bloque de Métrica / Valor destacado a la derecha
            html.Div([
                html.Span(valor, style={
                    'color': '#111827', 'fontWeight': '800', 'fontSize': '1.4rem',
                    'backgroundColor': '#f9fafb', 'padding': '6px 14px', 'borderRadius': '8px',
                    'border': '1px solid #e5e7eb'
                })
            ], style={'padding': '15px 20px', 'display': 'flex', 'alignItems': 'center'})
            
        ], className="bg-white shadow-sm d-flex position-relative mb-3", style={
            'borderRadius': '8px', 'border': '1px solid #e5e7eb', 'overflow': 'hidden',
            'transition': 'all 0.2s ease-in-out'
        }),
        md=6, xs=12  # Se organiza en pares (2 por fila) para que parezcan los Acuerdos del portal
    )

def generar_tablero_impacto(df):
    """Genera reportes y gráficas institucionales basados en reglas de negocio"""
    if df.empty:
        return html.Div("Esperando carga de datos gubernamentales...", className="text-muted text-center p-5")

    # --- IDENTIFICACIÓN DE COLUMNAS ---
    col_inv = [c for c in df.columns if any(k in c.upper() for k in ['INVERSION', 'MONTO', 'COSTO', 'EJERCIDO'])]
    col_ben = [c for c in df.columns if any(k in c.upper() for k in ['BENEFICIARIO', 'PERSONA', 'ATENDIDOS', 'CANTIDAD'])]
    col_act = [c for c in df.columns if any(k in c.upper() for k in ['ACTIVIDAD', 'ACCION', 'CONCEPTO', 'PROGRAMA'])]
    col_var = [c for c in df.columns if any(k in c.upper() for k in ['VARIABLE', 'DIRECCION'])]

    total_inv = df[col_inv[0]].sum() if col_inv else 0
    total_ben = df[col_ben[0]].sum() if col_ben else 0

    # --- FILTRADO INTELIGENTE DE SEGMENTOS ---
    df_temas = df[df[col_var[0]].str.contains('TEMAS|TRANSTORNOS|TRASTORNOS|ASUNTO|CONCEPTO', case=False, na=False)]
    df_demo = df[df[col_var[0]].str.contains('DEMOGRAFICA|PACIENTES|PERFIL|COMUNIDAD|LOCALIDAD', case=False, na=False)]

    if df_temas.empty: df_temas = df
    if df_demo.empty: df_demo = df

    # --- INDICADORES ESTILO ACUERDO OFICIAL ---
    fila_kpis = dbc.Row([
        crear_tarjeta_estilo_acuerdo("Población Impactada Total", f"{total_ben:,}", "Ciudadanos atendidos en el periodo", "bi bi-people-fill", GUINDA_INST),
        crear_tarjeta_estilo_acuerdo("Recursos e Inversión", f"${total_inv:,.2f}", "Presupuesto o apoyos gestionados", "bi bi-currency-dollar", DORADO_INST),
        crear_tarjeta_estilo_acuerdo("Ejes Operativos Activos", str(df[col_var[0]].nunique()), "Líneas de acción e indicadores clave", "bi bi-diagram-3-fill", "#374151"),
        crear_tarjeta_estilo_acuerdo("Estatus de Gestión", "100%", "Porcentaje de cumplimiento de metas", "bi bi-check-all", "#10b981"),
    ], className="mb-4")

    # --- GRÁFICA 1: ANÁLISIS DE ATENCIÓN (Barras Horizontales Institucionales) ---
    fig_prog = go.Figure()
    if not df_temas.empty:
        df_plot_temas = df_temas.groupby(col_act[0])[col_ben[0]].sum().sort_values(ascending=True).reset_index()
        fig_prog = px.bar(df_plot_temas, x=col_ben[0], y=col_act[0], orientation='h',
                          text_auto=True, color_discrete_sequence=[GUINDA_INST])
        fig_prog.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=40, t=10, b=10), height=350,
            xaxis=dict(showgrid=True, gridcolor='#e5e7eb', title="Cantidad"),
            yaxis=dict(title="", tickfont=dict(size=10, color='#111827'))
        )

    # --- GRÁFICA 2: TENDENCIA TEMPORAL (Línea de Gobierno) ---
    fig_area = go.Figure()
    col_mes = [c for c in df.columns if 'MES' in c.upper()]
    if col_mes:
        df_mes = df.groupby(col_mes[0])[col_ben[0]].sum().reset_index()
        fig_area = px.line(df_mes, x=col_mes[0], y=col_ben[0], markers=True, color_discrete_sequence=[DORADO_INST])
        fig_area.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=20, r=20, t=20, b=20), height=350,
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor='#e5e7eb', title="")
        )

    # --- GRÁFICA 3: COMPOSICIÓN DEMOGRÁFICA (Dona Institucional) ---
    fig_com = go.Figure()
    if not df_demo.empty:
        df_plot_demo = df_demo.groupby(col_act[0])[col_ben[0]].sum().reset_index()
        fig_com = px.pie(df_plot_demo, values=col_ben[0], names=col_act[0], 
                         hole=.4, color_discrete_sequence=COLORS_GOV)
        fig_com.update_layout(
            showlegend=True, margin=dict(t=10, b=10, l=10, r=10), height=380,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )

    return html.Div([
        # Sección de "Acuerdos" (KPIs)
        fila_kpis,
        
        # Bloques de Gráficos con cabeceras institucionales sólidas
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("DISTRIBUCIÓN POR LÍNEA DE ATENCIÓN", style={
                    'backgroundColor': GUINDA_INST, 'color': 'white', 'padding': '12px 16px',
                    'fontWeight': '700', 'fontSize': '0.85rem', 'borderRadius': '8px 8px 0 0', 'letterSpacing': '0.5px'
                }),
                html.Div(dcc.Graph(figure=fig_prog, config={'displayModeBar': False}), style={'padding': '15px'})
            ], className="bg-white border shadow-sm", style={'borderRadius': '8px', 'borderColor': '#e5e7eb'}), md=6),
            
            dbc.Col(html.Div([
                html.Div("EVOLUCIÓN MENSUAL DE SOLICITUDES", style={
                    'backgroundColor': '#374151', 'color': 'white', 'padding': '12px 16px',
                    'fontWeight': '700', 'fontSize': '0.85rem', 'borderRadius': '8px 8px 0 0', 'letterSpacing': '0.5px'
                }),
                html.Div(dcc.Graph(figure=fig_area, config={'displayModeBar': False}), style={'padding': '15px'})
            ], className="bg-white border shadow-sm", style={'borderRadius': '8px', 'borderColor': '#e5e7eb'}), md=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("COMPOSICIÓN Y SEGMENTACIÓN CIUDADANA DEL PADRÓN", style={
                    'backgroundColor': '#1f2937', 'color': 'white', 'padding': '12px 16px',
                    'fontWeight': '700', 'fontSize': '0.85rem', 'borderRadius': '8px 8px 0 0', 'letterSpacing': '0.5px'
                }),
                html.Div(dcc.Graph(figure=fig_com, config={'displayModeBar': False}), style={'padding': '15px', 'paddingBottom': '40px'})
            ], className="bg-white border shadow-sm", style={'borderRadius': '8px', 'borderColor': '#e5e7eb'}), md=12),
        ])
    ], style={'backgroundColor': '#f9fafb', 'padding': '5px'})

def seccion_impacto_layout():
    """Estructura base del panel con diseño del Plan Municipal de Desarrollo"""
    return html.Div([
        # Divisor sutil institucional
        html.Div(style={'borderTop': f'3px solid {DORADO_INST}', 'width': '80px', 'margin': '40px 0 20px 15px'}),
        
        html.Div([
            html.H3("SISTEMA DE EVALUACIÓN Y RENDICIÓN DE CUENTAS", 
                    style={'color': GUINDA_INST, 'fontWeight': '900', 'letterSpacing': '0.3px', 'fontSize': '1.4rem'}),
            html.P("Evidencia analítica de metas alcanzadas y cobertura institucional por área.", 
                   style={'color': GRIS_TEXTO, 'fontSize': '0.85rem', 'marginBottom': '30px'}),
        ], className="px-3"),

        # Contenedor dinámico donde se inyectan las tarjetas estilo acuerdos y gráficos
        html.Div(id='contenedor-graficas-impacto')
    ], className="mt-2")
