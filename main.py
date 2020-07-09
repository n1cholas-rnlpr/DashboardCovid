#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 02:56:02 2020

@author: n1cholas-rnlpr
"""
import os
import numpy as np
import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.0)
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

import dash             #(version 1.8.0)
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_renderer
#from dash_table.Format import Format
import dash_table.FormatTemplate as FormatTemplate
#from dash_table.Format import Sign
from dash.dependencies import Input, Output, State

import flask

from datetime import date, timedelta
import json
import time
import ssl

import visdcc

# from win32api import GetSystemMetrics
#
#
# app = QtGui.QApplication([])
# screen_resolution = app.desktop().screenGeometry()
# width = int(screen_resolution.width())
# height = int(screen_resolution.height())

#from flask import Flask
#from flask_caching import Cache

ssl._create_default_https_context = ssl._create_unverified_context
#import mapclassify

#df = pd.read_csv('df_temp.csv', decimal=',', delimiter=';')
#df.columns

#df['pop_60_perc'] = df['pop_60']/df['pop']
#df.drop(['pop', 'pop_60'], axis=1, inplace=True)

#today = date.today()
#today = pd.to_datetime('2020-07-01', format='%Y-%m-%d')

cod_rmc = [3501608, 3503802, 3509502, 3512803, 3515152, 3519055, 3519071,
           3520509, 3523404, 3524709, 3531803, 3532009, 3533403, 3536505,
           3537107, 3545803, 3548005, 3552403, 3556206, 3556701]
#dftable = df[df['datahora'] == today].groupby(by='nome_munic', sort=True).sum().reset_index()
# todo Implement weeks mean at incomplete weeks observations

# todo Implement weeks mean at incomplete weeks observations

df_missing_c = pd.read_csv('todas_cidades_sp.csv', sep=',') # DF to merge for missing cities

custom_colorscale_mortalidade = [
[0, 'rgb(209, 209, 209)'],
#[0, 'rgb(192, 171, 237)'],
#[0, 'rgb(214, 171, 237)'],
[0.5, 'rgb(126, 0, 122)'],
#[0.5, 'rgb(144, 0, 222)'],
[1, 'rgb(59, 0, 105)']]
#[1, 'rgb(85, 0, 130)']]

custom_colorscale_incidencia = [
[0, 'rgb(209, 209, 209)'],
[0.5, 'rgb(54, 161, 161)'],
[1, 'rgb(30, 61, 61)']]


roxo='#6400de'
#roxo='#9000de'
cyan='#36a1a1'


azul_observatorio = '#3f51b5'
azul_observatorio_rgb = 'rgb(63, 81, 181)'
azul_observatorio_footer = '#1a2130'

def unixTimeMillis(dt):
    # ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    #     ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix, unit='s')

def unixToDatetimeNoTime(unix):
    datetime_map_selector = pd.to_datetime(unix, unit='s')
    return datetime_map_selector.normalize()[0]

def getMarks(start, end, Nth=100):
    #     ''' Returns the marks for labeling.
    #         Every Nth value will be used.
    #     '''
    month = []
    result = {}
    for i, date in enumerate(daterange):
        if (i % Nth == 0):
            # Append value to dict
            month = date.month
            #result[unixTimeMillis(date)] = str(date.strftime('%d/%m/%y'))
            result[unixTimeMillis(date)] = str(date.strftime('%d/%m'))
        else:
            # Append value to dict
            #result[unixTimeMillis(date)] = str(date.strftime('%d'))
            result[unixTimeMillis(date)] = str(date.strftime('%d/%m'))

        if (date.month != month):
            #result[unixTimeMillis(date)] = str(date.strftime('%d/%m'))
            result[unixTimeMillis(date)] = str(date.strftime('%d/%m'))

        month = date.month

    return result


with open('geojs-35-mun.json', 'r') as json_file:
    gjson = json.load(json_file)

# #2f3e9b


css_directory = os.getcwd()
stylesheets = ['css_main.css']
static_css_route = '/static/'




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
locale_br_script = ['https://cdn.plot.ly/plotly-locale-pt-br-latest.js']
#external_stylesheets = ['css_dashboard.css']

#app = dash.Dash(__name__)
app = dash.Dash(__name__)#, external_stylesheets=external_stylesheets)#, external_scripts=locale_br_script)

pio.templates.default = "plotly_white"
server = app.server

# @app.server.route('{}<stylesheet>'.format(static_css_route))
# def serve_stylesheet(stylesheet):
#     if stylesheet not in stylesheets:
#         raise Exception(
#             '"{}" is excluded from the allowed static files'.format(
#                 stylesheet
#             )
#         )
#     return flask.send_from_directory(css_directory, stylesheet)
#
#
# for stylesheet in stylesheets:
#     app.css.append_css({"external_url": "/static/{}".format(stylesheet)})

# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache/',
# })


#Loading Stylesheet
#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})




tab_style = {
    'color': 'white',
    'primary': azul_observatorio_rgb,
    'background': azul_observatorio_rgb,
    'fontWeight': 'bold',
    #'padding': '11px 25px'
}

tab_style_selected = {
    'color': 'black',
    'primary': azul_observatorio_rgb,
    'background': 'white',
    'fontWeight': 'bold',
    #'padding': '11px 25px'
}

app.layout = html.Div(
    children=[
    dcc.Interval(id='update_trigger', disabled=False, interval=1800000, max_intervals=-1, n_intervals=0),
    html.Div([
        dcc.Tabs(id='region_tabs', value='RMC', children=[#style={'height': 50}, children=[
        dcc.Tab(label='REGIÃO METROPOLITANA DE CAMPINAS', value='RMC', style=tab_style, selected_style=tab_style_selected),
        dcc.Tab(label='DEPARTAMENTOS REGIONAIS DE SAÚDE', value='DRS', style=tab_style, selected_style=tab_style_selected),
        dcc.Tab(label='MUNICÍPIOS DE SÃO PAULO', value='SP', style=tab_style, selected_style=tab_style_selected),
        ], colors={
            'border': 'white',
            'primary': azul_observatorio_rgb,
            'background': azul_observatorio_rgb
        }),
    ], className= 'row'),
    #html.Br(),
    html.Div(className='row', children=[
        html.Button(children=' Imprimir / PDF ',n_clicks=0, id='button_print', className='two columns button_print'),
        html.Label(children='', id='label_last_update', className='two columns label_last_update', style={'fontSize': 14, 'margin': '0.7% 0px 0.7% 1.5%', 'color': '#d72a24', 'textAlign':'left'}),
        #html.Div(id='hidden_div_pdf', style={'display': 'none'}, children=[])
    ]),
    html.Div([
        html.Label(children='', id='label_ind', style={'fontSize': 14, 'margin': '0.5% 0px 1.5% 0.7%', 'font-weight': 'bold', 'textAlign':'left'}),
        html.Div(children=[

            dcc.Graph(id = 'today_indicators', config={'locale': 'pt-BR', 'displayModeBar': False})

            ], className = 'twelve columns ind_desktop'),

        html.Div(children=[
            html.Div([
                dcc.Graph(id = 'today_indicators_mr1', config={'locale': 'pt-BR', 'displayModeBar': False})
            ], style={'margin': '5% 0 0 0'}),
            html.Div([
                dcc.Graph(id = 'today_indicators_mr2', config={'locale': 'pt-BR', 'displayModeBar': False})
            ]),
            html.Div([
                dcc.Graph(id = 'today_indicators_mr3', config={'locale': 'pt-BR', 'displayModeBar': False})
            ]),
        ], className = 'twelve columns ind_mobile', id='mobile_ind_container'),
    #html.Br(),
    #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
        ], style={'backgroundColor': 'white'}, className= 'row rounded_border_blue '),
    html.Br(),

    html.Div([
        html.Div(className='row', children=[
           html.Div(className='one column button_filter_div', style={'width': '8.2%', 'margin': '0.5% 0 0 0.5%'}, children=[
               html.Button(children='Filtrar', n_clicks=0, id='apply_filter', style={'height': 36, 'width': '100%','backgroundColor': '#f0f1f4'})
           ]),
            html.Div(className='eleven columns table_filter_dropdown', style={'width': '90%','margin': '0.5% 0 0 0.7%'}, children=[
                dcc.Dropdown(
                    id='table_filter',
                    options=[],
                    value='',
                    searchable=True,
                    clearable=True,
                    multi=True,
                    placeholder='Filtro por localidade...',
                    style={'backgroundColor': '#f0f1f4'}
                ),
            ])
        ]),


        html.Label(children='', id='label_table', style={'fontSize': 14, 'font-weight': 'bold', 'marginLeft': '0.7%', 'textAlign': 'left', 'padding-top': '1%', 'padding-bottom': '1%'}),
        dash_table.DataTable(
            id='table',
            columns=[],
            data=[],
            locale_format={
                'decimal': ',',
                'group': '.',
                'separate_4digits': True
            },
            editable=False,
            filter_action='none',
            sort_action='native',
            sort_mode='single',
            fixed_rows={'headers': True},
            #row_selectable='multi',
            row_deletable=False,
            selected_columns=[],
            page_action='none', #old: native
            style_table={},
            #page_current=0,
            page_size=9,
            style_as_list_view=False,
            style_cell={
                'font-family': 'Arial',
                'minWidth': 95, 'maxWidth': 95, 'Width':95
            },
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': azul_observatorio_rgb,
                'color': 'white',
                'fontSize': 11,
                'whitespace': 'normal',
                'height': 'auto',
                'textAlign': 'left'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'nome_munic'},
                    'textAlign': 'left'
                },
                {
                    'if': {'column_id': 'nome_drs'},
                    'textAlign': 'left'
                },
            ],
            style_data={
                'whitespace': 'normal',
                'height': 'auto',
                'fontSize': 14
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(219, 223, 255)'
                }
            ],
            cell_selectable=False
            # css=[{
            #     'selector': 'td.cell--selected, td.focused',
            #     'rule': 'backgroundColor: #bac2ff'
            # }]
        ),
        html.Br(),
        html.Label('[1] Incidência: Número de casos confirmados por 100 mil habitantes. | [2] Mortalidade: Número de óbitos confirmados por 100 mil habitantes. | [3] Letalidade: Percentual do total óbitos em relação ao total de casos confirmados. | Obs: os filtros aplicados na tabela são aplicados também aos gráficos.', style={'fontSize':10, 'marginLeft': '0.5%', 'bottom': '0.5%'}),
        #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10})
    ], className='rounded_border_blue row white_bg'),
    html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
    html.Div([

        # First row
        html.Br(),
        html.Div([
            html.Div([
                visdcc.Run_js(id='javascript'),
                dcc.Loading(
                    id="loading_bargraph_novoscasos",
                    children=[dcc.Graph(id='bar_graph_novos_casos', config={'locale': 'pt-BR'})]
                    #type="graph"
                ),
            ], className='six columns'),

            html.Div([
                dcc.Loading(
                    id="loading_graph_casos",
                    children=[dcc.Graph(id='graph_casos', config={'locale': 'pt-BR'})]
                    #type="graph"
                ),
            ], className='six columns'),
            html.Br(),
            #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
        ], className='row rounded_border_blue white_bg'),
        html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
        html.Br(),
        html.Br(),

        # third row
        html.Div([

            html.Div([
                dcc.Loading(
                    id="loading_bargraph_novosobitos",
                    children=[dcc.Graph(id='bar_graph_novos_obitos', config={'locale': 'pt-BR'})]
                    #type="graph"
                ),
            ], className='six columns'),

            html.Div([
                dcc.Loading(
                    id="loading_graph_obitos",
                    children=[dcc.Graph(id='graph_obitos', config={'locale': 'pt-BR'})]
                    #type="graph"
                ),
            ], className='six columns'),
            html.Br(),
            #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
        ], className='row rounded_border_blue white_bg'),
        html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
        html.Br(),
        html.Br(),

        # second row
        html.Div([
            html.Div([
                html.Div([
                    html.Label('Selecione uma data para exibição nos mapas:', style={'marginLeft': '0.5%'}),
                    dcc.Slider(
                        id='map_slider',
                        #min=unixTimeMillis(daterange.min()),
                        #max=unixTimeMillis(daterange.max()),
                        step=None,
                        #value=unixTimeMillis(daterange.max()),
                        #marks=getMarks(daterange.min(), daterange.max()),
                        className='custom_slider'
                    )
                ], className='twelve columns')
            ], className='row'),

            html.Div([
                html.Div([
                    dcc.Loading(
                        id="loading_map_incidencia",
                        children=[dcc.Graph(id='map_incidencia',
                                            config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                    'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImageButton', 'lasso2d']})]
                        # type="graph"
                    )
                ], className='six columns'),

                html.Div([
                    dcc.Loading(
                        id="loading_map_mortalidade",
                        children=[dcc.Graph(id='map_mortalidade',
                                            config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                    'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImage', 'lasso2d']})]
                        # type="graph"
                    )
                ], className='six columns'),
                html.Br(),
                #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
            ], className='row'),
        ], className='rounded_border_blue white_bg'),
        html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
        html.Br(),
        html.Br(),
        html.Div(id='trigger_table_after_clear_filter', children=[], style={'display': 'none'}),


    ]),

    # html.Div([
    #     html.Div([
    #         html.Div([
    #             html.Label('Desenvolvimento | Nícholas R. Neves L. P. Ramos', style={'color': 'white'})
    #         ], className='row'),
    #         html.Div([
    #             html.Label('Equipe Técnica | Paulo Ricardo S. Oliveira e', style={'color': 'white'})
    #         ], className='row'),
    #         html.Div([
    #             html.Label('Felipe P. de Lima', style={'color': 'white'})
    #         ], className='row'),
    #         html.Br(),
    #         html.Br(),
    #         html.Div([
    #             html.Label('Contato | Prof. Paulo Ricardo S. Oliveira - paulo.oliveira@puc-campinas.edu.br', style={'color': 'white'})
    #         ], className='row')
    #     ], style={'background-color': azul_observatorio_footer, 'padding': '2.5% 0 2.5% 1%', 'margin': '0 0 0 0', 'width': '50%', 'height': '10%'},className='six columns'),
    #     html.Div([
    #         html.Div([
    #             html.Label('Fonte de dados: Fundação Sistema Estadual de Análise de Dados, 2020', style={'color': 'white'})
    #         ], className='row'),
    #         html.Br(),
    #         html.Div([
    #             html.Label('Mapas, gráficos e tabelas podem ser utilizados livremente, desde de que citada a fonte.', style={'color': 'white'})
    #         ], className='row'),
    #         html.Div([
    #             html.Label(children=['Citação sugerida: Ramos, N.L.P., Oliveira, P.R.S., Pedroso, F.L. Observatório PUC-Campinas: Painel Interativo Covid-19. Acessado em ' + str(pd.to_datetime('today').strftime('%d/%m/%Y')) + '.'], style={'color': 'white'})
    #         ], className='row'),
    #     ], style={'background-color': azul_observatorio_footer, 'padding': '2.5% 0 2.5% 1%', 'margin': '0 0 0 0', 'width': '50%', 'height': '10%'},className='six columns')
    # ], className='twelve columns row')
])


@app.callback(
    [Output('label_last_update', 'children'),
     Output('map_slider', 'min'),
     Output('map_slider', 'max'),
     Output('map_slider', 'value'),
     Output('map_slider', 'marks')],
    [Input('update_trigger', 'n_intervals')]
)

def update_data(n_intervals):

    today_timestamp = pd.to_datetime('today')
    today = pd.to_datetime('today', format='%Y-%m-%d')

    if n_intervals == 0:
        global last_update
        last_update = pd.to_datetime('2020-01-01')

    #if today_timestamp.hour >= 14 or n_intervals == 0:
    global df
    df = pd.read_csv("https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/dados_covid_sp.csv", sep=";", decimal=",")
    df = df.loc[:, ['datahora', 'nome_drs', 'nome_munic', 'codigo_ibge', 'casos', 'casos_novos', 'casos_pc', 'obitos',
                    'obitos_novos', 'obitos_pc', 'letalidade', 'pop', 'pop_60']]

    df.loc[:,'datahora'] = pd.to_datetime(df['datahora'], format="%Y-%m-%d")

    global daterange
    daterange = pd.date_range(start=df['datahora'].min(), end=df['datahora'].max(), freq='W-SAT')
    slider_min=unixTimeMillis(daterange.min())
    slider_max=unixTimeMillis(daterange.max())
    slider_value=slider_max
    slider_marks=getMarks(slider_min, slider_max)



    if df.loc[:,'datahora'].max() > last_update:
        df.loc[:,'casos_pc'] = df['casos_pc'].astype(int)  # todo check if we need one or two digits instead of a rounded int
        df.loc[:,'obitos_pc'] = df['obitos_pc'].astype(int)

        latest_data_table= df['datahora'].max()

        global df_gdate
        df_gdate = df.groupby(by=["nome_munic", "nome_drs", "codigo_ibge", "datahora"], sort=True).sum().reset_index(drop=False)

        global df_table_sp
        df_table_sp = df_gdate[df_gdate['datahora'] == latest_data_table]

        global dftc_ind
        dftc_ind = df_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(drop=False).sort_values('datahora')

        global df_rmc
        df_rmc = df[df['codigo_ibge'].isin(cod_rmc)]
        global df_rmc_gdate
        df_rmc_gdate = df_rmc.groupby(by=["nome_munic", "nome_drs", "codigo_ibge", "datahora"], sort=True).sum().reset_index(drop=False)
        global df_table_rmc
        df_table_rmc = df_rmc_gdate[df_rmc_gdate['datahora'] == latest_data_table]
        global dftcrmc_ind
        dftcrmc_ind = df_rmc_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(drop=False).sort_values('datahora')

        global df_drs_gdate
        df_drs_gdate = df.groupby(by=["nome_drs", "datahora"], sort=True).sum().reset_index(drop=False)
        global df_table_drs
        df_table_drs = df_drs_gdate[df_drs_gdate['datahora'] == latest_data_table]
        global df_drs_ind
        df_drs_ind = df_drs_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(drop=False).sort_values('datahora')  # todo having time: change drs indicators to update with dropdown


    #global last_update
    last_update= today_timestamp
    global latest_data
    latest_data= df['datahora'].max()
    first_string='Última atualização: '
    label_last_update= first_string + str(latest_data.strftime('%d/%m/%Y'))

    return label_last_update, slider_min, slider_max, slider_value, slider_marks

@app.callback(
    [Output('table_filter', 'value'),
     Output('trigger_table_after_clear_filter', 'children')],
    [Input('region_tabs', 'value')]
)
def clear_filter(value):
    return [''], []


@app.callback(
    [Output('table', 'data'),
    Output('table', 'columns'),
    Output('table', 'page_action'),
    Output('table', 'style_table'),
    Output('table_filter', 'options'),
    #Output('table_filter', 'value'),
    Output('label_ind', 'children'),
    Output('label_table', 'children')],
    [Input('label_last_update', 'children'),
     Input('region_tabs', 'value'),
     Input('apply_filter', 'n_clicks'),
     Input('trigger_table_after_clear_filter', 'children')],
    [State('table_filter', 'value')]
)
def build_table(label_last_update, region_tabs, n_clicks, trigger_table_after_clear_filter, selected_cities):
    # global dropdown_value
    # if dash.callback_context.triggered == ['region_tabs']:
    #     dropdown_value=""
    # else:
    #     dropdown_value=selected_cities

    columns = [{'name': 'Cidade', 'id': 'nome_munic', 'deletable': False, 'selectable': True, 'hideable': False},
               {'name': 'Casos Acumulados', 'id': 'casos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'}, #{'locale': {'group': '.', 'decimal': ','}, 'specifier': '.'}},
               {'name': 'Novos Casos', 'id': 'casos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
               {'name': 'Incidência [1]', 'id': 'casos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
               {'name': 'Óbitos Acumulados', 'id': 'obitos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
               {'name': 'Novos Óbitos', 'id': 'obitos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
               {'name': 'Mortalidade [2]', 'id': 'obitos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
               {'name': 'Letalidade [3]', 'id': 'letalidade', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(1)},
               {'name': 'População', 'id': 'pop', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
               {'name': 'População 60+', 'id': 'pop_60_perc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(1)}]

    if region_tabs == 'RMC':
        dropdown_options = [{'label': i, 'value': i}for i in df_table_rmc['nome_munic']]
        styletable = {'height': 300, 'overflowY': 'auto'}

        if selected_cities == ['']:
            dftable = df_table_rmc
        elif not selected_cities:
            dftable = df_table_rmc
        else:
            dftable = df_table_rmc[df_table_rmc['nome_munic'].isin(selected_cities)].reset_index(drop=True)
            styletable = {}


        pageaction = 'none'
        label_ind = 'Indicadores diários | Região Metropolitana de Campinas'
        label_table = 'Indicadores diários dos municípios da RMC'

    elif region_tabs == 'DRS':
        dropdown_options = [{'label': i, 'value': i} for i in df_table_drs['nome_drs']]
        styletable = {'height': 300, 'overflowY': 'auto'}

        columns = [{'name': 'Nome DRS', 'id': 'nome_drs', 'deletable': False, 'selectable': True, 'hideable': False},
                   {'name': 'Casos Acumulados', 'id': 'casos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
                   {'name': 'Novos Casos', 'id': 'casos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
                   {'name': 'Incidência [1]', 'id': 'casos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
                   {'name': 'Óbitos Acumulados', 'id': 'obitos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
                   {'name': 'Novos Óbitos', 'id': 'obitos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
                   {'name': 'Mortalidade [2]', 'id': 'obitos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
                   {'name': 'Letalidade [3]', 'id': 'letalidade', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(1)},
                   {'name': 'População', 'id': 'pop', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric'},
                   {'name': 'População 60+', 'id': 'pop_60_perc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(1)}]


        if selected_cities == ['']:
            dftable = df_table_drs
        elif not selected_cities:
            dftable = df_table_drs
        else:
            dftable = df_table_drs[df_table_drs['nome_drs'].isin(selected_cities)].reset_index(drop=True)
            styletable = {}

        pageaction = 'none'
        label_ind = 'Indicadores diários | Estado de São Paulo'
        label_table = 'Indicadores diários dos Departamentos Regionais de Saúde - SP'

    elif region_tabs == 'SP':
        dropdown_options = [{'label': i, 'value': i} for i in df_table_sp['nome_munic']]


        if selected_cities == ['']:
            dftable = df_table_sp
        elif not selected_cities:
            dftable = df_table_sp
        else:
            dftable = df_table_sp[df_table_sp['nome_munic'].isin(selected_cities)].reset_index(drop=True)

        pageaction = 'native'
        label_ind = 'Indicadores diários | Estado de São Paulo'
        label_table = 'Indicadores diários dos municípios paulistas'
        styletable = {}

    dftable.loc[:,'letalidade'] = dftable.loc[:,'obitos']/dftable.loc[:,'casos']
    dftable.loc[:,'pop_60_perc'] = dftable.loc[:,'pop_60']/dftable.loc[:,'pop']

    # global last_region_on_table_callback
    # last_region_on_table_callback = region_tabs
    #
    # if n_clicks == 0:
    #     global last_region_on_table_callback
    #     last_region_on_table_callback='first_display'

    # if region_tabs != last_region_on_table_callback:
    #     dropdown_value=['']
    # else:
    #     dropdown_value=region_tabs


    return dftable.to_dict('records'), columns, pageaction, styletable, dropdown_options, label_ind, label_table



@app.callback(
        [Output('bar_graph_novos_casos', 'figure'),
         Output('graph_casos', 'figure'),
         Output('bar_graph_novos_obitos', 'figure'),
         Output('graph_obitos', 'figure')],
        [Input('label_last_update', 'children'),
         Input('region_tabs', 'value'),
         Input('apply_filter', 'n_clicks'),
         Input('table', 'data')],
        [State('table_filter', 'value')]
)

#@cache.memoize(timeout=20)
def build_graphs(label_last_update, region_tabs, button, table_data_trigger_refresh, selected_cities):
    if region_tabs == 'RMC':
        dfplots = df_rmc_gdate.loc[:, ['datahora', 'nome_munic', 'casos_novos', 'casos', 'obitos_novos', 'obitos', 'casos_pc', 'obitos_pc', 'letalidade']]

    elif region_tabs == 'SP' or region_tabs == 'DRS':
        dfplots = df_gdate.loc[:, ['datahora', 'nome_munic', 'nome_drs', 'casos_novos', 'casos', 'obitos_novos', 'obitos', 'casos_pc', 'obitos_pc', 'letalidade']]

    if region_tabs != 'DRS':
        if not selected_cities:
            dfplots = dfplots
        elif selected_cities == ['']:
            dfplots = dfplots
        else:
            dfplots = dfplots[dfplots['nome_munic'].isin(selected_cities)].reset_index(drop=True)
    else:
        if not selected_cities:
            dfplots = dfplots
        elif selected_cities == ['']:
            dfplots = dfplots
        else:
            dfplots = dfplots[dfplots['nome_drs'].isin(selected_cities)].reset_index(drop=True)

    dfplots = dfplots.groupby(pd.Grouper(key='datahora', freq='W-SAT')).sum().sort_values('datahora').reset_index(drop=False)#.drop(19, axis=0)

    dfplots.loc[:,'letalidade'] = dfplots['obitos']/dfplots['casos']


    if dfplots['datahora'].max() > latest_data:
        dfplots = dfplots[:-1]

    fig_bar_novos_casos = px.bar(dfplots, x='datahora', y='casos_novos', hover_data={'casos_pc': True, 'letalidade': True})  # , labels = {'newCases': 'Novos casos', 'newDeaths':'Novos óbitos'})
    fig_bar_novos_casos.update_layout(title=dict(text='<b>Novos casos por semana de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1,
                      pad=dict(t=15, r=0, b=0, l=0)),
                      titlefont=dict(size=14),
                      xaxis_title="Semanas",
                      yaxis=dict(rangemode='nonnegative'),
                      yaxis_title="Novos casos",
                      hovermode='x unified',
                      margin=dict(l=0, r=0, t=60, b=0),
                      height=300)

    fig_bar_novos_casos.update_traces(hovertemplate='Novos casos: %{y}', marker_color=cyan)#azul_observatorio)
    #fig_bar_novos_casos.update_traces(hovertemplate='Novos casos: %{y}<br>Incidência: %{customdata[0]}<br>Letalidade: %{customdata[1]:.2%}', marker_color=cyan)#azul_observatorio)
    #     fig.update_yaxes(showspikes=True)

    fig_graph_casos = px.line(dfplots, x='datahora', y='casos', hover_data={'casos_pc': True, 'letalidade': True})  # , labels = {'newCases': 'Novos casos', 'newDeaths':'Novos óbitos'})
    #fig_graph_casos['data'][0]['line']['color'] = cyan#azul_observatorio
    #fig_graph_casos['data'][0]['line']['width'] = 3
    fig_graph_casos.update_layout(title=dict(text='<b>Casos acumulados por semana de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=15, r=0, b=0, l=0)),
                      titlefont=dict(size=14),
                      yaxis=dict(rangemode='nonnegative'),
                      xaxis_title="Semanas",
                      yaxis_title="Casos acumulados",
                      hovermode='x unified',
                      margin=dict(l=0, r=0, t=60, b=0),
                      height=300)

    fig_graph_casos.update_traces(mode="markers+lines", hovertemplate='Total de casos: %{y}', line=dict(color=cyan, width=3))

########### OBITOS
    fig_bar_novos_obitos = px.bar(dfplots, x='datahora', y='obitos_novos', hover_data={'obitos_pc': True, 'letalidade': True})  # , labels = {'newCases': 'Novos casos', 'newDeaths':'Novos óbitos'})
    fig_bar_novos_obitos.update_layout(title=dict(text='<b>Novos óbitos por semana de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=15, r=0, b=0, l=0)),
                             titlefont=dict(size=14),
                             yaxis=dict(rangemode='nonnegative'),
                             xaxis_title="Semanas",
                             yaxis_title="Novos óbitos",
                             hovermode='x unified',
                             margin=dict(l=0, r=0, t=60, b=0),
                             height=300)

    fig_bar_novos_obitos.update_traces(hovertemplate='Novos óbitos: %{y}', marker_color=roxo)#'#5dd4ff')#azul_observatorio)
    #fig_bar_novos_obitos.update_traces(hovertemplate='Novos óbitos: %{y}<br>Mortalidade: %{customdata[0]}<br>Letalidade: %{customdata[1]:.2%}', marker_color=roxo)#'#5dd4ff')#azul_observatorio)
    #     fig.update_yaxes(showspikes=True)

    fig_graph_obitos = px.line(dfplots, x='datahora', y='obitos', hover_data={'obitos_pc': True, 'letalidade': True})
    #fig_graph_obitos['data'][0]['line']['color'] = roxo #5dd4ff'#azul_observatorio
    #fig_graph_obitos['data'][0]['line']['width'] = 3
    fig_graph_obitos.update_layout(title=dict(text='<b>Óbitos acumulados por semana de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=15, r=0, b=0, l=0)),
                                  titlefont=dict(size=14),
                                  yaxis=dict(rangemode='nonnegative'),
                                  xaxis_title="Semanas",
                                  yaxis_title="Óbitos acumulados",
                                  hovermode='x unified',
                                  margin=dict(l=0, r=0, t=60, b=0),
                                  height=300)

    fig_graph_obitos.update_traces(mode="markers+lines", hovertemplate='Total de óbitos: %{y}', line=dict(color=roxo, width=3))
    #fig_graph_obitos.update_traces(mode="markers+lines", hovertemplate='Total de óbitos: %{y}<br>Mortalidade: %{customdata[0]}<br>Letalidade: %{customdata[1]:.2%}', line=dict(color=roxo, width=3))


    return fig_bar_novos_casos, fig_graph_casos, fig_bar_novos_obitos, fig_graph_obitos



@app.callback(
    [Output('map_incidencia', 'figure'),
     Output('map_mortalidade', 'figure')],
    [Input('label_last_update', 'children'),
     Input('region_tabs', 'value'),
     Input('map_slider', 'value'),
     Input('apply_filter', 'n_clicks'),
     Input('table', 'data')],
    [State('table_filter', 'value')]
)

#@cache.memoize(timeout=20)
def build_maps(label_last_update, region_tabs, map_slider, button, selected_cities, table_data_trigger_refresh):
    selected_date = unixToDatetime(map_slider)
    selected_date = selected_date.date()
    selected_date = pd.to_datetime(selected_date, format="%Y-%m-%d")

    df_missing_c_map = df_missing_c.loc[:,:]
    df_missing_c_map['datahora'] = selected_date
    #df_missing_c_map.insert(loc=2, column='datahora', value=selected_date)

    if region_tabs == 'RMC':
        dfmaps = df_rmc_gdate.loc[:, ['datahora', 'codigo_ibge', 'nome_munic', 'nome_drs', 'casos_pc', 'obitos_pc']]

    elif region_tabs == 'DRS' or region_tabs == 'SP':
        dfmaps = df_gdate.loc[:, ['datahora', 'codigo_ibge', 'nome_drs', 'nome_munic', 'casos_pc', 'obitos_pc']]

    if region_tabs == 'SP' or region_tabs == 'DRS':
        missing_cities = df_missing_c_map[~df_missing_c_map['codigo_ibge'].isin(dfmaps['codigo_ibge'])]
        dfmaps = pd.concat([dfmaps, missing_cities], sort=True, ignore_index=True)

    # if not selected_cities:
    #     dfmaps = dfmaps
    # elif selected_cities == ['']:
    #     dfmaps = dfmaps
    #
    #
    # if region_tabs == 'DRS':
    #         dfmaps = dfmaps[dfmaps['nome_drs'].isin(selected_cities)]
    #     else:
    #         dfmaps = dfmaps#[dfmaps['nome_munic'].isin(selected_cities)]

    # if region_tabs == 'DRS':
    #     if not selected_cities:
    #         dfmaps = dfmaps
    #     elif selected_cities == ['']:
    #         dfmaps = dfmaps
    #     else:
    #         dfmaps = dfmaps[dfmaps['nome_drs'].isin(selected_cities)].reset_index(drop=True)
    # else:
    #     if not selected_cities:
    #         dfplots = dfplots
    #     elif selected_cities == ['']:
    #         dfplots = dfplots
    #     else:
    #         dfplots = dfplots[dfplots['nome_drs'].isin(selected_cities)].reset_index(drop=True)

    dfmaps = dfmaps[dfmaps['datahora'] == str((unixToDatetime(map_slider)).strftime('%Y-%m-%d'))].reset_index(drop=True)


    max_scale_incidencia = dfmaps['casos_pc'].quantile(q=0.97)
    max_scale_obitos = dfmaps['obitos_pc'].quantile(q=0.97)

    if unixToDatetime(map_slider) <= pd.to_datetime('2020-03-29', format='%Y-%m-%d'):
        max_scale_incidencia = 1

    if unixToDatetime(map_slider) <= pd.to_datetime('2020-04-12', format='%Y-%m-%d'):
        max_scale_obitos = 1


    fig_map_incidencia = px.choropleth(data_frame= dfmaps,
                           geojson= gjson,
                           locations= 'codigo_ibge',
                           featureidkey= 'properties.id',  # properties.CD_GEOCMU
                           color= 'casos_pc',
                           #color_discrete_sequence= custom_colorscale_incidencia,
                           hover_data= {'nome_munic': True, 'nome_drs': True, 'codigo_ibge': False},  # ,
                           range_color= (0,max_scale_incidencia),
                           color_continuous_scale= custom_colorscale_incidencia)#'Reds')

    fig_map_incidencia.update_layout(title=dict(text="<b>Coeficiente de incidência por município de notificação</b>", xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=20, r=0, b=0, l=0)),
                                     coloraxis_colorbar=dict(title='', x=0, xanchor='left', lenmode='fraction', len=0.75, ticks='outside', thickness=20, tick0=0),
                                     margin=dict(l=0, r=0, b=0, t=30), titlefont=dict(size=14), height=300)

    if region_tabs == 'DRS':
        fig_map_incidencia.update_traces(hovertemplate='Cidade: %{customdata[0]}<br>DRS: %{customdata[1]}<br>Incidência: %{z}', marker={'line': {'color': 'white', 'width': 0.4}})
    else:
        fig_map_incidencia.update_traces(hovertemplate='Cidade: %{customdata[0]}<br>Incidência: %{z}', marker={'line': {'color': 'white', 'width': 0.4}})

    fig_map_incidencia.update_geos(showframe=False, showcountries=False, showcoastlines=False, showland=True, fitbounds='locations')


    ### Mapa mortalidade
    fig_map_mortalidade = px.choropleth(data_frame=dfmaps,
                           geojson=gjson,
                           locations='codigo_ibge',
                           featureidkey='properties.id',  # properties.CD_GEOCMU
                           color='obitos_pc',
                           #color_discrete_sequence= custom_colorscale_incidencia,
                           hover_data={'nome_munic': True, 'nome_drs': True, 'codigo_ibge': False},  # ,
                           range_color=(0,max_scale_obitos),
                           color_continuous_scale=custom_colorscale_mortalidade)#'Oranges')

    fig_map_mortalidade.update_layout(title=dict(text="<b>Coeficiente de mortalidade por município de notificação</b>", xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=20, r=0, b=0, l=0)),
                                      coloraxis_colorbar=dict(title='', xanchor='right', lenmode='fraction', len=0.75, ticks='outside', thickness=20, tick0=0),
                                      margin=dict(l=0, r=0, b=0, t=30), titlefont=dict(size=14), height=300)#, pad=0))

    if region_tabs == 'DRS':
        fig_map_mortalidade.update_traces(hovertemplate='Cidade: %{customdata[0]}<br>DRS: %{customdata[1]}<br>Incidência: %{z}', marker={'line': {'color': 'white', 'width': 0.4}})#, marker_line_size=1)
    else:
        fig_map_mortalidade.update_traces(hovertemplate='Cidade: %{customdata[0]}<br>Mortalidade: %{z}', marker={'line': {'color': 'white', 'width': 0.4}})#, marker_line_size=1)

    fig_map_mortalidade.update_geos(showframe=False, showcountries=False, showcoastlines=False, showland=True, fitbounds='locations')

    if region_tabs == 'RMC':
        fig_map_incidencia.update_traces(marker={'line': {'width': 1}})
        fig_map_mortalidade.update_traces(marker={'line': {'width': 1}})


    return fig_map_incidencia, fig_map_mortalidade



@app.callback(
    Output('today_indicators', 'figure'),
    [Input('label_last_update', 'children'),
     Input('region_tabs', 'value')]
)

#@cache.memoize(timeout=20)
def update_today_indicators(label_last_update, region_tabs):

    # today = date.today()
    today_ind = pd.to_datetime(latest_data, format='%Y-%m-%d')# TEMP
    yesterday = today_ind - timedelta(days=1) ### !!!!!!!! CHANGED to days=2 to comply with the temporary dfyesterday as dftoday
    today_ind = today_ind.strftime('%Y-%m-%d')
    yesterday = yesterday.strftime('%Y-%m-%d')

    if region_tabs == 'RMC':
        # !!!!!!!!! TEMPORARILY STORING dfyesterday as dftoday (WHILE I DONT IMPLEMENT A FALL-BACK IF THERES NO DATA TODAY)
        dftoday = dftcrmc_ind[dftcrmc_ind['datahora'] == today_ind]
        dfyesterday = dftcrmc_ind[dftcrmc_ind['datahora'] == yesterday]
        dftoday.loc[:,'letalidade']= dftoday['obitos']/dftoday['casos']
        dfyesterday.loc[:,'letalidade']= dfyesterday['obitos']/dfyesterday['casos']

    elif region_tabs == 'SP' or region_tabs == 'DRS':
        # !!!!!!!!! TEMPORARILY STORING dfyesterday as dftoday (WHILE I DONT IMPLEMENT A FALL-BACK IF THERES NO DATA TODAY)
        dftoday = dftc_ind[dftc_ind['datahora'] == today_ind] # todo update indicators to fetch latest data
        dfyesterday = dftc_ind[dftc_ind['datahora'] == yesterday]
        dftoday.loc[:,'letalidade'] = dftoday['obitos'] / dftoday['casos']
        dfyesterday.loc[:,'letalidade'] = dfyesterday['obitos'] / dfyesterday['casos']


    fontsize_ind = 24
    fontsize_title_ind = 12

    fig_ind = go.Figure()
    #fig_ind_r2 = go.Figure()
    #fig_ind_r3= go.Figure()

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos'].to_numpy()[0],
        number = {'font': {'size': fontsize_ind}},
        title = {'text': 'Total de casos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 0}),

        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_novos'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Novos casos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 1})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_pc'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Casos por<br>100 mil habitantes', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_pc'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 2})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Total de óbitos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 3})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_novos'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Novos óbitos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 4})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_pc'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Óbitos por<br>100 mil habitantes', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos_pc'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 5})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['letalidade'].to_numpy()[0],
        number={'valueformat': '.2%', 'font': {'size': fontsize_ind}},
        title = {'text': 'Letalidade<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['letalidade'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 6})
        )

    fig_ind.update_layout(
        grid = {'rows': 1, 'columns': 7, 'xgap': 0.4, 'pattern': "coupled"},
        margin=dict(l=30, r=30, t=20, b=15),
        height= 110)

    return fig_ind

@app.callback(
    [Output('today_indicators_mr1', 'figure'),
     Output('today_indicators_mr2', 'figure'),
     Output('today_indicators_mr3', 'figure')],
    [Input('label_last_update', 'children'),
     Input('region_tabs', 'value')]
)

#@cache.memoize(timeout=20)
def update_today_indicators_mobile(label_last_update, region_tabs):

    # today = date.today()
    today_ind = pd.to_datetime(latest_data, format='%Y-%m-%d')# TEMP
    yesterday = today_ind - timedelta(days=1) ### !!!!!!!! CHANGED to days=2 to comply with the temporary dfyesterday as dftoday
    today_ind = today_ind.strftime('%Y-%m-%d')
    yesterday = yesterday.strftime('%Y-%m-%d')

    if region_tabs == 'RMC':
        # !!!!!!!!! TEMPORARILY STORING dfyesterday as dftoday (WHILE I DONT IMPLEMENT A FALL-BACK IF THERES NO DATA TODAY)
        dftoday = dftcrmc_ind[dftcrmc_ind['datahora'] == today_ind]
        dfyesterday = dftcrmc_ind[dftcrmc_ind['datahora'] == yesterday]
        dftoday.loc[:,'letalidade']= dftoday['obitos']/dftoday['casos']
        dfyesterday.loc[:,'letalidade']= dfyesterday['obitos']/dfyesterday['casos']

    elif region_tabs == 'SP' or region_tabs == 'DRS':
        # !!!!!!!!! TEMPORARILY STORING dfyesterday as dftoday (WHILE I DONT IMPLEMENT A FALL-BACK IF THERES NO DATA TODAY)
        dftoday = dftc_ind[dftc_ind['datahora'] == today_ind] # todo update indicators to fetch latest data
        dfyesterday = dftc_ind[dftc_ind['datahora'] == yesterday]
        dftoday.loc[:,'letalidade'] = dftoday['obitos'] / dftoday['casos']
        dfyesterday.loc[:,'letalidade'] = dfyesterday['obitos'] / dfyesterday['casos']


    fontsize_ind = 24
    fontsize_title_ind = 11

    fig_ind_r1 = go.Figure()
    fig_ind_r2 = go.Figure()
    fig_ind_r3= go.Figure()

    fig_ind_r1.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos'].to_numpy()[0],
        number = {'font': {'size': fontsize_ind}},
        title = {'text': 'Total de casos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 0}),

        )

    fig_ind_r1.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_novos'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Novos casos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 1})
        )

    fig_ind_r1.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_pc'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Casos por<br>100 mil habitantes', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_pc'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 2})
        )

    fig_ind_r2.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Total de óbitos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 0})
        )

    fig_ind_r2.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_novos'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Novos óbitos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 1})
        )

    fig_ind_r2.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_pc'].to_numpy()[0],
        number={'font': {'size': fontsize_ind}},
        title = {'text': 'Óbitos por<br>100 mil habitantes', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos_pc'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 2})
        )

    fig_ind_r3.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['letalidade'].to_numpy()[0],
        number={'valueformat': '.2%', 'font': {'size': fontsize_ind}},
        title = {'text': 'Letalidade', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['letalidade'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 0})
        )

    fig_ind_r1.update_layout(
        grid = {'rows': 1, 'columns': 3, 'xgap': 0.4, 'pattern': "coupled"},
        margin=dict(l=30, r=30, t=20, b=15),
        height= 100)
    fig_ind_r2.update_layout(
        grid = {'rows': 1, 'columns': 3, 'xgap': 0.4, 'pattern': "coupled"},
        margin=dict(l=30, r=30, t=20, b=15),
        height= 100)
    fig_ind_r3.update_layout(
        grid = {'rows': 1, 'columns': 1, 'xgap': 0.4, 'pattern': "coupled"},
        margin=dict(l=30, r=30, t=20, b=15),
        height= 100)

    return fig_ind_r1, fig_ind_r2, fig_ind_r3


@app.callback(
    Output('javascript', 'run'),
    [Input('button_print', 'n_clicks')])
def printpdf(x):
    if x:
        return "window.print()"
    return ""

# if __name__ == '__main__':
#    app.run_server(host="127.0.0.1", debug=True, port=8080)

if __name__ == '__main__':
     app.run_server(host="0.0.0.0", debug=True, port=8080, use_reloader=False)