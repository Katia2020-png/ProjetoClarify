import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash.dependencies import Input, Output
from dash import html, dcc, Input, Output


# Configurando cores para os temas
dark_theme = 'darkly'
vapor_theme = 'vapor'
url_dark_theme = dbc.themes.DARKLY
url_vapor_theme = dbc.themes.VAPOR



# -------------------- DADOS --------------------
# Importando dados
df = pd.read_csv('./src/data/dataset_comp.csv')
df['dt_Venda'] = pd.to_datetime(df['dt_Venda'])


# ------------------- LISTAS --------------------
lista_clientes = []
for cliente in df['Cliente'].unique():
    lista_clientes.append({
            'label': cliente, 
            'value': cliente
    })

lista_clientes.append({
    'label': 'Todos os Clientes', 
    'value': 'todos_clientes'
})

meses_br = dict(
    JAN = 'JAN',
    FEB = 'FEV',
    MAR = 'MAR',
    APR = 'ABR',
    MAY = 'MAI',
    JUN = 'JUN',
    JUL = 'JUL',
    AUG = 'AGO',
    SEP = 'SET',
    OCT = 'OUT',
    NOV = 'NOV', 
    DEC = 'DEZ'
)

lista_meses = []
for mes in df['Mes'].unique(): 
    mes_pt = meses_br.get(mes, mes)

    lista_meses.append({
        'label': mes_pt,
        'value': mes
    })

lista_meses.append({
    'label': 'Ano Completo',
    'value': 'ano_completo'
})



#Criando APP
app = dash.Dash(__name__)


# ------------------ LAYOUT ------------------
layout_titulo = html.Div([

    html.Div(
        dcc.Dropdown(
            id='dropdown_cliente',
            options=lista_clientes,
            placeholder= lista_clientes[-1]['label'],
            style={
                'background-color': 'transparent',
                'border': 'none',
                'color': 'black'
            }
        ), style={'width': '25%'}
    ),

    html.Div(
        html.Legend(
            'Ebony Store',
            style={
                'font-size': '150%',
                'text-align': 'center'
            }
        ), style={'width': '50%'}
    ),

    html.Div(
        ThemeSwitchAIO(
            aio_id='theme',
            themes=[
                url_dark_theme,
                url_vapor_theme
            ]
        ), style={'width': '25%'}
    )
], style={
    'text-align': 'center',
    'display': 'flex',
    'justify-content': 'space-around',
    'align-items': 'center',
    'font-family': 'Fira Code',
    'margin-top': '20px'
})

layout_linha01 = html.Div([
    
    html.Div([
        html.H4(id='output_cliente'),
        dcc.Graph(id='visual01')
    ], style={
        'width': '65%'
    }),

    html.Div([
        dbc.RadioItems(
            id='radio_mes',
            options=lista_meses,
            inline=True
        )

    ], style={
        'width': '30%',
        'display': 'flex',
        'flex-direction': 'column',
        'justify-content': 'space-evenly'
    })

], style={
    'display': 'flex',
    'justify-content': 'space-around',
    'margin-top': '25px',
    'height': '300px'
})


# Carregando layout
app.layout = html.Div([
    layout_titulo,
    layout_linha01
])




# ------------------ CALLBACKS ------------------
@app.callback(
    Output('output_cliente', 'children'),
    Input('dropdown_cliente', 'value')
)
def atualizar_texto(cliente_selecionado):
    if cliente_selecionado:  
        return f'TOP5 Produtos | Cliente: {cliente_selecionado}'
    else:
        return f'TOP5 Categorias'








# Subindo servidor
if __name__ == '__main__':
    app.run_server(debug=True)