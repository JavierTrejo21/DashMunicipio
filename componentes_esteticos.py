import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

# --- NUEVA PALETA INSTITUCIONAL V4 ---
GUINDA = "#7A1E3D"
GUINDA_DARK = "#5A1530"
GOLD = "#B5892C"
VERDE = "#136F63"
VERDE_DARK = "#0C5148"
BG_APP = "#EFEDE6"
INK = "#241E1B"

def generar_banner_institucional(titulo_principal="SISTEMA DE GESTIÓN MUNICIPAL", subtitulo="PbR - PMD"):
    """Genera el banner institucional superior V4."""
    return html.Div([
        html.Div([
            html.I(className="bi bi-bank me-2", style={'color': GOLD}),
            html.Span(titulo_principal, style={'fontWeight': '700', 'letterSpacing': '0.5px'}),
            html.Span(" | ", style={'margin': '0 10px', 'opacity': '0.6'}),
            html.Span(subtitulo, style={'fontWeight': '400', 'fontSize': '0.9em', 'opacity': '0.9'})
        ], style={'display': 'flex', 'alignItems': 'center', 'fontSize': '0.95rem'})
    ], style={
        'backgroundColor': GUINDA,
        'color': 'white',
        'padding': '12px 24px',
        'borderBottom': f'3px solid {GOLD}',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    })

def generar_bloque_encabezado_area(nombre_eje, clave_area, nombre_area, icono_clase="ti ti-briefcase", resumen_texto="Área operativa integrada en los acuerdos del Plan Municipal de Desarrollo."):
    """Genera el bloque completo de cabecera de área y resumen estratégico (Breadcrumbs eliminados)."""
    return html.Div([
        # Tarjeta encabezado del área
        html.Div([
            html.Div(html.I(className=icono_clase), className="area-header-badge"),
            html.Div([
                html.Div("Área administrativa", className="area-header-eyebrow"),
                html.Div(f"{clave_area} · {nombre_area}", className="area-header-title")
            ])
        ], className="area-header-card"),

        # Tarjeta resumen estratégico
        html.Div([
            html.Div([
                html.I(className="ti ti-pin"),
                html.Div([
                    html.Div("Resumen estratégico", className="summary-eyebrow"),
                    html.Div(resumen_texto, className="summary-text")
                ])
            ], className="summary-row pin"),
            html.Div([
                html.I(className="ti ti-target-arrow"),
                html.Div([
                    html.Div("Objetivo general", className="summary-eyebrow"),
                    html.Div([html.B("Seguimiento y evaluación continua"), " de los indicadores sectoriales."], className="summary-text")
                ])
            ], className="summary-row goal")
        ], className="summary-card"),

        # Título de sección
        html.Div([
            html.Div(className="section-title-bar"),
            html.Div("Sistema de evaluación y rendición de cuentas", className="section-title")
        ], className="section-title-row")
    ])


def generar_breadcrumbs(nombre_eje, nombre_area):
    """Genera la navegación jerárquica (Vaciado para no mostrarse)."""
    return html.Div()

def generar_header_area_v4(nombre_area, icono="bi-briefcase"):
    """Genera la tarjeta de encabezado con badge circular."""
    return html.Div([
        html.Div([
            html.I(className=f"bi {icono}")
        ], className="area-header-badge"),
        html.Div([
            html.Div("ÁREA ADMINISTRATIVA", className="area-header-eyebrow"),
            html.Div(nombre_area, className="area-header-title playfair")
        ])
    ], className="area-header-card")

def generar_summary_card_v4(resumen, objetivo):
    """Genera la tarjeta de resumen estratégico y objetivo."""
    return html.Div([
        html.Div([
            html.I(className="bi bi-pin-angle-fill"),
            html.Div([
                html.Div("Resumen estratégico", className="summary-eyebrow"),
                html.Div(resumen, className="summary-text")
            ])
        ], className="summary-row pin"),
        html.Div([
            html.I(className="bi bi-target"),
            html.Div([
                html.Div("Objetivo general", className="summary-eyebrow"),
                html.Div([html.B("Seguimiento y evaluación continua"), f" {objetivo}"], className="summary-text")
            ])
        ], className="summary-row goal")
    ], className="summary-card")

def generar_titulo_seccion_v4(titulo):
    """Genera el título de sección con barra de acento verde."""
    return html.Div([
        html.Div(className="section-title-bar"),
        html.Div(titulo, className="section-title")
    ], className="section-title-row")

def crear_tarjeta_estilo_acuerdo(titulo, valor, subtitulo, icono_class, color_borde):
    """KPIs con el nuevo estilo de tarjetas limpias V4."""
    return dbc.Col(
        html.Div([
            # Barra lateral de color
            html.Div(style={
                'width': '4px', 'backgroundColor': color_borde, 'borderRadius': '4px 0 0 4px',
                'position': 'absolute', 'top': '15px', 'bottom': '15px', 'left': '0'
            }),
            
            html.Div([
                # Icono circular suave
                html.Div([
                    html.I(className=f"bi {icono_class}", style={'color': color_borde, 'fontSize': '1.2rem'}),
                ], style={
                    'width': '42px', 'height': '42px', 'backgroundColor': f"{color_borde}15", 
                    'borderRadius': '50%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center',
                    'marginRight': '15px'
                }),
                
                # Textos
                html.Div([
                    html.Div(titulo, style={
                        'color': '#9B928C', 'fontWeight': '700', 'fontSize': '0.65rem', 
                        'textTransform': 'uppercase', 'letterSpacing': '0.8px'
                    }),
                    html.Div(subtitulo, style={'color': INK, 'fontWeight': '700', 'fontSize': '0.85rem'})
                ], className="flex-grow-1"),
                
                # Valor destacado
                html.Div([
                    html.Div(valor, style={
                        'color': INK, 'fontWeight': '800', 'fontSize': '1.5rem', 'lineHeight': '1'
                    })
                ], className="ps-3")
            ], className="d-flex align-items-center p-3")
            
        ], className="bg-white shadow-sm position-relative mb-3", style={
            'borderRadius': '8px', 'border': '1px solid #E3DDD2', 'overflow': 'hidden'
        }),
        lg=4, md=6, xs=12
    )

def generar_tabla_gestion(df):
    """Construye el DataTable con el estilo institucional V4."""
    return html.Div([
        dash_table.DataTable(
            id='main-table', 
            data=df.to_dict('records'),
            columns=[{"name": i.upper(), "id": i, "editable": (i != 'rowid')} for i in df.columns],
            row_deletable=True, 
            page_size=10, 
            editable=True, 
            filter_action="native",
            sort_action="native",
            style_header={
                'backgroundColor': GUINDA, 
                'color': 'white', 
                'fontWeight': '700', 
                'fontSize': '11px', 
                'padding': '12px',
                'textTransform': 'uppercase',
                'border': f'1px solid {GUINDA_DARK}'
            },
            style_data={
                'backgroundColor': 'white', 
                'color': INK,
                'fontSize': '12px', 
                'padding': '10px 12px',
                'border': '1px solid #F2EFE9'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#FAF8F4'},
                {'if': {'state': 'active'}, 'backgroundColor': '#E5F3F0', 'border': f'1px solid {VERDE}'}
            ],
            style_table={
                'overflowX': 'auto', 
                'borderRadius': '8px', 
                'border': '1px solid #E3DDD2',
                'marginBottom': '20px'
            },
            css=[{
                'selector': '.dash-spreadsheet td div',
                'rule': 'line-height: 1.2;'
            }]
        )
    ], className="shadow-sm")