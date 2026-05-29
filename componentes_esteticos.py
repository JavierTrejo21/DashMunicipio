import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

# --- PALETA INSTITUCIONAL - GOBIERNO DEL ESTADO DE HIDALGO ---
GUINDA_INST = "#691c32"      # Color principal institucional
DORADO_INST = "#bc955c"      # Color de acento de gobierno
GRIS_CONTRASTE = "#374151"   # Encabezados secundarios
GRIS_FONDO_TABLA = "#f9fafb" # Fondo intercalado (Zebra)
GRIS_TEXTO = "#4b5563"       # Texto secundario legible

DICCIONARIO_AREAS = {
    "DIF_DESAYUNOS_ESCOLARES": {
        "resumen": "Programa de asistencia alimentaria básica para menores en edad escolar en zonas de alta vulnerabilidad.",
        "objetivo": "Reducir la inseguridad alimentaria mediante raciones diarias y vigilancia nutricional."
    },
    "ATENCION_A_ADULTOS_MAYORES": {
        "resumen": "Servicios de salud, integración social y seguimiento preventivo para la población de la tercera edad.",
        "objetivo": "Fomentar el envejecimiento activo y digno a través de terapias, visitas y apoyos directos."
    },
    "COMERCIO_E_INGRESOS": {
        "resumen": "Regularización y fomento de la actividad económica local y control de recaudación por giros comerciales.",
        "objetivo": "Ordenamiento del comercio formal e informal para fortalecer los ingresos propios municipales."
    }
}

def crear_tarjeta_acuerdo_institucional(id_acuerdo, nombre_acuerdo, porcentaje_avance=85):
    """
    Replica del formato estético de cuadrícula del portal de planeación.
    Caja gris claro con bordes redondeados, sombra difuminada e icono envuelto en anillo perimetral.
    """
    # Mapeo inteligente de iconos según palabras clave detectadas en el nombre del Acuerdo/Eje
    icono_eje = "bi-people-fill"
    nombre_upper = nombre_acuerdo.upper()
    if "BIENESTAR" in nombre_upper or "SOCIAL" in nombre_upper:
        icono_eje = "bi-heart-pulse-fill"
    elif "ECONÓMICO" in nombre_upper or "DESARROLLO" in nombre_upper or "INGRESOS" in nombre_upper:
        icono_eje = "bi-cash-coin"
    elif "SOSTENIBLE" in nombre_upper or "INFRAESTRUCTURA" in nombre_upper or "OBRA" in nombre_upper:
        icono_eje = "bi-building-gear"
    elif "TRANSPARENCIA" in nombre_upper or "ANTICORRUPCIÓN" in nombre_upper:
        icono_eje = "bi-shield-check"
    elif "PARTICIPATIVO" in nombre_upper or "GOBIERNO" in nombre_upper or "MUNICIPIO" in nombre_upper:
        icono_eje = "bi-person-workspace"

    return dbc.Col(
        html.Div([
            # 1. Anillo perimetral de avance (Diseñado con conic-gradient sobre el fondo)
            html.Div([
                # Contenedor del icono interno
                html.Div([
                    html.I(className=f"bi {icono_eje}", style={
                        'color': 'white', 
                        'fontSize': '1.25rem',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    })
                ], style={
                    'width': '50px',
                    'height': '50px',
                    'backgroundColor': GUINDA_INST,
                    'borderRadius': '50%',
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'zIndex': '2'
                })
            ], style={
                'width': '64px',
                'height': '64px',
                'borderRadius': '50%',
                'background': f'conic-gradient(#a61c3c {porcentaje_avance}%, #e5e7eb 0)', 
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'margin': '0 auto 15px auto',
                'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
            }),
            
            # 2. Texto Descriptivo del Acuerdo
            html.P(nombre_acuerdo.lower(), style={
                'color': '#1f2937', 
                'fontSize': '0.82rem', 
                'fontWeight': '600',
                'lineHeight': '1.3',
                'minHeight': '45px',
                'margin': '0 0 12px 0',
                'textTransform': 'capitalize',
                'textAlign': 'center'
            }),
            
            # 3. Porcentaje de Cumplimiento Inferior
            html.H6(f"{porcentaje_avance}%", style={
                'color': '#111827', 
                'fontWeight': '800', 
                'fontSize': '0.95rem',
                'margin': '0',
                'textAlign': 'center'
            }),
            
            # 4. Botón transparente absoluto para capturar el click en toda la superficie de la tarjeta
            dbc.Button(
                "Seleccionar", 
                id={'type': 'btn-acuerdo', 'index': id_acuerdo}, 
                style={
                    'position': 'absolute', 'top': '0', 'left': '0', 
                    'width': '100%', 'height': '100%', 'opacity': '0', 'cursor': 'pointer'
                }
            )
            
        ], className="position-relative p-4 mb-4 shadow-sm", style={
            'backgroundColor': '#e9ecef', 
            'borderRadius': '16px',        
            'border': '1px solid rgba(0,0,0,0.02)',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'space-between',
            'minHeight': '190px'
        }),
        xs=12, sm=6, md=4, lg=3, className="d-flex align-items-stretch"
    )

def generar_banner_institucional(nombre_area, tabla):
    """Genera el encabezado con la identidad institucional del municipio y el área."""
    info_est = DICCIONARIO_AREAS.get(tabla, {
        "resumen": "Área operativa de la administración municipal encargada de la gestión de indicadores locales.",
        "objetivo": "Cumplimiento de las metas establecidas dentro del Plan Municipal de Desarrollo vigente."
    })
    
    return html.Div([
        html.Div([
            html.Div([
                html.I(className="bi bi-journal-check me-3", style={'fontSize': '1.4rem', 'color': DORADO_INST}),
                html.Div([
                    html.H4("CONTROL DE COMPROMISOS Y EVALUACIÓN OPERATIVA", style={
                        'margin': '0', 'fontWeight': '800', 'fontSize': '1.05rem', 'letterSpacing': '0.5px'
                    }),
                    html.P("Plan Municipal de Desarrollo - Rendición de Cuentas Cobertura Municipal", style={
                        'margin': '0', 'fontSize': '0.72rem', 'color': '#f3f4f6', 'opacity': '0.85'
                    })
                ])
            ], className="d-flex align-items-center")
        ], style={
            'backgroundColor': GUINDA_INST, 'color': 'white', 'padding': '16px 24px',
            'borderRadius': '8px 8px 0 0', 'borderBottom': f'4px solid {DORADO_INST}'
        }),

        html.Div([
            html.Div([
                html.H5("EJE / DIRECCIÓN SELECCIONADA", style={
                    'color': GUINDA_INST, 'fontWeight': '700', 'fontSize': '0.75rem', 'letterSpacing': '0.5px', 'marginBottom': '3px'
                }),
                html.H3(f"{nombre_area}", style={
                    'color': '#111827', 'fontWeight': '900', 'fontSize': '1.35rem', 'margin': '0', 'textTransform': 'uppercase'
                }),
                html.Hr(style={'margin': '15px 0', 'opacity': '0.1'}),
                
                html.P(info_est['resumen'], style={'color': '#4b5563', 'fontSize': '0.85rem', 'lineHeight': '1.5', 'marginBottom': '12px'}),
                
                html.Div([
                    html.Span("🎯 OBJETIVO ESTRATÉGICO: ", style={'fontWeight': 'bold', 'color': DORADO_INST, 'fontSize': '0.75rem'}),
                    html.Span(info_est['objective'] if 'objective' in info_est else info_est['objetivo'], style={'fontStyle': 'italic', 'color': '#4b5563', 'fontSize': '0.8rem'})
                ], style={'backgroundColor': '#f9fafb', 'padding': '8px 14px', 'borderRadius': '6px', 'borderLeft': f'3px solid {DORADO_INST}'})
            ], className="p-4")
        ], style={
            'backgroundColor': 'white', 'borderRadius': '0 0 8px 8px', 
            'borderLeft': '1px solid #e5e7eb', 'borderRight': '1px solid #e5e7eb', 'borderBottom': '1px solid #e5e7eb',
            'boxShadow': '0 4px 6px -1px rgba(0,0,0,0.02)'
        })
    ], className="mb-4")

def generar_tabla_gestion(df):
    """Construye el componente DataTable estilizado."""
    return html.Div([
        dash_table.DataTable(
            id='main-table', data=df.to_dict('records'),
            columns=[{"name": i.upper(), "id": i, "editable": (i != 'rowid')} for i in df.columns],
            row_deletable=True, page_size=5, editable=True, filter_action="native",
            style_header={
                'backgroundColor': GUINDA_INST, 'color': 'white', 
                'fontWeight': 'bold', 'fontSize': '0.85rem', 'padding': '10px'
            },
            style_data={
                'backgroundColor': 'white', 'color': '#374151',
                'fontSize': '0.82rem', 'padding': '8px 12px'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': GRIS_FONDO_TABLA},
                {'if': {'state': 'active'}, 'backgroundColor': '#f3f4f6', 'border': f'1px solid {DORADO_INST}'}
            ],
            style_table={
                'overflowX': 'auto', 'marginBottom': '40px',
                'borderRadius': '4px', 'border': '1px solid #e5e7eb'
            }
        )
    ])

def crear_tarjeta_estilo_acuerdo(titulo, valor, subtitulo, icono_class, color_borde):
    """Estructura visual para las tarjetas horizontales de KPI de Impacto."""
    return dbc.Col(
        html.Div([
            html.Div(style={
                'width': '6px', 'backgroundColor': color_borde, 'borderRadius': '4px 0 0 4px',
                'position': 'absolute', 'top': '0', 'bottom': '0', 'left': '0'
            }),
            html.Div([
                html.I(className=f"{icono_class}", style={'color': color_borde, 'fontSize': '1.6rem'}),
            ], style={'padding': '15px 20px', 'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.H5(titulo, style={
                    'color': '#1f2937', 'fontWeight': '700', 'fontSize': '0.95rem', 
                    'marginBottom': '2px', 'textTransform': 'uppercase', 'letterSpacing': '0.3px'
                }),
                html.P(subtitulo, style={'color': GRIS_TEXTO, 'fontSize': '0.75rem', 'margin': '0'})
            ], style={'flexGrow': '1', 'padding': '15px 10px', 'alignSelf': 'center'}),
            html.Div([
                html.Span(valor, style={
                    'color': '#111827', 'fontWeight': '800', 'fontSize': '1.4rem',
                    'backgroundColor': '#f9fafb', 'padding': '6px 14px', 'borderRadius': '8px',
                    'border': '1px solid #e5e7eb'
                })
            ], style={'padding': '15px 20px', 'display': 'flex', 'alignItems': 'center'})
        ], className="bg-white shadow-sm d-flex position-relative mb-3", style={
            'borderRadius': '8px', 'border': '1px solid #e5e7eb', 'overflow': 'hidden'
        }),
        md=6, xs=12
    )
