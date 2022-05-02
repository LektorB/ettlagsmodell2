import plotly.express as px
from dash import dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template  # Bruker bootstap-template i plotly grafene

sigma = 5.67E-8  # Stefan-Boltzmann konstant (W.m-2.K-4)
I_sol = 1361  #
tyk = 50  # 100% - piltykkelse

Template = 'flatly'  # bruk samme "theme" som under, men med småbokstaver
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name': 'viewport',  # skalering for mobil
                            'content': 'width=device-width, initial-scale=0.9'}]
                )
server = app.server
load_figure_template(Template)

# ---------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Ettlagsmodell av atmosfæren', style={'font-size': '2.5vw'},
                    className='text-center text-primary mb-4')
        ], width=12)
    ], justify='center'),

    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup(
                            [dbc.InputGroupText(u'Solarkonstanten, \u03A9  (W/m\u00B2)'),
                             dbc.Input(id='my_Omega', type='text', value='1361')],
                        )
                    ], lg=4, md=6, sm=8, xs=12, align="end"),
                    dbc.Col([
                        dbc.InputGroup([dbc.InputGroupText(u"Albedo, \u03B1"),
                                        dbc.Input(id='my_alpha', type='text', value='0.306')],
                                       )], lg=3, md=6, sm=4, xs=12, align="end"),
                    dbc.Col([
                        dbc.InputGroup(
                            [dbc.InputGroupText(u"Emissisivitet, \u03B5"),
                             dbc.Input(id='my_epsilon', type='text', value='0.77')],
                        )
                    ], lg=3, md=6, sm=8, xs=12, align="end"),

                    dbc.Col([
                        dbc.Button('Oppdater temperatur', id='modell_knapp', n_clicks=0, color="secondary",
                                   className="me-1"),
                        html.Div(id='output_state'),
                    ], lg=2, md=6, sm=4, xs=12, align="end")
                ])
            ])
        ], color="primary", inverse=True, class_name="mb-3")

    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='pil_graf', figure={}, mathjax=True)
            # , className='four columns')#,config={'staticPlot': True})
        ], class_name="mt-3")

    ])
])


# ------------------
@app.callback(
    Output(component_id='pil_graf', component_property='figure'),
    [Input(component_id='modell_knapp', component_property='n_clicks')],
    State(component_id='my_Omega', component_property='value'),
    State(component_id='my_alpha', component_property='value'),
    State(component_id='my_epsilon', component_property='value'),
)
def piler(klikk, omega, alfa, epsilon):
    omega = float(omega)
    alfa = float(alfa)
    epsilon = float(epsilon)
    temp = (((1 - alfa) * omega) / (4 * sigma * (1 - (epsilon / 2)))) ** (1 / 4)
    temp2 = temp / 2 ** 0.25

    u = sigma * temp ** 4
    u_atm = epsilon * sigma * temp2 ** 4
    skala = (4 * u / omega) * tyk
    skala2 = skala * (1 - epsilon)
    skala = skala * epsilon
    skala3 = (4 * u_atm / omega) * tyk

    fig = px.line(x=[0], y=[0])

    # sol
    fig.add_annotation(ax=0.7, axref='x', ay=2.2, ayref='y',
                       x=0.7, xref='x', y=0.68, yref='y',
                       arrowwidth=tyk, arrowhead=7, arrowsize=0.3, font=dict(size=16), text="$\\frac{\\Omega}{4}$",
                       arrowcolor="yellow", arrowside='none')

    fig.add_annotation(text='$\\frac{(1-\\alpha) \\Omega}{4}$', xref="x", yref="y", x=0.7, y=0.1, showarrow=False,
                       font=dict(size=16))

    if (1 - alfa) > 0.1:
        fig.add_annotation(ax=0.7 + alfa * 0.025, axref='x', ay=0.9, ayref='y',
                           x=0.7 + alfa * 0.025, xref='x', y=0.2, yref='y',
                           arrowwidth=tyk * (1 - alfa), startarrowhead=6, arrowhead=4, arrowsize=0.3,
                           font=dict(size=16), arrowcolor="yellow")

    if alfa > 0.1:
        fig.add_annotation(ax=0.5, axref='x', ay=2.2, ayref='y',
                           x=0.69, xref='x', y=0.60, yref='y', arrowside='start',
                           arrowwidth=alfa * tyk, arrowhead=6, startarrowhead=4, startarrowsize=0.3, font=dict(size=16),
                           text="$\\frac{\\alpha \\Omega}{4}$", arrowcolor="yellow", align='left')

    # jord
    if skala > 0.1:
        fig.add_annotation(ax=0.99, axref='x', ay=1.2, ayref='y',
                           x=0.99, xref='x', y=0.2, yref='y', arrowside='start',
                           arrowwidth=skala, startarrowhead=4, startarrowsize=0.3, font=dict(size=16), arrowcolor="red",
                           text='$\\epsilon\\sigma T_{j}^4$')

    if skala2 > 0.1:
        fig.add_annotation(ax=1.12, axref='x', ay=2.2, ayref='y',
                           x=1.01, xref='x', y=0.2, yref='y', arrowside='start',
                           arrowwidth=skala2, startarrowhead=4, startarrowsize=0.3, font=dict(size=16),
                           text="'$(1-\\epsilon)\\sigma T_{j}^4$'", arrowcolor="red", )

    fig.add_annotation(text='$\\sigma T_{j}^4$', xref="x", yref="y", x=0.99, y=0.1, font=dict(size=16), showarrow=False)

    # atmosfære
    if skala3 > 0.1:
        fig.add_annotation(ax=1.35, axref='x', ay=2.2, ayref='y',
                           x=1.35, xref='x', y=0.2, yref='y', arrowside='end+start',
                           arrowwidth=skala3, arrowhead=4, startarrowhead=4, startarrowsize=0.3, arrowsize=0.3,
                           font=dict(size=16), text="$\\epsilon \\sigma T_{a}^4$", arrowcolor="FireBrick", )

    fig.add_annotation(text='$\\epsilon \\sigma T_{a}^4$', xref="x", yref="y", x=1.35, y=0.1, font=dict(size=16),
                       showarrow=False)

    jord = (
            '$T_{j}=\\left(\\frac{(1-\\alpha)\\Omega)}{4\\sigma(1-\\frac{\\epsilon}{2})}\\right)^{\\frac{1}{4}}=\\text{'
            + str(round(temp, 1)) + ' K =' + str(round(temp - 273, 1)) + '} ^{\\circ}C$')
    atm = ('$T_{a}=\\frac{T_{j}}{\\sqrt[4]{2}} =\\text{' + str(round(temp2, 1)) + ' K =' + str(
        round(temp2 - 273, 1)) + '} ^{\\circ}C$')

    fig.add_annotation(
        text=jord,
        xref="x", yref="y",
        x=1.7, y=0.7,
        showarrow=False,
        font=dict(size=16),
    )

    fig.add_annotation(
        text=atm,
        xref="x", yref="y",
        x=1.7, y=1.7,
        showarrow=False,
        font=dict(size=16),
    )

    fig.update_layout(xaxis_range=[0.4, 2], yaxis_range=[0, 2], margin_l=0, margin_r=0)

    fig.add_hrect(y0=0, y1=0.2, fillcolor="DarkOliveGreen", opacity=0.5, layer="below", line_width=0)
    fig.add_hrect(y0=1, y1=1.4, fillcolor="lightblue", opacity=0.5, layer="above", line_width=0)
    fig.update_yaxes(showgrid=False, title=None, showticklabels=False)
    fig.update_xaxes(showgrid=False, title=None, showticklabels=False)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=50)
