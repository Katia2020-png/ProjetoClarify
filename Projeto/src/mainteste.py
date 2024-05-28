import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash
import dash_bootstrap_components as dbc

from dash_bootstrap_templates import ThemeSwitchAIO
from dash.dependencies import Input, Output
from dash import html, dcc, Input, Output

# configurando cores para os temas

dark_theme = 'darkly'
vapor_theme = 'vapor'
url_dark_theme = dbc.themes.DARKLY
url_vapor_theme = dbc.themes.VAPOR

# --------------------------------------Importando os dados--------------------------
df = pd.read_csv('src/data/dataset_comp.csv')

df['dt_Venda'] = pd.to_datetime(df['dt_Venda'])
df['Mes'] = df['dt_Venda'].dt.strftime('%b').str.upper()


# ---------------------------------------------------------------


# ---------------------------Listas------------------------------------
lista_clientes = []

for cliente in df['Cliente'].unique():
    lista_clientes.append({
        'label': cliente,
        'value': cliente
    })

lista_clientes.append({'label': 'Todos os Clientes',
                       'value': 'Todos_clientes'
                        })

meses_br = dict(
    JAN="JAN",
    FEB="FEV",
    MAR="MAR",
    APR="ABR",
    MAY="MAI",
    JUN="JUN",
    JUL="JUL",
    AGO="AGO",
    SEP="SET",
    OCT="OUT",
    NOV="NOV",
    DEC="DEZ"
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

# Criando lista de categorias

lista_categorias = []
for categoria in df['Categorias'].unique():
    lista_categorias.append({
        'label': categoria,
        'value': categoria
    })
lista_categorias.append({
    'label': 'Todas as categoria',
    'value': "todas_categorias"

})

# criando app

app = dash.Dash(__name__)
#deploy
server = app.server

# -----------------layout---------------------------------
layout_titulo = html.Div([

    html.Div(  # caixa de seleçao dropdown
        dcc.Dropdown(
            id='dropdown_cliente',
            options=lista_clientes,
            placeholder="Selcione um Cliente",
            style={
                'background-color': 'transparent',
                'border': 'none',
                'color': 'black'}
        ), style={'width': '25%'}

    ),

    html.Div(
        html.Legend('Ebony Store',
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
],
    style={
    'text-align': 'center',
    'display': 'flex',
    'justfy-content': 'space-around',
    'align-items': 'center',
    'margin-top': '5px'


})

layout_linha01 = html.Div([
    html.Div([
        html.H4(id='output_cliente'),
        dcc.Graph(id='visual01')
    ], style={
        'width': '65%'

    }),

    html.Div([
        dbc.Checklist(
            id='radio_mes',
            options=lista_meses,
            inline=True
        ),
        dbc.RadioItems(
            id='radio_categorias',
            options=lista_categorias,
            inline=True
        )

    ], style={'width': '30%',
              'display': 'flex',
              'flex-direction': 'column',
              'justify-content': 'space-around'

              })

], style={

    'display': 'flex',
    'justify-content': 'space-around',
    'magin-top': '25px',
    'height': '300px'

})

layout_linha02 = html.Div([

    html.Div([
        html.H4('Vendas por Mês e lojas /Cidades'),
        dcc.Graph(id='visual02')
    ], style={
        'width': '60%',
        'text-align': 'center'
    }),

    html.Div(
        dcc.Graph(id='visual03'), style={'width': '35%'}

    )
], style={
    'display': 'flex',
    'justify-content': 'space-around',
    'margin-top': '40px',
    'heigth': '150px'
})
# -----carregando layout--------------------------------

app.layout = html.Div([
    layout_titulo,
    layout_linha01,
    layout_linha02,
])

# Funçoes de apoio-----------------------------------


def filtro_cliente(cliente_selecionado):
    if cliente_selecionado is None:
        return pd.Series(True, index=df.index)
    return df['Cliente'] == cliente_selecionado


def filtro_categoria(categoria_selecionada):
    if categoria_selecionada is None:
        return pd.Series(True, index=df.index)
    elif categoria_selecionada == 'todas_categorias':
        return pd.Series(True, index=df.index)
    return df['Categorias'] == categoria_selecionada


def filtro_mes(mes_selecionado):
    if not mes_selecionado:
        return pd.Series(True, index=df.index)

    elif 'ano_completo' in mes_selecionado:
        return pd.Series(True, index=df.index)

    else:
        return df['Mes'].isin(mes_selecionado)


# -----callback--------------------------------

@app.callback(
    Output('output_cliente', 'children'),
    [
        Input('dropdown_cliente', 'value'),
        Input('radio_categorias', 'value')
    ]
)
def atualizar_texto(cliente_selecionado, categoria_selecionada):
    if cliente_selecionado and categoria_selecionada:
        return f'Top5 {categoria_selecionada} | Cliente: {cliente_selecionado}'
    elif cliente_selecionado:
        return f'Top5 Produtos | Cliente: {cliente_selecionado}'
    elif categoria_selecionada:
        return f'Top5 {categoria_selecionada}'

    return 'Top5 Categorias'


@app.callback(
    Output('visual01', 'figure'),
    [
        Input('dropdown_cliente', 'value'),
        Input('radio_mes', 'value'),
        Input('radio_categorias', 'value'),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value")

    ]
)
def visual01(cliente, mes, categoria, toggle):
    template = vapor_theme if toggle else dark_theme

    nome_cliente = filtro_cliente(cliente)
    nome_categoria = filtro_categoria(categoria)
    nome_mes = filtro_mes(mes)

    cliente_mes_categoria = nome_cliente & nome_categoria & nome_mes
    df_filtrado = df.loc[cliente_mes_categoria]

    df_grupo = df_filtrado.groupby(['Produto', 'Categorias'])['Total Vendas'].sum().reset_index()
    df_top5 = df_grupo.sort_values(by="Total Vendas", ascending=False).head(5)

    # Criando o grafico
    fig = px.bar(
        df_top5,
        x='Produto',
        y="Total Vendas",
        color='Total Vendas',
        text="Total Vendas",
        color_continuous_scale='blues',
        height=280,
        template=template

    )
    return fig


@app.callback(
    [
        Output('visual02', 'figure'),
        Output('visual03', 'figure')
    ],
    [
        Input('radio_mes', 'value'),
        Input('radio_categorias', 'value'),
        Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
    ]
)
def visual02_03(mes, categoria, toggle):
    # definindo o tema que foi escolhido
    template = vapor_theme if toggle else dark_theme

    # filgtrando apenas por mes
    nome_mes = filtro_mes(mes)
    nome_categoria = filtro_categoria(categoria)

    # combinado os filtros
    mes_categoria = nome_mes & nome_categoria
    # Filtrando o dataframe
    df2 = df.loc[nome_categoria]
    df3 = df.loc[mes_categoria]

    # gerando analise de dadados

    df_vendasmesloja02 = df2.groupby(['Mes', 'Loja'])['Total Vendas'].sum().reset_index()

    df_vendasmesloja03 = df3.groupby(['Mes', 'Loja'])['Total Vendas'].sum().reset_index()

    # normalizar o tam.maanho das bolhas

    max_size = df_vendasmesloja02['Total Vendas'].max()
    min_size = df_vendasmesloja02['Total Vendas'].min()

    # definir as cores para cada loja

    cores_lojas = {
        'Rio de janeiro': 'green',
        'Salvador': 'blue',
        'Santos': 'yellow',
        'São Paulo': 'red',
        'Três Rios': 'cyan'
    }

    # Definir a ordem dos meses
    ordem_meses = [
        'JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN',
        'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'
    ]

    fig2 = go.Figure()

    for loja in df_vendasmesloja02['Loja'].unique():
        df_loja = df_vendasmesloja02[df_vendasmesloja02['Loja'] == loja]
        cor = cores_lojas.get(loja, 'black')

        fig2.add_trace(
            go.Scatter(
                x=df_loja['Mes'],
                y=df_loja['Total Vendas'],
                mode='markers',

                marker=dict(
                    color=cor,
                    size=(df_loja['Total Vendas'] - min_size) /
                         (max_size - min_size) * 50,

                    opacity=0.5,
                    line=dict(color=cor, width=0)

                ), name=str(loja)

            )
        )
    # Criando o visual 03
    fig3 = go.Figure(data=go.Scatterpolar(

        r=df_vendasmesloja03['Total Vendas'],
        theta=df_vendasmesloja03['Loja'],
        fill='toself',
        line=dict(color='rgba(31,119,180)'),
        marker=dict(color='rgb(31,110,180)', size=8),
        opacity=0.7

    ))
    return fig2, fig3


# subindo o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
