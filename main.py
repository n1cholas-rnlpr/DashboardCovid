#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 02:56:02 2020

@author: n1cholas-rnlpr
"""
import os
import urllib3

import numpy as np
import pandas as pd     #(version 1.0.0)
# import plotly           #(version 4.5.0)
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

import dash             #(version 1.8.0)
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_renderer
# from dash_table.Format import Format
import dash_table.FormatTemplate as FormatTemplate
# from dash_table.Format import Sign
from dash.dependencies import Input, Output, State

#import redis
import flask
import flask_caching
from flask_caching import Cache

from datetime import date, timedelta
from datetime import datetime as dt

import json
import time
import ssl

import visdcc

from epiweeks import Week

#from scipy import stats as sps
#from scipy.interpolate import interp1d


ssl._create_default_https_context = ssl._create_unverified_context


cod_rmc = [3501608, 3503802, 3509502, 3512803, 3515152, 3519055, 3519071,
           3520509, 3523404, 3524709, 3531803, 3532009, 3533403, 3536505,
           3537107, 3545803, 3548005, 3552403, 3556206, 3556701]

df_missing_c = pd.read_csv('todas_cidades_sp.csv', sep=',') # DF to merge for missing cities

custom_colorscale_mortalidade = [
[0, 'rgb(209, 209, 209)'],
[0.5, 'rgb(126, 0, 122)'],
[1, 'rgb(59, 0, 105)']]

custom_colorscale_incidencia = [
[0, 'rgb(209, 209, 209)'],
[0.5, 'rgb(54, 161, 161)'],
[1, 'rgb(30, 61, 61)']]


roxo='#6400de'
cyan='#36a1a1'


azul_observatorio = '#3f51b5'
azul_observatorio_rgb = 'rgb(63, 81, 181)'
azul_observatorio_footer = '#1a2130'

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

#global
#last_update = pd.to_datetime('2020-01-01')

#global dfseade_size_lastupdate
class gvars():
    dfseade_size_lastupdate = 0
    dfsg_size_lastupdate = 0
    last_update = pd.to_datetime('2020-01-01')

    df = 0
    daterange = 0
    df_hover = 0
    df_gdate = 0
    df_table_sp = 0
    dftc_ind = 0
    df_rmc = 0
    df_rmc_gdate = 0
    df_table_rmc = 0
    dftcrmc_ind = 0
    df_drs_gdate = 0
    df_table_drs = 0
    df_drs_ind = 0
    latest_data = 0
    df_SG = 0
    df_SG_obitos = 0
    df_SG_rmc = 0
    df_SG_rmc_obitos = 0



http = urllib3.PoolManager()


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
    for i, date in enumerate(gvars.daterange):
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



#update_data_fn()

with open('geojs-35-mun.json', 'r', encoding="UTF-8") as json_file:
    gjson = json.load(json_file)

#if not last_update:
#    last_update = pd.to_datetime('2020-01-01') # Date to use on first load, before initial callback that overwrites it

css_directory = os.getcwd()
stylesheets = ['css_main.css']
static_css_route = '/static/'




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
locale_br_script = ['https://cdn.plot.ly/plotly-locale-pt-br-latest.js']


app = dash.Dash(__name__)

pio.templates.default = "plotly_white"
server = app.server

# app.config['CACHE_TYPE'] = 'simple'

cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple',
  })


# ################### R0 PARAMETERS AND FUNCTIONS ######################
#
# ############################################ Parameters
#
# sigmas = np.linspace(1 / 20, 1, 20)
#
# #FILTERED_REGION_CODES = ['Estado de São Paulo']
#
# R_T_MAX = 12
# r_t_range = np.linspace(0, R_T_MAX, R_T_MAX * 100 + 1)
#
# GAMMA = 1/2.3
# #GAMMA = 1 / 2
#
#
# ############################################ Functions
#
# def prepare_cases(cases, cutoff=25):
#     new_cases = cases.diff()
#
#     smoothed = new_cases.rolling(7,
#                                  win_type='gaussian',
#                                  min_periods=1,
#                                  center=True).mean(std=2).round()
#
#     idx_start = np.searchsorted(smoothed, cutoff)
#
#     smoothed = smoothed.iloc[idx_start:]
#     original = new_cases.loc[smoothed.index]
#
#     return original, smoothed
#
#
#
# def get_posteriors(sr, sigma=0.15):
#     # (1) Calculate Lambda
#     lam = sr[:-1].values * np.exp(GAMMA * (r_t_range[:, None] - 1))
#
#     # (2) Calculate each day's likelihood
#     likelihoods = pd.DataFrame(
#         data=sps.poisson.pmf(sr[1:].values, lam),
#         index=r_t_range,
#         columns=sr.index[1:])
#
#     # (3) Create the Gaussian Matrix
#     process_matrix = sps.norm(loc=r_t_range,
#                               scale=sigma
#                               ).pdf(r_t_range[:, None])
#
#     # (3a) Normalize all rows to sum to 1
#     process_matrix /= process_matrix.sum(axis=0)
#
#     # (4) Calculate the initial prior
#     # prior0 = sps.gamma(a=4).pdf(r_t_range)
#     prior0 = np.ones_like(r_t_range) / len(r_t_range)
#     prior0 /= prior0.sum()
#
#     # Create a DataFrame that will hold our posteriors for each day
#     # Insert our prior as the first posterior.
#     posteriors = pd.DataFrame(
#         index=r_t_range,
#         columns=sr.index,
#         data={sr.index[0]: prior0}
#     )
#
#     # We said we'd keep track of the sum of the log of the probability
#     # of the data for maximum likelihood calculation.
#     log_likelihood = 0.0
#
#     # (5) Iteratively apply Bayes' rule
#     for previous_day, current_day in zip(sr.index[:-1], sr.index[1:]):
#         # (5a) Calculate the new prior
#         current_prior = process_matrix @ posteriors[previous_day]
#
#         # (5b) Calculate the numerator of Bayes' Rule: P(k|R_t)P(R_t)
#         numerator = likelihoods[current_day] * current_prior
#
#         # (5c) Calcluate the denominator of Bayes' Rule P(k)
#         denominator = np.sum(numerator)
#
#         # Execute full Bayes' Rule
#         posteriors[current_day] = numerator / denominator
#
#         # Add to the running sum of log likelihoods
#         log_likelihood += np.log(denominator)
#
#     return posteriors, log_likelihood
#
#
# def highest_density_interval(pmf, p=.9, debug=False):
#     # If we pass a DataFrame, just call this recursively on the columns
#     if (isinstance(pmf, pd.DataFrame)):
#         return pd.DataFrame([highest_density_interval(pmf[col], p=p) for col in pmf],
#                             index=pmf.columns)
#
#     cumsum = np.cumsum(pmf.values)
#
#     # N x N matrix of total probability mass for each low, high
#     total_p = cumsum - cumsum[:, None]
#
#     # Return all indices with total_p > p
#     lows, highs = (total_p > p).nonzero()
#
#     # Find the smallest range (highest density)
#     best = (highs - lows).argmin()
#
#     low = pmf.index[lows[best]]
#     high = pmf.index[highs[best]]
#
#     return pd.Series([low, high],
#                      index=[f'Low_{p * 100:.0f}',
#                             f'High_{p * 100:.0f}'])
#
#
#
#
# # R0
# def get_R0(latest_date, dfrmc, dfdrs, dfsp): # todo continue this
#
#     # Preparing the data and merging it all into one dataframe to be fed to the get_R0 function
#     dfrmc['state'] = 'RMC'
#     dfrmc.columns = ['date', 'positive', 'state']
#
#     dfdrs.columns = ['state', 'date', 'positive']
#
#     dfsp['state'] = 'Estado de São Paulo'
#
#     dfsp.columns = ['date', 'positive', 'state']
#
#     df_r0 = dfsp.append([dfdrs, dfrmc])
#
#     df_r0['date'] = pd.to_datetime(df_r0['date'], format="%Y-%m-%d")
#
#     df_r0.set_index(['state', 'date'], inplace=True)
#
#     df_r0 = df_r0.squeeze()
#
#
#
#     results = {}
#
#     targets = df_r0.index.get_level_values('state').isin(['Estado de São Paulo'])  # ~
#     df_r0 = df_r0.loc[targets]
#
#     for state_name, cases in df_r0.groupby(level='state'):
#
#         print(state_name)
#         new, smoothed = prepare_cases(cases, cutoff=25)
#
#         if len(smoothed) == 0:
#             new, smoothed = prepare_cases(cases, cutoff=10)
#
#         result = {}
#
#         # Holds all posteriors with every given value of sigma
#         result['posteriors'] = []
#
#         # Holds the log likelihood across all k for each value of sigma
#         result['log_likelihoods'] = []
#
#         # if state_name == 'São Paulo':
#         #     GAMMA = 1 / 2.4
#         # else:
#         #     GAMMA = 1 / 7
#
#         for sigma in sigmas:
#             posteriors, log_likelihood = get_posteriors(smoothed, sigma=sigma)
#             result['posteriors'].append(posteriors)
#             result['log_likelihoods'].append(log_likelihood)
#
#         # Store all results keyed off of state name
#         results[state_name] = result
#         # clear_output(wait=True)
#
#     #print('Done I.')
#
#     ############################################ Escolhendo o melhor sigma
#
#     # Each index of this array holds the total of the log likelihoods for
#     # the corresponding index of the sigmas array.
#     total_log_likelihoods = np.zeros_like(sigmas)
#
#     # Loop through each state's results and add the log likelihoods to the running total.
#     for state_name, result in results.items():
#         total_log_likelihoods += result['log_likelihoods']
#
#     # Select the index with the largest log likelihood total
#     max_likelihood_index = total_log_likelihoods.argmax()
#
#     # Select the value that has the highest log likelihood
#     sigma = sigmas[max_likelihood_index]
#
#     #print('Done II.')
#
#     ############################################ Processando o resultado final
#
#     final_results = None
#
#     for state_name, result in results.items():
#         print(state_name)
#         posteriors = result['posteriors'][max_likelihood_index]
#         hdis_90 = highest_density_interval(posteriors, p=.9)
#         hdis_50 = highest_density_interval(posteriors, p=.5)
#         most_likely = posteriors.idxmax().rename('ML')
#         result = pd.concat([most_likely, hdis_90, hdis_50], axis=1)
#         if final_results is None:
#             final_results = result
#         else:
#             final_results = pd.concat([final_results, result])
#         # clear_output(wait=True)
#
#     #print('Done III.')
#
#     return final_results



#server.secret_key = os.environ.get('secret_key', 'secret_key_default')

# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache/'
# })

# dfdfdfdf

# @server.route('/')
# @cache.memoize(timeout=1800000)
# def update_data_fn():
#
#     global df
#     df = pd.read_csv("https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/dados_covid_sp.csv", sep=";",
#                      decimal=",")
#     df = df.loc[:, ['datahora', 'nome_drs', 'nome_munic', 'codigo_ibge', 'casos', 'casos_novos', 'casos_pc', 'obitos',
#                     'obitos_novos', 'obitos_pc', 'letalidade', 'pop', 'pop_60', 'semana_epidem']]
#
#     df.loc[:, 'datahora'] = pd.to_datetime(df['datahora'], format="%Y-%m-%d")
#
#     global daterange
#     daterange = pd.date_range(start=df['datahora'].min(), end=df['datahora'].max(), freq='W-SAT')
#     # slider_min=unixTimeMillis(daterange.min())
#     # slider_max=unixTimeMillis(daterange.max())
#     # slider_value=slider_max
#     # slider_marks=getMarks(slider_min, slider_max)
#
#     #global last_update
#     #last_update = None
#
#     #nonlocal last_update
#     #if not last_update:
#     #    last_update = pd.to_datetime('2020-01-01')
#
#
#     if df.loc[:, 'datahora'].max() > last_update:
#         # df.loc[:,'casos_pc'] = df['casos_pc'].astype(int)  # todo check if we need one or two digits instead of a rounded int
#         # df.loc[:,'obitos_pc'] = df['obitos_pc'].astype(int)
#
#         latest_data_table = df['datahora'].max()
#
#         global df_hover
#         df_hover = df.groupby(by=['semana_epidem', 'datahora'], sort=True).sum().reset_index(drop=False)[
#             ['datahora', 'semana_epidem']]  # todo remember this test...
#
#         global df_gdate
#         df_gdate = df.groupby(by=["nome_munic", "nome_drs", "codigo_ibge", "datahora"], sort=True).sum().reset_index(
#             drop=False)
#         global df_table_sp
#         df_table_sp = df_gdate[df_gdate['datahora'] == latest_data_table]
#         global dftc_ind
#         dftc_ind = df_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(drop=False).sort_values(
#             'datahora')
#         # global df_plots_sp
#
#         global df_rmc
#         df_rmc = df[df['codigo_ibge'].isin(cod_rmc)]
#         global df_rmc_gdate
#         df_rmc_gdate = df_rmc.groupby(by=["nome_munic", "nome_drs", "codigo_ibge", "datahora"],
#                                       sort=True).sum().reset_index(drop=False)
#         global df_table_rmc
#         df_table_rmc = df_rmc_gdate[df_rmc_gdate['datahora'] == latest_data_table]
#         global dftcrmc_ind
#         dftcrmc_ind = df_rmc_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(
#             drop=False).sort_values('datahora')
#
#         global df_drs_gdate
#         df_drs_gdate = df.groupby(by=["nome_drs", "datahora"], sort=True).sum().reset_index(drop=False)
#         global df_table_drs
#         df_table_drs = df_drs_gdate[df_drs_gdate['datahora'] == latest_data_table]
#         global df_drs_ind
#         df_drs_ind = df_drs_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(
#             drop=False).sort_values('datahora')  # todo having time: change drs indicators to update with dropdown
#
#         #cache.clear()
#
#     # fhf
#     global latest_data
#     latest_data = df['datahora'].max()
#
#     # Loading SG DB
#     global df_SG
#     df_SG = pd.read_csv(
#         'http://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/casos_obitos_doencas_preexistentes.csv.zip',
#         sep=';')
#
#     df_SG.loc[:, 'data_inicio_sintomas'] = pd.to_datetime(df_SG['data_inicio_sintomas'], format="%m/%d/%Y")
#
#     # if df_SG.loc[:, 'datahora'].max() > last_update:
#     # global latest_data_sg
#     # latest_data_sg = df_SG['data_inicio_sintomas'].max()
#
#     df_SG = df_SG.loc[:, ['nome_munic', 'codigo_ibge', 'idade', 'cs_sexo', 'obito', 'asma', 'cardiopatia', 'diabetes',
#                           'doenca_hematologica', 'doenca_hepatica', 'doenca_neurologica', 'doenca_renal',
#                           'imunodepressao', 'obesidade', 'outros_fatores_de_risco', 'pneumopatia', 'puerpera',
#                           'sindrome_de_down']]
#
#     df_nomes_drs = df.groupby(by=["nome_munic", "nome_drs"], sort=True).sum().reset_index(drop=False)
#     # df_nomes_drs = df_gdate[df_gdate['datahora' == latest_data]]
#     df_nomes_drs = df_nomes_drs[['nome_munic', 'nome_drs']]
#
#     df_SG = pd.merge(df_SG, df_nomes_drs, on='nome_munic', how='left')
#
#     df_SG.replace("SIM", 1, inplace=True)
#     df_SG.replace("NÃO", 0, inplace=True)
#     df_SG.replace("IGNORADO", 0, inplace=True)
#     df_SG.replace("MASCULINO", "Masculino", inplace=True)
#     df_SG.replace("FEMININO", "Feminino", inplace=True)
#     df_SG.replace("INDEFINIDO", "Indefinido", inplace=True)
#
#     df_SG['bins_idade'] = pd.cut(x=df_SG['idade'],
#                                  bins=[0, 15, 25, 35, 45, 55, 60, 65, 70, 75, 80, 85, 90, 150],
#                                  labels=['0-15 anos', '16-25 anos', '26-35 anos', '36-45 anos', '46-55 anos',
#                                          '56-60 anos',
#                                          '61-65 anos', '66-70 anos', '71-75 anos', '76-80 anos', '81-85 anos',
#                                          '86-90 anos', '91+ anos'])
#
#     global df_SG_obitos
#     df_SG_obitos = df_SG[df_SG['obito'] == 1]
#
#     df_SG_obitos.reset_index(drop=True, inplace=True)
#
#     # for i in range(0, len(df_SG_obitos), 1):
#     #     if not any(df_SG_obitos.loc[i, ['asma', 'cardiopatia', 'diabetes', 'doenca_hematologica', 'doenca_hepatica',
#     #                                     'doenca_neurologica', 'doenca_renal', 'imunodepressao', 'obesidade',
#     #                                     'outros_fatores_de_risco', 'pneumopatia', 'puerpera', 'sindrome_de_down']]):
#     #         df_SG_obitos.loc[i, 'sem_comorbidades'] = 1
#     #
#     # df_SG_obitos['sem_comorbidades'].fillna(0, inplace=True)
#
#     global df_SG_rmc
#     df_SG_rmc = df_SG[df_SG['codigo_ibge'].isin(cod_rmc)]  # todo see if this is faster
#
#     global df_SG_rmc_obitos
#     df_SG_rmc_obitos = df_SG_obitos[df_SG_obitos['codigo_ibge'].isin(cod_rmc)]
#
#     return df, df_hover, df_gdate, df_table_sp, dftc_ind, df_rmc, df_rmc_gdate, df_table_rmc, dftcrmc_ind, df_drs_gdate, df_table_drs, df_drs_ind, latest_data, df_SG, df_SG_obitos, df_SG_rmc, df_SG_rmc_obitos

app.layout = html.Div([
    dcc.Interval(id='update_trigger', disabled=False, interval=1800000, max_intervals=-1, n_intervals=0),
    html.Div([
        dcc.Tabs(id='region_tabs', value='RMC', children=[
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
        html.Button(children='  PDF  ',n_clicks=0, id='button_print', className='two columns button_print'),
        html.Label(children='', id='label_last_update', className='two columns label_last_update', style={'fontSize': 14, 'margin': '0.7% 0px 0.7% 1.5%', 'color': '#d72a24', 'textAlign':'left'}),
    ]),
    html.Label(children='', id='label_ind', style={'fontSize': 14, 'margin': '1.5% 0px 0.5% 0', 'font-weight': 'bold', 'textAlign':'left'}),
    html.Div([
        #html.Label(children='', id='label_ind', style={'fontSize': 14, 'margin': '0.5% 0px 1.5% 0.7%', 'font-weight': 'bold', 'textAlign':'left'}),
        html.Div(children=[
            dcc.Loading(id="loading_ind_desktop", children=[
                dcc.Graph(id = 'today_indicators', config={'locale': 'pt-BR', 'displayModeBar': False})
                ]),
            html.Label('[1] Variação em relação ao mesmo dia da semana anterior.', style={'fontSize': 12, 'margin': '0 0px 0px 0.7%', 'textAlign':'left'})
        ], style={'margin': '1.5% 0 0 0'}, className= 'twelve columns ind_desktop'),

        html.Div(children=[
            dcc.Loading(id='loading_ind_mob', children=[
                html.Div([
                    dcc.Graph(id = 'today_indicators_mr1', config={'locale': 'pt-BR', 'displayModeBar': False})
                ], style={'margin': '5% 0 0 0'}),
                html.Div([
                    dcc.Graph(id = 'today_indicators_mr2', config={'locale': 'pt-BR', 'displayModeBar': False})
                ]),
                html.Div([
                    dcc.Graph(id = 'today_indicators_mr3', config={'locale': 'pt-BR', 'displayModeBar': False})
                ])
            ]),
            html.Label('[1] Variação em relação ao mesmo dia da semana anterior.', style={'fontSize': 8, 'margin': '0.5% 0px 0px 0.7%', 'textAlign':'left'})
        ], className = 'twelve columns ind_mobile', id='mobile_ind_container'),
    #html.Br(),
    #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
        ], style={'backgroundColor': 'white'}, className= 'row rounded_border_blue '),
    html.Br(),

    html.Div(id='div_filter_table_drs', className='row rounded_border_blue white_bg', style={'margin': '1% 0 1% 0'}, children=[
                   html.Div(className='one column button_filter_div', style={'width': '8.2%', 'margin': '0.5% 0 0 0.5%'}, children=[
                       html.Button(children='Filtrar', n_clicks=0, id='apply_filter_drs', style={'height': 36, 'width': '100%','backgroundColor': '#f0f1f4'})
                   ]),
                    html.Div(className='eleven columns table_filter_dropdown', style={'width': '90%','margin': '0.5% 0 0.5% 0.7%'}, children=[
                        dcc.Dropdown(
                            id='table_filter_drs',
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


    # #R0 Graph
    # html.Div(children=[
    #
    #    dcc.Loading(
    #        id='loading_r0',
    #        children=[
    #             dcc.Graph(id='r0_graphs', config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False})#,
    #                                                    #'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImage', 'lasso2d']})
    #        ]
    #    )
    #
    # ], className='row rounded_border_blue white_bg'),



    #Maps
    html.Label(children='', id='label_maps', style={'fontSize': 14, 'margin': '1.5% 0px 0.5% 0', 'font-weight': 'bold', 'textAlign':'left'}),
    html.Div(children=[
        html.Div(className='row', children=[

            html.Label('Selecione uma data:', style={'margin': '0.7% 0 0 0.7%', 'fontSize': 12, 'width': '100%', 'float': 'left', 'box-sizing': 'border-box'}), #8%

            html.Div(className='eight columns', style={'margin': '0.7% 0 0 0.7%'}, children=[
                dcc.DatePickerSingle(
                    id='map_calendar',
                    min_date_allowed=dt(2020, 2, 25),
                    #max_date_allowed=dt(2020, 7, 26),
                    #initial_visible_month=dt(2020, 7, 26),
                    #date=str(dt(2020, 7, 26)),
                    display_format='DD/MM/YYYY',
                    month_format='MM/YYYY',
                    show_outside_days=False,
                    placeholder='',
                    clearable=False,
                    style={'backgroundColor': '#f0f1f4'}
                    #style={'text-align':'middle'}
                ),
            ]),
        ]),


        html.Div([
            html.Div([
                dcc.Loading(
                    id="loading_map_incidencia",
                    children=[dcc.Graph(id='map_incidencia',
                                        config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImage', 'lasso2d']})],
                    # type="graph"
                )
            ], className='six columns'),

            html.Div([
                dcc.Loading(
                    id="loading_map_mortalidade",
                    children=[dcc.Graph(id='map_mortalidade',
                                        config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImage', 'lasso2d']})],
                    # type="graph"
                )
            ], className='six columns'),
            html.Br(),
            #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
        ], className='row'),

    ], className='row rounded_border_blue white_bg'),

    html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
    #html.Br(),
    #html.Br(),

    html.Div(id='div_filter_table', className='row rounded_border_blue white_bg', style={'margin': '1% 0 1% 0'}, children=[
               html.Div(className='one column button_filter_div', style={'width': '8.2%', 'margin': '0.5% 0 0 0.5%'}, children=[
                   html.Button(children='Filtrar', n_clicks=0, id='apply_filter', style={'height': 36, 'width': '100%','backgroundColor': '#f0f1f4'})
               ]),
                html.Div(className='eleven columns table_filter_dropdown', style={'width': '90%','margin': '0.5% 0 0.5% 0.7%'}, children=[
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
    #html.Br(),

    html.Label(children='', id='label_table', style={'fontSize': 14, 'margin': '1.5% 0px 0.5% 0', 'font-weight': 'bold', 'textAlign':'left'}),
    html.Div([

        html.Br(),
        #html.Label(children='', id='label_table', style={'fontSize': 14, 'font-weight': 'bold', 'marginLeft': '0.7%', 'textAlign': 'left', 'padding-top': '1%', 'padding-bottom': '1%'}),
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
            page_current=0,
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
                'fontSize': 10,
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
        html.Label('[1] Incidência: Número de casos confirmados por 100 mil habitantes. | [2] Mortalidade: Número de óbitos confirmados por 100 mil habitantes. | [3] Letalidade: Percentual do total óbitos em relação ao total de casos confirmados. | Obs: os filtros aplicados na tabela são aplicados também aos gráficos.', style={'fontSize':12, 'marginLeft': '0.5%', 'bottom': '0.5%'}),
        #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10})
    ], className='rounded_border_blue row white_bg'),
    html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
    html.Div([
        html.Br(),
        html.Br(),
        # First graphs row
        html.Label(children='', id='label_casos', style={'fontSize': 14, 'margin': '1.5% 0px 0.5% 0', 'font-weight': 'bold', 'textAlign':'left'}),
        html.Div([
            html.Div([
                visdcc.Run_js(id='javascript'),
                dcc.Loading(
                    id="loading_bargraph_novoscasos",
                    children=[dcc.Graph(id='bar_graph_novos_casos', config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                    'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImageButton', 'lasso2d', 'zoom2d', 'autoScale2d']})]
                    #type="graph"
                ),
            ], className='six columns'),

            html.Div([
                dcc.Loading(
                    id="loading_graph_casos",
                    children=[dcc.Graph(id='graph_casos', config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                    'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImageButton', 'lasso2d', 'zoom2d', 'autoScale2d']})]
                    #type="graph"
                ),
            ], className='six columns'),
            html.Br(),
            #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
        ], style={'paddingTop': '1%'}, className='row rounded_border_blue white_bg'),
        html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
        html.Br(),
        html.Br(),

        # third row
        html.Label(children='', id='label_obitos', style={'fontSize': 14, 'margin': '1.5% 0px 0.5% 0', 'font-weight': 'bold', 'textAlign':'left'}),
        html.Div([

            html.Div([
                dcc.Loading(
                    id="loading_bargraph_novosobitos",
                    children=[dcc.Graph(id='bar_graph_novos_obitos', config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                    'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImageButton', 'lasso2d', 'zoom2d', 'autoScale2d']})]
                    #type="graph"
                ),
            ], className='six columns'),

            html.Div([
                dcc.Loading(
                    id="loading_graph_obitos",
                    children=[dcc.Graph(id='graph_obitos', config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                    'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImageButton', 'lasso2d', 'zoom2d', 'autoScale2d']})]
                    #type="graph"
                ),
            ], className='six columns'),
            html.Br(),
            #html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':10, 'text-align':'center'})
        ], style={'paddingTop': '1%'}, className='row rounded_border_blue white_bg'),
        html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),
        html.Br(),

        html.Label(children='', id='label_sg', style={'fontSize': 14, 'margin': '1.5% 0px 0.5% 0', 'font-weight': 'bold', 'textAlign':'left'}),
        html.Div([
            html.Div([
                dcc.Loading(id='loading_piramide', children=[
                    dcc.Graph(id='piramide', config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                     'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImageButton', 'lasso2d', 'zoom2d', 'autoScale2d']}
                              )
            ])
            ], style={"marginTop":"1%"}, className='six columns'),

            html.Div([
                dcc.Loading(id='loading_comorbidades', children=[
                    dcc.Graph(id='comorbidades', config={'locale': 'pt-BR', 'displaylogo': False, 'scrollZoom': False,
                                                     'modeBarButtonsToRemove': ['hoverClosestGeo', 'pan2d', 'toImageButton', 'lasso2d', 'zoom2d', 'autoScale2d']}
                              )
                ])
            ], style={"marginTop":"1%"}, className='six columns'),
        ], className='row rounded_border_blue white_bg'),
        html.Label('Fonte: Observatório PUC-Campinas, com base nos dados do SEADE, 2020.', style={'fontSize':11}),

        html.Br(),

        html.Label('Versão:  v4.1', style={'fontSize': 11, 'fontWeight': 'bold', 'marginTop': '0.5%'}),
        html.Div(id='trigger_table_after_clear_filter', children=[], style={'display': 'none'})


    ])
])


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
#])


@app.callback(
    [Output('label_last_update', 'children'),
     Output('map_calendar', 'max_date_allowed'),
     Output('map_calendar', 'initial_visible_month'),
     Output('map_calendar', 'date')],
    [Input('update_trigger', 'n_intervals')]
)
#@cache.memoize(timeout=1800000)
def update_data(n_intervals):  #, df_seade_size_lastupdate_local=gvars.dfseade_size_lastupdate, df_sg_size_lastupdate_local=gvars.dfsg_size_lastupdate):

    #ctx = dash.callback_context
    today_timestamp = pd.to_datetime('today')
    today = pd.to_datetime('today', format='%Y-%m-%d')

    # if n_intervals == 0:
    #     #global last_update
    #     gvars.last_update = pd.to_datetime('2020-01-01') # todo consider setting this outside the app scope.

    http = urllib3.PoolManager()

    req_dfseade = http.request('HEAD', 'https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/dados_covid_sp.csv')
    req_dfsg = http.request('HEAD', 'http://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/casos_obitos_doencas_preexistentes.csv.zip')

    dfseade_size_now = req_dfseade.headers['Content-Length']
    dfsg_size_now = req_dfsg.headers['Content-Length']

    #if today_timestamp.hour >= 14 or n_intervals == 0:

    if dfseade_size_now != gvars.dfseade_size_lastupdate:
        #global df
        gvars.df = pd.read_csv("https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/dados_covid_sp.csv", sep=";", decimal=",")
        #df = pd.read_csv("seade.csv", sep=";", decimal=",")
        gvars.df = gvars.df.loc[:, ['datahora', 'nome_drs', 'nome_munic', 'codigo_ibge', 'casos', 'casos_novos', 'casos_pc', 'obitos',
                        'obitos_novos', 'obitos_pc', 'letalidade', 'pop', 'pop_60', 'semana_epidem']]

        gvars.df.loc[:, 'datahora'] = pd.to_datetime(gvars.df['datahora'], format="%Y-%m-%d")

        #global daterange
        gvars.daterange = pd.date_range(start=gvars.df['datahora'].min(), end=gvars.df['datahora'].max(), freq='W-SAT')

        latest_data_table = gvars.df['datahora'].max()

        for date in gvars.df.loc[gvars.df['semana_epidem'].isna(), 'datahora'].unique().tolist():
            date = pd.to_datetime(date, format="%Y-%m-%d")
            week = Week.fromdate(date)
            gvars.df.loc[(gvars.df['semana_epidem'].isna()) & (gvars.df['datahora'] == date), 'semana_epidem'] = week.weektuple()[1]

        #global df_hover
        gvars.df_hover = gvars.df.groupby(by=['semana_epidem', 'datahora'], sort=True).sum().reset_index(drop=False)[['datahora', 'semana_epidem']]  # todo remember this test...

        #global df_gdate
        gvars.df_gdate = gvars.df.groupby(by=["nome_munic", "nome_drs", "codigo_ibge", "datahora"], sort=True).sum().reset_index(drop=False)
        #global df_table_sp
        gvars.df_table_sp = gvars.df_gdate[gvars.df_gdate['datahora'] == latest_data_table]
        #global dftc_ind
        gvars.dftc_ind = gvars.df_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(drop=False).sort_values('datahora')
        # global df_plots_sp

        #global df_rmc
        gvars.df_rmc = gvars.df[gvars.df['codigo_ibge'].isin(cod_rmc)]
        #global gvars.df_rmc_gdate
        gvars.df_rmc_gdate = gvars.df_rmc.groupby(by=["nome_munic", "nome_drs", "codigo_ibge", "datahora"],
                                      sort=True).sum().reset_index(drop=False)
        #global df_table_rmc
        gvars.df_table_rmc = gvars.df_rmc_gdate[gvars.df_rmc_gdate['datahora'] == latest_data_table]
        #global dftcrmc_ind
        gvars.dftcrmc_ind = gvars.df_rmc_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(drop=False).sort_values('datahora')

        #global df_drs_gdate
        gvars.df_drs_gdate = gvars.df.groupby(by=["nome_drs", "datahora"], sort=True).sum().reset_index(drop=False)
        #global df_table_drs
        gvars.df_table_drs = gvars.df_drs_gdate[gvars.df_drs_gdate['datahora'] == latest_data_table]
        #global df_drs_ind
        #gvars.df_drs_ind = gvars.df_drs_gdate.groupby(pd.Grouper(key='datahora', freq='D')).sum().reset_index(drop=False).sort_values('datahora')  # todo having time: change drs indicators to update with dropdown

        gvars.dfseade_size_lastupdate = dfseade_size_now

        gvars.latest_data = gvars.df['datahora'].max()

        cache.clear()

    if dfsg_size_now != gvars.dfsg_size_lastupdate:
        gvars.df_SG = pd.read_csv('http://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/casos_obitos_doencas_preexistentes.csv.zip', sep=';')
        #gvars.df_SG = pd.read_csv('sg.csv', sep=';')

        gvars.df_SG.loc[:, 'data_inicio_sintomas'] = pd.to_datetime(gvars.df_SG['data_inicio_sintomas'], format="%Y-%m-%d")  #format="%m/%d/%Y")


        gvars.df_SG = gvars.df_SG.loc[:, ['nome_munic', 'codigo_ibge', 'idade', 'cs_sexo', 'obito', 'asma', 'cardiopatia', 'diabetes',
                              'doenca_hematologica', 'doenca_hepatica', 'doenca_neurologica', 'doenca_renal',
                              'imunodepressao', 'obesidade', 'outros_fatores_de_risco', 'pneumopatia', 'puerpera',
                              'sindrome_de_down']]

        df_nomes_drs = gvars.df.groupby(by=["nome_munic", "nome_drs"], sort=True).sum().reset_index(drop=False)

        df_nomes_drs = df_nomes_drs[['nome_munic', 'nome_drs']]

        gvars.df_SG = pd.merge(gvars.df_SG, df_nomes_drs, on='nome_munic', how='left')

        gvars.df_SG.replace("SIM", 1, inplace=True)
        gvars.df_SG.replace("NÃO", 0, inplace=True)
        gvars.df_SG.replace("IGNORADO", 0, inplace=True)
        gvars.df_SG.replace("MASCULINO", "Masculino", inplace=True)
        gvars.df_SG.replace("FEMININO", "Feminino", inplace=True)
        gvars.df_SG.replace("INDEFINIDO", "Indefinido", inplace=True)

        gvars.df_SG['bins_idade'] = pd.cut(x=gvars.df_SG['idade'],
                                     bins=[0, 15, 25, 35, 45, 55, 60, 65, 70, 75, 80, 85, 90, 150],
                                     labels=['0-15 anos', '16-25 anos', '26-35 anos', '36-45 anos', '46-55 anos', '56-60 anos',
                                             '61-65 anos', '66-70 anos', '71-75 anos', '76-80 anos', '81-85 anos', '86-90 anos', '91+ anos'])

        #global df_SG_obitos
        gvars.df_SG_obitos = gvars.df_SG[gvars.df_SG['obito'] == 1]

        gvars.df_SG_obitos.reset_index(drop=True, inplace=True)

        #global df_SG_rmc
        gvars.df_SG_rmc = gvars.df_SG[gvars.df_SG['codigo_ibge'].isin(cod_rmc)]  # todo see if this is faster

        #global gvars.df_SG_rmc_obitos
        gvars.df_SG_rmc_obitos = gvars.df_SG_obitos[gvars.df_SG_obitos['codigo_ibge'].isin(cod_rmc)]

        gvars.dfsg_size_lastupdate = dfsg_size_now

        cache.clear()
    ##if fetched_one:
    #    fetched_once = 1

    #global last_update
    gvars.last_update = today_timestamp

    first_string='Última atualização: '
    label_last_update= first_string + str(gvars.latest_data.strftime('%d/%m/%Y'))#  + second_string + str(gvars.latest_data_sg.strftime('%d/%m/%Y'))

    max_allowed_date = gvars.latest_data
    initial_visible_month = gvars.latest_data
    calendar_date = gvars.latest_data

    # if not ctx.triggered:
    #     global fetched_once
    #     fetched_once = 1
    # global n_fetches
    # if not n_fetches: # hi
    #     n_fetches = 1
    # else:
    #     n_fetches = n_fetches + 1

    #global fetched_once
    #fetched_once = 1

    return label_last_update, max_allowed_date, initial_visible_month, calendar_date#, slider_min, slider_max, slider_value, slider_marks

@app.callback(
    [Output('table_filter', 'value'),
     Output('table_filter_drs', 'value'),
     Output('div_filter_table', 'style'),
     Output('div_filter_table_drs', 'style'),
     Output('trigger_table_after_clear_filter', 'children')],
    [Input('region_tabs', 'value')]
)
def clear_filter(region_tabs):
    if region_tabs == 'DRS':
        style_table_filter={'display': 'none', 'margin': '1.5% 0 1% 0'}
        style_table_filter_drs={'display': 'block', 'margin': '0.8% 0 1% 0'}
    else:
        style_table_filter = {'display': 'block', 'margin': '1.5% 0 1% 0'}
        style_table_filter_drs = {'display': 'none', 'margin': '0.8% 0 1% 0'}
    return [''], [''], style_table_filter, style_table_filter_drs, []


@app.callback(
    [Output('table', 'data'),
    Output('table', 'columns'),
    Output('table', 'page_action'),
    Output('table', 'style_table'),
    Output('table', 'page_current'),
    Output('table_filter', 'options'),
    Output('table_filter_drs', 'options'),
    #Output('table_filter', 'value'),
    Output('label_ind', 'children'),
    Output('label_maps', 'children'),
    Output('label_table', 'children'),
    Output('label_casos', 'children'),
    Output('label_obitos', 'children'),
    Output('label_sg', 'children')],
    [Input('label_last_update', 'children'),
     Input('region_tabs', 'value'),
     Input('apply_filter', 'n_clicks'),
     Input('apply_filter_drs', 'n_clicks'),
     Input('trigger_table_after_clear_filter', 'children')],
    [State('table_filter', 'value'),
     State('table_filter_drs', 'value')],
    prevent_initial_call=True
)
@cache.memoize(timeout=86400)
def build_table(label_last_update, region_tabs, n_clicks, button2, trigger_table_after_clear_filter, selected_cities, selected_cities_drs):

    if not selected_cities:
        if selected_cities_drs:
            selected_cities = selected_cities_drs
    elif selected_cities == ['']:
        if selected_cities_drs:
            selected_cities = selected_cities_drs

    separator = ', '

    columns = [{'name': 'Cidade', 'id': 'nome_munic', 'deletable': False, 'selectable': True, 'hideable': False},
               {'name': 'Casos Acumulados', 'id': 'casos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}}, #{'locale': {'group': '.', 'decimal': ','}, 'specifier': '.'}},
               {'name': 'Novos Casos', 'id': 'casos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
               {'name': 'Incidência [1]', 'id': 'casos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ',.1f'}},
               {'name': 'Óbitos Acumulados', 'id': 'obitos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
               {'name': 'Novos Óbitos', 'id': 'obitos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
               {'name': 'Mortalidade [2]', 'id': 'obitos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ',.1f'}},
               {'name': 'Letalidade [3]', 'id': 'letalidade', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(2)},
               {'name': 'População', 'id': 'pop', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
               {'name': 'População 60+', 'id': 'pop_60_perc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(1)}]

    label_selected_cities = selected_cities

    if region_tabs == 'RMC':
        dropdown_options = [{'label': i, 'value': i}for i in gvars.df_table_rmc['nome_munic']]
        styletable = {'height': 300, 'overflowY': 'auto'}

        label_ind = 'Indicadores Diários [1] | Região Metropolitana de Campinas'
        label_table = 'Indicadores Diários | Municípios da RMC'
        label_maps = 'Mapas | Região Metropolitana de Campinas'
        label_casos = 'Evolução de Casos | Municípios da RMC'
        label_obitos = 'Evolução de Mortes | Municípios da RMC'
        label_sg = 'Demografia e Doenças Pré-existentes | Municípios da RMC'

        if selected_cities == ['']:
            dftable = gvars.df_table_rmc
        elif not selected_cities:
            dftable = gvars.df_table_rmc
        else:
            dftable = gvars.df_table_rmc[gvars.df_table_rmc['nome_munic'].isin(selected_cities)].reset_index(drop=True)
            styletable = {}


            if len(selected_cities) < 5:
                label_table = 'Indicadores Diários | ' + separator.join(label_selected_cities)
                label_casos = 'Evolução de Casos | ' + separator.join(label_selected_cities)
                label_obitos = 'Evolução de Mortes | ' + separator.join(label_selected_cities)
                label_sg = 'Demografia e Doenças Pré-existentes | ' + separator.join(label_selected_cities)
            else:
                label_table = 'Indicadores Diários | Municípios selecionados'
                label_casos = 'Evolução de Casos | Municípios selecionados'
                label_obitos = 'Evolução de Mortes | Municípios selecionados'
                label_sg = 'Demografia e Doenças Pré-existentes | Municípios selecionados'


        pageaction = 'none'

    elif region_tabs == 'DRS':
        dropdown_options = [{'label': i, 'value': i} for i in gvars.df_table_drs['nome_drs']]
        styletable = {'height': 300, 'overflowY': 'auto'}

        columns = [{'name': 'Nome DRS', 'id': 'nome_drs', 'deletable': False, 'selectable': True, 'hideable': False},
                   {'name': 'Casos Acumulados', 'id': 'casos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
                   {'name': 'Novos Casos', 'id': 'casos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
                   {'name': 'Incidência [1]', 'id': 'casos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': '.1f'}},
                   {'name': 'Óbitos Acumulados', 'id': 'obitos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
                   {'name': 'Novos Óbitos', 'id': 'obitos_novos', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
                   {'name': 'Mortalidade [2]', 'id': 'obitos_pc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': '.1f'}},
                   {'name': 'Letalidade [3]', 'id': 'letalidade', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(2)},
                   {'name': 'População', 'id': 'pop', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': {'specifier': ','}},
                   {'name': 'População 60+', 'id': 'pop_60_perc', 'deletable': False, 'selectable': True, 'hideable': False, 'type': 'numeric', 'format': FormatTemplate.percentage(1)}]

        label_ind = 'Indicadores Diários [1] | Estado de São Paulo'
        label_table = 'Indicadores Diários | Departamentos Regionais de Saúde - SP'
        label_maps = 'Mapas | Estado de São Paulo'
        label_casos = 'Evolução de Casos | Estado de São Paulo'
        label_obitos = 'Evolução de Mortes | Estado de São Paulo'
        label_sg = 'Demografia e Doenças Pré-Existentes | Estado de São Paulo'


        if selected_cities == ['']:
            dftable = gvars.df_table_drs
        elif not selected_cities:
            dftable = gvars.df_table_drs
        else:
            dftable = gvars.df_table_drs[gvars.df_table_drs['nome_drs'].isin(selected_cities)].reset_index(drop=True)
            styletable = {}

            if len(selected_cities) < 5:
                label_maps = 'Mapas | DRS: ' + separator.join(label_selected_cities)
                label_table = 'Indicadores Diários | DRS: ' + separator.join(label_selected_cities)
                label_casos = 'Evolução de Casos | DRS: ' + separator.join(label_selected_cities)
                label_obitos = 'Evolução de Óbitos | DRS: ' + separator.join(label_selected_cities)
                label_sg = 'Demografia e Doenças Pré-Existentes | DRS: ' + separator.join(label_selected_cities)
            else:
                label_maps = 'Mapas | DRSs selecionadas'
                label_table = 'Indicadores Diários | DRSs selecionadas'
                label_casos = 'Evolução de Casos | DRSs selecionadas'
                label_obitos = 'Evolução de Mortes | DRSs selecionadas'
                label_sg = 'Demografia e Doenças Pré-Existentes | DRSs selecionadas'


        #dftable.loc[:,'casos_pc']= dftable['casos_pc'].round(decimals=0)
        #dftable.loc[:,'obitos_pc']= dftable['obitos_pc'].round(decimals=0)
        pageaction = 'none'

    elif region_tabs == 'SP':
        dropdown_options = [{'label': i, 'value': i} for i in gvars.df_table_sp['nome_munic']]

        label_ind = 'Indicadores Diários [1] | Estado de São Paulo'
        label_table = 'Indicadores Diários | Municípios do Estado de São Paulo'
        label_maps = 'Mapas | Estado de São Paulo'
        label_casos = 'Evolução de Casos | Estado de São Paulo'
        label_obitos = 'Evolução de Mortes | Estado de São Paulo'
        label_sg = 'Demografia e Doenças Pré-Existentes | Estado de São Paulo'

        if selected_cities == ['']:
            dftable = gvars.df_table_sp
        elif not selected_cities:
            dftable = gvars.df_table_sp
        else:
            dftable = gvars.df_table_sp[gvars.df_table_sp['nome_munic'].isin(selected_cities)].reset_index(drop=True)

            if len(selected_cities) < 5:
                label_table = 'Indicadores Diários | ' + separator.join(label_selected_cities)
                label_casos = 'Evolução de Casos | ' + separator.join(label_selected_cities)
                label_obitos = 'Evolução de Mortes | ' + separator.join(label_selected_cities)
                label_sg = 'Demografia e Doenças Pré-Existentes | ' + separator.join(label_selected_cities)
            else:
                label_table = 'Indicadores Diários | Municípios selecionados'
                label_casos = 'Evolução de Casos | Municípios selecionados'
                label_obitos = 'Evolução de Mortes | Municípios selecionados'
                label_sg = 'Demografia e Doenças Pré-Existentes | Municípios selecionados'

        pageaction = 'native'
        styletable = {}

    dftable.loc[:, 'casos_pc'] = dftable.loc[:, 'casos'] / (dftable.loc[:, 'pop'] / 100000)
    dftable.loc[:, 'obitos_pc'] = dftable.loc[:, 'obitos'] / (dftable.loc[:, 'pop'] / 100000)

    dftable.loc[:,'letalidade'] = dftable.loc[:,'obitos']/dftable.loc[:,'casos']
    dftable.loc[:,'pop_60_perc'] = dftable.loc[:,'pop_60']/dftable.loc[:,'pop']

    page_current=0

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

    if region_tabs == 'DRS':
        dropdown_options_drs = dropdown_options
    else:
        dropdown_options_drs = []

    return dftable.to_dict('records'), columns, pageaction, styletable, page_current, dropdown_options, dropdown_options_drs, label_ind, label_maps, label_table, label_casos, label_obitos, label_sg



@app.callback(
        [Output('bar_graph_novos_casos', 'figure'),
         Output('graph_casos', 'figure'),
         Output('bar_graph_novos_obitos', 'figure'),
         Output('graph_obitos', 'figure'),
         Output('piramide', 'figure'),
         Output('comorbidades', 'figure')],
        [Input('label_last_update', 'children'),
         Input('region_tabs', 'value'),
         Input('apply_filter', 'n_clicks'),
         Input('apply_filter_drs', 'n_clicks'),
         Input('table', 'data')],
        [State('table_filter', 'value'),
         State('table_filter_drs', 'value')],
        prevent_initial_call=True
)

@cache.memoize(timeout=86400)
def build_graphs(label_last_update, region_tabs, button, button2, table_data_trigger_refresh, selected_cities, selected_cities_drs):

    if not selected_cities:
        if selected_cities_drs:
            selected_cities=selected_cities_drs
    elif selected_cities == ['']:
        if selected_cities_drs:
            selected_cities=selected_cities_drs

    if region_tabs == 'RMC':
        dfplots = gvars.df_rmc_gdate.loc[:, ['datahora', 'nome_munic', 'casos_novos', 'casos', 'obitos_novos', 'obitos', 'casos_pc', 'obitos_pc', 'letalidade', 'pop']]
        df_comorb = gvars.df_SG_rmc_obitos.loc[:,:]
        df_pir_casos = gvars.df_SG_rmc.loc[:, ['nome_munic', 'bins_idade', 'cs_sexo']]
        df_pir_obitos = gvars.df_SG_rmc_obitos.loc[:, ['nome_munic', 'bins_idade', 'cs_sexo']]

    elif region_tabs == 'SP' or region_tabs == 'DRS':
        dfplots = gvars.df_gdate.loc[:, ['datahora', 'nome_munic', 'nome_drs', 'casos_novos', 'casos', 'obitos_novos', 'obitos', 'casos_pc', 'obitos_pc', 'letalidade', 'pop']]
        df_comorb = gvars.df_SG_obitos.loc[:,:]
        df_pir_casos = gvars.df_SG.loc[:, ['nome_munic', 'nome_drs', 'bins_idade', 'cs_sexo']]
        df_pir_obitos = gvars.df_SG_obitos.loc[:, ['nome_munic', 'nome_drs', 'bins_idade', 'cs_sexo']]


    if region_tabs != 'DRS':
        if not selected_cities:
            dfplots = dfplots

        elif selected_cities == ['']:
            dfplots = dfplots
        else:
            dfplots = dfplots[dfplots['nome_munic'].isin(selected_cities)].reset_index(drop=True)
            df_pir_casos = df_pir_casos[df_pir_casos['nome_munic'].isin(selected_cities)].reset_index(drop=True)
            df_pir_obitos = df_pir_obitos[df_pir_obitos['nome_munic'].isin(selected_cities)].reset_index(drop=True)
            df_comorb = df_comorb[df_comorb['nome_munic'].isin(selected_cities)].reset_index(drop=True)
    else:
        if not selected_cities:
            dfplots = dfplots
            df_comorb = df_comorb.loc[:,:]
        elif selected_cities == ['']:
            dfplots = dfplots
            df_comorb = df_comorb.loc[:,:]
        else:
            dfplots = dfplots[dfplots['nome_drs'].isin(selected_cities)].reset_index(drop=True)
            df_pir_casos = df_pir_casos[df_pir_casos['nome_drs'].isin(selected_cities)].reset_index(drop=True)
            df_pir_obitos = df_pir_obitos[df_pir_obitos['nome_drs'].isin(selected_cities)].reset_index(drop=True)
            df_comorb = df_comorb[df_comorb['nome_drs'].isin(selected_cities)].reset_index(drop=True)


    df_moving_avg = dfplots.groupby(by="datahora", sort=True).sum().reset_index(drop=False)

    dfacumulados_daily = df_moving_avg[['datahora', 'casos', 'obitos']]

    dfplots = dfplots.groupby(pd.Grouper(key='datahora', freq='W-SAT')).sum().sort_values('datahora').reset_index(drop=False)#.drop(19, axis=0)

    #dfacumulados = pd.DataFrame()
    week_interval = pd.date_range(start=dfplots['datahora'].min(), end=dfplots['datahora'].max(), freq='W-SAT')

    if week_interval.max() == gvars.latest_data:
        rows = len(dfplots)
    else:
        rows = len(dfplots)-1

    dfplots['var_casos_novos_semana'] = 0
    dfplots['var_obitos_novos_semana'] = 0
    dfplots['var_casos_semana'] = 0
    dfplots['var_obitos_semana'] = 0

    for i in range(0, rows, 1):
        idate = week_interval[i]
        dftemp = dfacumulados_daily[dfacumulados_daily['datahora'] == idate].reset_index(drop=True)
        dfplots.loc[i, 'casos'] = dftemp.loc[0, 'casos']
        dfplots.loc[i, 'obitos'] = dftemp.loc[0, 'obitos']
        if i >= 1:
            dfplots.loc[i, 'var_casos_novos_semana'] = dfplots.loc[i, 'casos_novos'] / dfplots.loc[i-1, 'casos_novos']-1
            dfplots.loc[i, 'var_obitos_novos_semana'] = dfplots.loc[i, 'obitos_novos'] / dfplots.loc[i-1, 'obitos_novos']-1
            dfplots.loc[i, 'var_casos_semana'] = dfplots.loc[i, 'casos'] / dfplots.loc[i-1, 'casos']-1
            dfplots.loc[i, 'var_obitos_semana'] = dfplots.loc[i, 'obitos'] / dfplots.loc[i-1, 'obitos']-1


    dfplots['var_casos_novos_semana'].fillna(value=0, inplace=True)
    dfplots['var_obitos_novos_semana'].fillna(value=0, inplace=True)
    dfplots['var_casos_semana'].fillna(value=0, inplace=True)
    dfplots['var_obitos_semana'].fillna(value=0, inplace=True)


    #dfplots['var_casos_novos_semana'].replace([np.inf, -np.inf], "∞")
    #dfplots['var_obitos_novos_semana'].replace([np.inf, -np.inf], "∞")
    #dfplots['var_casos_semana'].replace([np.inf, -np.inf], "∞")
    #dfplots['var_obitos_semana'].replace([np.inf, -np.inf], "∞")


    if dfplots['datahora'].max() > gvars.latest_data:
        dfplots = dfplots[:-1]



    # dftoday.loc[:, 'casos_pc'] = dftoday['casos_pc'].round(decimals=0)
    # dftoday.loc[:, 'obitos_pc'] = dftoday['obitos_pc'].round(decimals=0)


    df_moving_avg['media_movel_casos'] = 0
    df_moving_avg['media_movel_obitos'] = 0
    df_moving_avg['var_media_movel_casos'] = 0
    df_moving_avg['var_media_movel_obitos'] = 0


    for i in range(6, len(df_moving_avg), 1):
        dfmovavg_sum = df_moving_avg.loc[i - 6:i, :]
        dfmovavg_sum = dfmovavg_sum.sum()
        df_moving_avg.loc[i, 'media_movel_casos'] = dfmovavg_sum['casos_novos'] / 7
        df_moving_avg.loc[i, 'media_movel_obitos'] = dfmovavg_sum['obitos_novos'] / 7
        if i >= 14:
            df_moving_avg.loc[i, 'var_media_movel_casos'] = df_moving_avg.loc[i, 'media_movel_casos']/df_moving_avg.loc[i-14, 'media_movel_casos']-1
            df_moving_avg.loc[i, 'var_media_movel_obitos'] = df_moving_avg.loc[i, 'media_movel_obitos'] / df_moving_avg.loc[i-14, 'media_movel_obitos']-1

    #dfplots['var_media_movel_casos'].fillna(value=0, inplace=True)      # todo sort out how to show inf in plotly
    #dfplots['var_media_movel_obitos'].fillna(value=0, inplace=True)


    df_moving_avg.loc[:, 'media_movel_casos'] = df_moving_avg['media_movel_casos'].round(decimals=0)
    df_moving_avg.loc[:, 'media_movel_obitos'] = df_moving_avg['media_movel_obitos'].round(decimals=0)
    df_moving_avg.loc[:, 'var_media_movel_casos'] = df_moving_avg['var_media_movel_casos'].round(decimals=4)
    df_moving_avg.loc[:, 'var_media_movel_obitos'] = df_moving_avg['var_media_movel_obitos'].round(decimals=4)

    # Fixing incidencia and mortalidade
    df_moving_avg.loc[:, 'casos_pc'] = df_moving_avg.loc[:, 'casos'] / (df_moving_avg.loc[:, 'pop'] / 100000)
    df_moving_avg.loc[:, 'obitos_pc'] = df_moving_avg.loc[:, 'obitos'] / (df_moving_avg.loc[:, 'pop'] / 100000)
    #dfplots.loc[:, 'casos_pc'] = dfplots.loc[:, 'casos'] / (dfplots.loc[:, 'pop'] / 100000)
    #dfplots.loc[:, 'obitos_pc'] = dfplots.loc[:, 'obitos'] / (dfplots.loc[:, 'pop'] / 100000)

    #dfpc = df_moving_avg.loc[:,['datahora', 'casos_pc', 'obitos_pc']]
    #dfplots = pd.merge(dfplots, dfpc, how='left', on='datahora')
    dfplots = pd.merge(dfplots, gvars.df_hover, how='left', on='datahora')
    df_moving_avg = pd.merge(df_moving_avg, gvars.df_hover, how='left', on='datahora')

    #dfplots.loc[:, 'letalidade'] = 0
    dfplots.loc[:,'letalidade'] = dfplots['obitos']/dfplots['casos']
    dfplots['letalidade'].fillna(value=0, inplace= True)
    df_moving_avg.loc[:, 'letalidade'] = df_moving_avg['obitos'] / df_moving_avg['casos']
    df_moving_avg['letalidade'].fillna(value=0, inplace= True)

    fig_bar_novos_casos = px.bar(df_moving_avg, x='datahora', y='casos_novos', hover_data={'letalidade': True})
    #fig_bar_novos_casos = go.Figure()
    #fig_bar_novos_casos.add_trace(go.Bar(

    fig_bar_novos_casos.update_traces(hovertemplate="<b>Novos casos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[0]:.2%}", marker={'color': cyan, 'opacity': 0.5})#azul_observatorio)
    #)
    fig_bar_novos_casos.add_trace(go.Scatter(
        x=df_moving_avg['datahora'],
        y=df_moving_avg['media_movel_casos'],
        customdata=df_moving_avg[['var_media_movel_casos', 'semana_epidem']],
        mode='lines',
        line=go.scatter.Line(color='#277373'),
        showlegend=False,
        text=df_moving_avg['var_media_movel_casos'],
        name='',
        hovertemplate='<b>Média móvel</b> (7 dias): %{y:,}<br><b>Var. média móvel</b> (14 dias): %{text:.2%}'))

# SEMANAL
    fig_bar_novos_casos.add_trace(go.Bar(
            x=dfplots['datahora'],
            y=dfplots['casos_novos'],
            customdata=dfplots[['var_casos_novos_semana', 'semana_epidem', 'letalidade']],
            showlegend=False,
            marker={'color': cyan, 'opacity': 0.75},
            name='',
            visible=False,
            hoverinfo='all',
            hovertemplate='<b>Semana Epidem.</b>: %{customdata[1]}<br><b>Novos casos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[2]:.2%}<br><b>Var.</b> (ref. semana anterior): %{customdata[0]:.2%}'))

    fig_bar_novos_casos.update_layout(title=dict(text='<b>Novos casos por dia de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1,
                      pad=dict(t=17, r=0, b=20, l=0)), #b70
                      titlefont=dict(size=13),
                      xaxis=dict(#rangeslider=dict(visible=True),
                                 range=[pd.to_datetime('11-04-2020', format='%d-%m-%Y'), gvars.latest_data+timedelta(days=1)]),
                      xaxis_title="",
                      yaxis=dict(rangemode='nonnegative'),
                      yaxis_title="Novos casos",
                      hovermode='x unified',
                      margin=dict(l=0, r=0, t=30, b=60),
                      height=370,
                      dragmode=False,
                      selectdirection='h',
                      hoverlabel={'bordercolor': '#ced1d6', 'font': {'size': 10, 'color': '#5e6063'}, 'namelength':5},
                      #xaxis_tickformat='%d %b',
                      updatemenus=[
                          dict(
                              type="buttons",
                              direction="left",
                              buttons=list([
                                  dict(
                                      args=[{"visible": [True, True, False]},
                                            {"title": {'text': "<b>Novos casos por dia de notificação</b>", 'font': {'size': 13}, 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5,
                                                       'y': 1, 'pad': dict(t=17, r=0, b=40, l=0)}}
                                            ],
                                      label="Diário | Média Móvel",
                                      method="update"
                                  ),
                                  dict(
                                      args=[{"visible": [False, False, True]},
                                            {"title": {'text': "<b>Novos casos por semana de notificação</b>", 'font':{'size':13}, 'xanchor': 'center',
                                                       'yanchor': 'top', 'x': 0.5, 'y': 1, 'pad': dict(t=17, r=0, b=40, l=0)}}
                                            ],
                                      label="Semana Epidemiológica",
                                      method="update"
                                  )
                              ]),
                              pad={"r": 7, "t": 8},
                              showactive=True,
                              x=0.5,
                              xanchor="center",
                              y=-0.2, #-0.54
                              yanchor="bottom",
                              font=dict(size=9)
                          )
                      ])



    fig_bar_novos_casos.update_xaxes(tickfont={'size':8})#, tickformatstops=[dict(dtickrange=[None,691200000], value='%d/%m/%Y'),
                                                                                        #dict(dtickrange=[691200000,None], value='%d %b')])



    fig_graph_casos = px.line(df_moving_avg, x='datahora', y='casos', hover_data={'casos_pc': True, 'letalidade': True})  # , labels = {'newCases': 'Novos casos', 'newDeaths':'Novos óbitos'})

    fig_graph_casos.update_traces(mode="lines", hovertemplate='<b>Total de casos</b>: %{y:,}<br><b>Incidência</b> (100 mil hab.): %{customdata[0]:,.1f}<br><b>Letalidade</b>: %{customdata[1]:.2%}', line=dict(color='#277373', width=2))

    fig_graph_casos.add_trace(go.Scatter(
        x=dfplots['datahora'],
        y=dfplots['casos'],
        customdata=dfplots[['var_casos_semana', 'semana_epidem', 'casos_pc', 'letalidade']],
        mode='lines+markers',
        line=go.scatter.Line(color='#277373', width=2.5),
        showlegend=False,
        marker= {'size': 5, 'color': cyan, 'opacity': 0.7},
        name='',
        visible= False,
        hovertemplate='<b>Semana Epidem.</b>: %{customdata[1]}<br><b>Total de casos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[3]:.2%}<br><b>Var.</b> (ref. semana anterior): %{customdata[0]:.2%}')) # <b>Incidencia</b> (100 mil hab.): %{customdata[2]:,.1f}<br>

    fig_graph_casos.update_layout(title=dict(text='<b>Casos acumulados por dia de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=17, r=0, b=20, l=0)),
                      titlefont=dict(size=13),
                      yaxis=dict(rangemode='nonnegative'),
                      xaxis_title="",
                      yaxis_title="Casos acumulados",
                      hovermode='x unified',
                      hoverlabel={'bordercolor': '#ced1d6', 'font': {'size': 10, 'color': '#5e6063'}, 'namelength': 5},
                      margin=dict(l=0, r=0, t=30, b=60),
                      height=370,
                      dragmode=False,
                      selectdirection='h',
                      updatemenus=[
                          dict(
                              type="buttons",
                              direction="left",
                              buttons=list([
                                  dict(
                                      args=[{"visible": [True, False]},
                                            {"title": {'text': "<b>Casos acumulados por dia de notificação</b>",
                                                       'font': {'size': 13}, 'xanchor': 'center',
                                                       'yanchor': 'top', 'x': 0.5,
                                                       'y': 1, 'pad': dict(t=17, r=0, b=40, l=0)}}
                                            ],
                                      label="Diário",
                                      method="update"
                                  ),
                                  dict(
                                      args=[{"visible": [False, True]},
                                            {"title": {
                                                'text': "<b>Casos acumulados por semana de notificação</b>",
                                                'font': {'size': 13}, 'xanchor': 'center',
                                                'yanchor': 'top', 'x': 0.5, 'y': 1,
                                                'pad': dict(t=17, r=0, b=40, l=0)}}
                                            ],
                                      label="Semana Epidemiológica",
                                      method="update"
                                  )
                              ]),
                              pad={"r": 8, "t": 7},
                              showactive=True,
                              x=0.5,
                              xanchor="center",
                              y=-0.2,
                              yanchor="bottom",
                              font=dict(size=9)
                          )
                      ]
                                  )

    fig_graph_casos.update_xaxes(tickfont={'size':8})#, tickformatstops=[dict(dtickrange=[None,691200000], value='%d/%m/%Y'),
                                                                                    #dict(dtickrange=[691200000,None], value='%d/%b/%y')])
########### OBITOS
    fig_bar_novos_obitos = px.bar(df_moving_avg, x='datahora', y='obitos_novos', hover_data={'letalidade': True})  # , labels = {'newCases': 'Novos casos', 'newDeaths':'Novos óbitos'})

    fig_bar_novos_obitos.update_traces(hovertemplate='<b>Novos óbitos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[0]:.2%}', marker={'color': roxo, 'opacity': 0.5})#'#5dd4ff')#azul_observatorio)

    fig_bar_novos_obitos.add_trace(go.Scatter(
        x=df_moving_avg['datahora'],
        y=df_moving_avg['media_movel_obitos'],
        customdata=df_moving_avg['var_media_movel_obitos'],
        mode='lines',
        line=go.scatter.Line(color='#47029c'),
        showlegend=False,
        #xaxis_tickangle=0,
        #xaxis_tickfont={'size': 8},
        #xaxis_tickformat='%d/%b',
        # marker= {'size': 2, 'color': '#b80000'},
        name='',
        hovertemplate='<b>Média móvel</b> (7 dias): %{y}<br><b>Var. média móvel</b> (14 dias): %{customdata:.2%}'))

    # DIARIO
    fig_bar_novos_obitos.add_trace(go.Bar(
        x=dfplots['datahora'],
        y=dfplots['obitos_novos'],
        customdata=dfplots[['var_obitos_novos_semana', 'semana_epidem', 'letalidade']],
        showlegend=False,
        marker={'color': '#47029c', 'opacity': 0.75},
        name='',
        visible=False,
        hovertemplate='<b>Semana Epidem.</b>: %{customdata[1]}<br><b>Novos óbitos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[2]:.2%}<br><b>Var.</b> (ref. semana anterior): %{customdata[0]:.2%}'))

    fig_bar_novos_obitos.update_layout(title=dict(text='<b>Novos óbitos por dia de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=17, r=0, b=20, l=0)),
                             titlefont=dict(size=13),
                             yaxis=dict(rangemode='nonnegative'),
                             xaxis=dict(#rangeslider=dict(visible=True),
                                        range=[pd.to_datetime('11-04-2020', format='%d-%m-%Y'), gvars.latest_data + timedelta(days=1)]),
                             xaxis_title="",
                             yaxis_title="Novos óbitos",
                             hovermode='x unified',
                             hoverlabel={'bordercolor': '#ced1d6', 'font': {'size': 10, 'color': '#5e6063'}, 'namelength': 5},
                             margin=dict(l=0, r=0, t=30, b=60),
                             height=370,
                             dragmode=False,
                             selectdirection='h',
                             updatemenus=[
                                   dict(
                                       type="buttons",
                                       direction="left",
                                       buttons=list([
                                           dict(
                                               args=[{"visible": [True, True, False]},
                                                     {"title": {'text': "<b>Novos óbitos por dia de notificação</b>",
                                                                'font': {'size': 13}, 'xanchor': 'center',
                                                                'yanchor': 'top', 'x': 0.5,
                                                                'y': 1, 'pad': dict(t=17, r=0, b=40, l=0)}}
                                                     ],
                                               label="Diário | Média Móvel",
                                               method="update"
                                           ),
                                           dict(
                                               args=[{"visible": [False, False, True]},
                                                     {"title": {
                                                         'text': "<b>Novos óbitos por semana de notificação</b>",
                                                         'font': {'size': 13}, 'xanchor': 'center',
                                                         'yanchor': 'top', 'x': 0.5, 'y': 1,
                                                         'pad': dict(t=17, r=0, b=40, l=0)}}
                                                     ],
                                               label="Semana Epidemiológica",
                                               method="update"
                                           )
                                       ]),
                                       pad={"r": 8, "t": 7},
                                       showactive=True,
                                       x=0.5,
                                       xanchor="center",
                                       y=-0.2, #-0.54
                                       yanchor="bottom",
                                       font=dict(size=9)
                                   )
                               ]
                             )

    fig_bar_novos_obitos.update_xaxes(tickfont={'size':8})#, tickangle=0, tickformat='%b/%y')#, tickformatstops=[dict(dtickrange=[None,691200000], value='%d/%m/%Y'),
                                                                                   # dict(dtickrange=[691200000,None], value='%d/%b')])

    fig_graph_obitos = px.line(df_moving_avg, x='datahora', y='obitos', hover_data={'obitos_pc': True, 'letalidade': True})

    fig_graph_obitos.update_traces(mode="lines", hovertemplate='<b>Total de óbitos</b>: %{y:,}<br><b>Mortalidade</b> (100 mil hab.): %{customdata[0]:.1f}<br><b>Letalidade</b>: %{customdata[1]:.2%}', line=dict(color='#47029c', width=2))

    fig_graph_obitos.add_trace(go.Scatter(
        x=dfplots['datahora'],
        y=dfplots['obitos'],
        customdata= dfplots[['var_obitos_semana', 'semana_epidem', 'obitos_pc', 'letalidade']],
        mode='lines+markers',
        line=go.scatter.Line(color='#47029c', width=2.5),
        showlegend=False,
        marker={'size': 5, 'color': roxo, 'opacity':0.7},
        name='',
        visible=False,
        hovertemplate='<b>Semana Epidem.</b>: %{customdata[1]}<br><b>Total de óbitos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[3]:.2%}<br><b>Var.</b> (ref semana anterior): %{customdata[0]:.2%}')) # <b>Mortalidade</b> (100 mil hab.): %{customdata[2]:,.1f}<br>

    fig_graph_obitos.update_layout(title=dict(text='<b>Óbitos acumulados por dia de notificação</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=17, r=0, b=20, l=0)),
                                  titlefont=dict(size=13),
                                  yaxis=dict(rangemode='nonnegative'),
                                  xaxis_title="",
                                  yaxis_title="Óbitos acumulados",
                                  hovermode='x unified',
                                  hoverlabel={'bordercolor': '#ced1d6', 'font': {'size': 10, 'color': '#5e6063'}, 'namelength': 5},
                                  margin=dict(l=0, r=0, t=30, b=60),
                                  height=370,
                                  dragmode=False,
                                  selectdirection='h',
                                  updatemenus=[
                                       dict(
                                           type="buttons",
                                           direction="left",
                                           buttons=list([
                                               dict(
                                                   args=[{"visible": [True, False]},
                                                         {"title": {'text': "<b>Óbitos acumulados por dia de notificação</b>",
                                                                    'font': {'size': 13}, 'xanchor': 'center',
                                                                    'yanchor': 'top', 'x': 0.5,
                                                                    'y': 1, 'pad': dict(t=17, r=0, b=40, l=0)}}
                                                         ],
                                                   label="Diário",
                                                   method="update"
                                               ),
                                               dict(
                                                   args=[{"visible": [False, True]},
                                                         {"title": {
                                                             'text': "<b>Óbitos acumulados por semana de notificação</b>",
                                                             'font': {'size': 13}, 'xanchor': 'center',
                                                             'yanchor': 'top', 'x': 0.5, 'y': 1,
                                                             'pad': dict(t=17, r=0, b=40, l=0)}}
                                                         ],
                                                   label="Semana Epidemiológica",
                                                   method="update"
                                               )
                                           ]),
                                           pad={"r": 8, "t": 7},
                                           showactive=True,
                                           x=0.5,
                                           xanchor="center",
                                           y=-0.2,
                                           yanchor="bottom",
                                           font=dict(size=9)
                                       )
                                   ]
                                   )

    fig_graph_obitos.update_xaxes(tickfont={'size':8})#, tickformatstops=[dict(dtickrange=[None,691200000], value='%d/%m/%Y'),
                                                                                    #dict(dtickrange=[691200000,None], value='%d %b')])


    # Calculando o banco para a piramide de casos
    df_pir_m = df_pir_casos[df_pir_casos['cs_sexo'] == 'Masculino']
    df_pir_f = df_pir_casos[df_pir_casos['cs_sexo'] == 'Feminino']

    df_pir_m = df_pir_m.groupby('bins_idade').count().reset_index(drop=False)
    df_pir_m.rename(columns={"cs_sexo": "Masculino"}, inplace=True)

    df_pir_f = df_pir_f.groupby('bins_idade').count().reset_index(drop=False)
    df_pir_f.rename(columns={"cs_sexo": "Feminino"}, inplace=True)

    df_pir_casos = pd.merge(df_pir_m, df_pir_f, on='bins_idade', how='outer', sort=True)

    df_pir_casos['label'] = df_pir_casos.loc[:,'Masculino']
    df_pir_casos['Masculino'] = df_pir_casos['Masculino'] * -1

    # Calculando o banco para a piramide de obitos
    df_pir_m = df_pir_obitos[df_pir_obitos['cs_sexo'] == 'Masculino']
    df_pir_f = df_pir_obitos[df_pir_obitos['cs_sexo'] == 'Feminino']

    df_pir_m = df_pir_m.groupby('bins_idade').count().reset_index(drop=False)
    df_pir_m.rename(columns={"cs_sexo": "Masculino"}, inplace=True)

    df_pir_f = df_pir_f.groupby('bins_idade').count().reset_index(drop=False)
    df_pir_f.rename(columns={"cs_sexo": "Feminino"}, inplace=True)

    df_pir_obitos = pd.merge(df_pir_m, df_pir_f, on='bins_idade', how='outer', sort=True)

    df_pir_obitos['label'] = df_pir_obitos.loc[:, 'Masculino']
    df_pir_obitos['Masculino'] = df_pir_obitos['Masculino'] * -1

    max_pir_casos = df_pir_casos['label'].max()

    if max_pir_casos < df_pir_casos['Feminino'].max():
        max_pir_casos = df_pir_casos['Feminino'].max()

    max_pir_obitos = df_pir_obitos['label'].max()

    if max_pir_obitos < df_pir_obitos['Feminino'].max():
        max_pir_obitos = df_pir_obitos['Feminino'].max()

    # Calculando percentuais do total
    df_pir_casos['perc_masc'] = df_pir_casos['label'] / sum(df_pir_casos['label'])
    df_pir_casos['perc_fem'] = df_pir_casos['Feminino'] / sum(df_pir_casos['Feminino'])
    df_pir_obitos['perc_masc'] = df_pir_obitos['label'] / sum(df_pir_obitos['label'])
    df_pir_obitos['perc_fem'] = df_pir_obitos['Feminino'] / sum(df_pir_obitos['Feminino'])

    # Piramide Casos
    fig_piramide = go.Figure(go.Bar(
       y=df_pir_casos['bins_idade'],
       x=df_pir_casos['Masculino'],
       customdata=df_pir_casos[['label', 'perc_masc']],
       orientation='h',
       name='Homens',
       hoverinfo='x',
       marker=dict(color='#87ceeb', opacity=0.85),
       hovertemplate='%{customdata[0]:,}<br>% do total masculino: %{customdata[1]:.2%}'))

    fig_piramide.add_trace(go.Bar(
        y=df_pir_casos['bins_idade'],
        x=df_pir_casos['Feminino'],
        customdata=df_pir_casos[['perc_fem']],
        orientation='h',
        name='Mulheres',
        hoverinfo='x',
        marker=dict(color='plum', opacity=0.85),
        hovertemplate='%{x:,}<br>% do total feminino: %{customdata[0]:.2%}'))

    # Piramide Obitos
    fig_piramide.add_trace(go.Bar(
        y=df_pir_obitos['bins_idade'],
        x=df_pir_obitos['Masculino'],
        customdata=df_pir_obitos[['label', 'perc_masc']],
        orientation='h',
        name='Homens',
        hoverinfo='x',
        marker=dict(color='#87ceeb', opacity=0.85),
        hovertemplate='%{customdata[0]:,}<br>% do total masculino: %{customdata[1]:.2%}',
        visible=False))

    fig_piramide.add_trace(go.Bar(
        y=df_pir_obitos['bins_idade'],
        x=df_pir_obitos['Feminino'],
        customdata=df_pir_obitos[['perc_fem']],
        orientation='h',
        name='Mulheres',
        hoverinfo='x',
        marker=dict(color='plum', opacity=0.93),
        hovertemplate='%{x:,}<br>% do total feminino: %{customdata[0]:.2%}',
        visible=False))

    fig_piramide.update_layout(
                title=dict(text='<b>Pirâmide demográfica COVID-19</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=17, r=0, b=20, l=0)),
                titlefont=dict(size=13),
                hovermode='y unified',
                xaxis={'range': [-max_pir_casos-10, max_pir_casos+10], 'visible': False},
                hoverlabel={'bordercolor': '#ced1d6', 'font': {'size': 12, 'color': '#5e6063'}, 'namelength': 5},
                #yaxis=go.layout.YAxis(title='Idade'),
                #xaxis=go.layout.XAxis(
                       #range=[-1200, 1200],
                       #tickvals=[-1000, -700, -300, 0, 300, 700, 1000],
                       #ticktext=[1000, 700, 300, 0, 300, 700, 1000],
                #       title='Óbitos'),
                barmode='overlay',
                bargap=0.09,
                height=370,
                margin=dict(l=0, r=0, t=70, b=60),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.165,
                    xanchor="left",
                    x=0),
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        buttons=list([
                            dict(
                                args=[{"visible": [True, True, False, False]},
                                      {"xaxis": {
                                          "range": [-max_pir_casos-10, max_pir_casos+10],
                                          "visible": False
                                      }}
                                      ],
                                label="Casos",
                                method="update"
                            ),
                            dict(
                                args=[{"visible": [False, False, True, True]},
                                      {"xaxis": {
                                          "range": [-max_pir_obitos-10, max_pir_obitos+10],
                                          "visible": False
                                      }}
                                      ],
                                label="Óbitos",
                                method="update"
                            )
                        ]),
                        pad={"r": 8, "t": 7},
                        showactive=True,
                        x=0.5,
                        xanchor="center",
                        y=-0.2,
                        yanchor="bottom",
                        font=dict(size=9)
                    )
                ]
    )

    #df_comorb.rename(columns=lambda x: x.replace("_", " "))
    #df_comorb_columns = df_comorb_columns.str.replace("_", " ")
    #df_comorb_columns = df_comorb.columns.str.title()
    #df_comorb.columns = df_comorb_columns



    df_comorb = df_comorb.loc[:,['asma', 'cardiopatia', 'diabetes', 'doenca_hematologica', 'doenca_hepatica', 'doenca_neurologica', 'doenca_renal', 'imunodepressao', 'obesidade', 'outros_fatores_de_risco', 'pneumopatia', 'puerpera', 'sindrome_de_down']]

    df_comorb['soma_comorb'] = np.sum(df_comorb, axis=1)

    df_sem_comorb = df_comorb.loc[df_comorb['soma_comorb'] == 0, 'soma_comorb'].reset_index(drop=True)

    df_comorb['soma_comorb'] = 1

    df_comorb = df_comorb.groupby(by="soma_comorb").sum().reset_index(drop=True)

    df_comorb = df_comorb.transpose().reset_index(drop=False)

    df_comorb.columns = ['comorbidade', 'ocorrencias']

    df_comorb = df_comorb.append({'comorbidade': 'Sem Comorbidade', 'ocorrencias': len(df_sem_comorb)}, ignore_index=True)#.sort_values(by='ocorrencias', ascending=False, inplace=True)

    df_comorb['comorbidade'] = df_comorb['comorbidade'].str.replace("_", " ").str.title().str.replace("Doenca", "Doença").str.replace("De", "de").str.replace("Hematologica", "Hematológica").str.replace("Hepatica", "Hepática").str.replace("Neurologica", "Neurológica").str.replace("Imunodepressao", "Imunodepressão").str.replace("Puerpera", "Puérpera").str.replace("Sindrome", "Síndrome")


    total_comorb = sum(df_comorb['ocorrencias'])

    df_comorb['percent'] = df_comorb['ocorrencias']/total_comorb
    #ob_comorb = sum(df_comorb['ocorrencias'])

    #df_comorb.append({'comorbidade': "Sem Comorbidades", 'ocorrencias': len_df_comorb-ob_comorb}, ignore_index=True)
    #df_comorb.loc[len(df_comorb), 'comorbidade'] = 'Sem Comorbidade'
    #df_comorb.loc[len(df_comorb), 'ocorrencias'] = len_df_comorb - ob_comorb

    fig_comorbidades = px.bar(df_comorb, x='comorbidade', y='ocorrencias', hover_data={'percent': True})
    # fig_comorbidades = go.Figure(go.Bar(
    #     x=df_comorb['comorbidade'],
    #     y=df_comorb['ocorrencias'],
    #     #customdata=dfplots[['var_obitos_novos_semana', 'semana_epidem', 'letalidade']],
    #     showlegend=False,
    #     marker={'color': '#47029c', 'opacity': 0.75},
    #     #name='',
    #     visible=False))#,
        #hovertemplate='<b>Semana Epidem.</b>: %{customdata[1]}<br><b>Novos óbitos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[2]:.2%}<br><b>Var.</b> (ref. semana anterior): %{customdata[0]:.2%}'))

    fig_comorbidades.update_layout(
        title=dict(text='<b>Mortes da COVID-19 por Comorbidades</b>', xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=17, r=0, b=20, l=0)),
        titlefont=dict(size=13),
        yaxis=dict(rangemode='nonnegative'),
        xaxis_title="",
        yaxis_title="Óbitos",
        hovermode='x unified',
        hoverlabel={'bordercolor': '#ced1d6', 'font': {'size': 12, 'color': '#5e6063'}, 'namelength': 5},
        margin=dict(l=0, r=0, t=50, b=60),
        height=370,
        dragmode=False,
        selectdirection='h',
        xaxis={'categoryorder': 'total descending'})

    fig_comorbidades.update_traces(marker={'color': '#47029c', 'opacity': 0.85}, hovertemplate='%{y:,}<br>%{customdata[0]:.2%}')

    fig_comorbidades.update_xaxes(tickfont={'size': 10})

    return fig_bar_novos_casos, fig_graph_casos, fig_bar_novos_obitos, fig_graph_obitos, fig_piramide, fig_comorbidades



@app.callback(
    [Output('map_incidencia', 'figure'),
     Output('map_mortalidade', 'figure')],
    [Input('label_last_update', 'children'),
     Input('region_tabs', 'value'),
     Input('map_calendar', 'date'),
     Input('apply_filter', 'n_clicks'),
     Input('apply_filter_drs', 'n_clicks'),
     Input('table', 'data')],
    [State('table_filter', 'value'),
     State('table_filter_drs', 'value')],
    prevent_initial_call=True
)

@cache.memoize(timeout=86400)
def build_maps(label_last_update, region_tabs, selected_date, button, button2, table_data_trigger_refresh, selected_cities, selected_cities_drs):
    # selected_date = unixToDatetime(map_slider)
    # selected_date = selected_date.date()
    # selected_date = pd.to_datetime(selected_date, format="%Y-%m-%d")

    if not selected_cities:
        if selected_cities_drs:
            selected_cities=selected_cities_drs
    elif selected_cities == ['']:
        if selected_cities_drs:
            selected_cities=selected_cities_drs

    selected_date = pd.to_datetime(selected_date, format='%Y-%m-%d')

    df_missing_c_map = df_missing_c.loc[:,:]
    df_missing_c_map['datahora'] = selected_date

    if region_tabs == 'RMC':
        dfmaps = gvars.df_rmc_gdate.loc[gvars.df_rmc_gdate['datahora'] == pd.to_datetime(selected_date, format='%Y-%m-%d'), ['datahora', 'codigo_ibge', 'nome_munic', 'nome_drs', 'casos_pc', 'obitos_pc', 'casos', 'obitos', 'casos_novos', 'obitos_novos', 'letalidade']]

    elif region_tabs == 'DRS' or region_tabs == 'SP':
        dfmaps = gvars.df_gdate.loc[gvars.df_gdate['datahora'] == pd.to_datetime(selected_date, format='%Y-%m-%d'), ['datahora', 'codigo_ibge', 'nome_drs', 'nome_munic', 'casos_pc', 'obitos_pc', 'casos', 'obitos', 'casos_novos', 'obitos_novos', 'letalidade']]
        missing_cities = df_missing_c_map[~df_missing_c_map['codigo_ibge'].isin(dfmaps['codigo_ibge'])]
        dfmaps = pd.concat([dfmaps, missing_cities], sort=True, ignore_index=True)

    if region_tabs == 'DRS':
        if not selected_cities:
            dfmaps = dfmaps
        elif selected_cities == ['']:
            dfmaps = dfmaps
        else:
            dfmaps = dfmaps[dfmaps['nome_drs'].isin(selected_cities)]

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

    #dfmaps = dfmaps[dfmaps['datahora'] == str((unixToDatetime(map_slider)).strftime('%Y-%m-%d'))].reset_index(drop=True) # todo REMEMBER YOU COMMENTED THIS...


    max_scale_incidencia = dfmaps['casos_pc'].quantile(q=0.97)
    max_scale_obitos = dfmaps['obitos_pc'].quantile(q=0.97)

    if pd.to_datetime(selected_date, format='%Y-%m-%d') <= pd.to_datetime('2020-03-29', format='%Y-%m-%d'):
        max_scale_incidencia = 1

    if pd.to_datetime(selected_date, format='%Y-%m-%d') <= pd.to_datetime('2020-04-12', format='%Y-%m-%d'):
        max_scale_obitos = 1


    fig_map_incidencia = px.choropleth(data_frame= dfmaps,
                           geojson= gjson,
                           locations= 'codigo_ibge',
                           featureidkey= 'properties.id',  # properties.CD_GEOCMU
                           color= 'casos_pc',
                           #color_discrete_sequence= custom_colorscale_incidencia,
                           hover_data= {'nome_munic': True, 'nome_drs': True, 'casos': True, 'letalidade':True, 'codigo_ibge': False},  # ,
                           range_color= (0,max_scale_incidencia),
                           color_continuous_scale= custom_colorscale_incidencia)#'Reds')


    fig_map_incidencia.update_layout(title=dict(text="<b>Coeficiente de Incidência por Município</b>", xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=10, r=0, b=0, l=0)),
                                     coloraxis_colorbar=dict(title='', x=0, xanchor='left', lenmode='fraction', len=0.75, ticks='outside', thickness=14, tick0=0),
                                     margin=dict(l=0, r=0, b=0, t=40), titlefont=dict(size=12), height=300)

    if region_tabs == 'DRS':
        fig_map_incidencia.update_traces(hovertemplate="<b>Cidade</b>: %{customdata[0]}<br><b>DRS</b>: %{customdata[1]}<br><b>Incidência</b>: %{z:,.1f}<br><b>Total de casos</b>: %{customdata[2]:,}<br><b>Letalidade</b>: %{customdata[3]:.2%}", marker={'line': {'color': 'white', 'width': 0.4}})
    else:
        fig_map_incidencia.update_traces(hovertemplate='<b>Cidade</b>: %{customdata[0]}<br><b>Incidência</b>: %{z:,.1f}<br><b>Total de casos</b>: %{customdata[2]:,}<br><b>Letalidade</b>: %{customdata[3]:.2%}', marker={'line': {'color': 'white', 'width': 0.4}})
    #<br> Novos casos: % {customdata[3]} <br> Letalidade: % {customdata[4]}
    fig_map_incidencia.update_geos(showframe=False, showcountries=False, showcoastlines=False, showland=True, fitbounds='locations')


    ### Mapa mortalidade
    fig_map_mortalidade = px.choropleth(data_frame=dfmaps,
                           geojson=gjson,
                           locations='codigo_ibge',
                           featureidkey='properties.id',  # properties.CD_GEOCMU
                           color='obitos_pc',
                           #color_discrete_sequence= custom_colorscale_incidencia,
                           hover_data={'nome_munic': True, 'nome_drs': True, 'obitos': True, 'letalidade': True, 'codigo_ibge': False},  # ,
                           range_color=(0,max_scale_obitos),
                           color_continuous_scale=custom_colorscale_mortalidade)#'Oranges')

    fig_map_mortalidade.update_layout(title=dict(text="<b>Coeficiente de Mortalidade por Município</b>", xanchor='center', yanchor='top', x=0.5, y=1, pad=dict(t=10, r=0, b=0, l=0)),
                                      coloraxis_colorbar=dict(title='', xanchor='right', lenmode='fraction', len=0.75, ticks='outside', thickness=14, tick0=0),
                                      margin=dict(l=0, r=0, b=0, t=40), titlefont=dict(size=12), height=300)#, pad=0))

    if region_tabs == 'DRS':
        fig_map_mortalidade.update_traces(hovertemplate='<b>Cidade</b>: %{customdata[0]}<br><b>DRS</b>: %{customdata[1]}<br><b>Mortalidade</b>: %{z:,.1f}<br><b>Total de óbitos</b>: %{customdata[2]:,}<br><b>Letalidade</b>: %{customdata[3]:.2%}', marker={'line': {'color': 'white', 'width': 0.4}})#, marker_line_size=1)
    else:
        fig_map_mortalidade.update_traces(hovertemplate='<b>Cidade</b>: %{customdata[0]}<br><b>Mortalidade</b>: %{z:,.1f}<br><b>Total de óbitos</b>: %{customdata[2]:,}<br><b>Letalidade</b>: %{customdata[3]:.2%}', marker={'line': {'color': 'white', 'width': 0.4}})#, marker_line_size=1)

    fig_map_mortalidade.update_geos(showframe=False, showcountries=False, showcoastlines=False, showland=True, fitbounds='locations')

    if region_tabs == 'RMC':
        fig_map_incidencia.update_traces(marker={'line': {'width': 1}})
        fig_map_mortalidade.update_traces(marker={'line': {'width': 1}})


    return fig_map_incidencia, fig_map_mortalidade



@app.callback(
    Output('today_indicators', 'figure'),
    [Input('label_last_update', 'children'),
     Input('region_tabs', 'value')],
    prevent_initial_call=True
)

@cache.memoize(timeout=86400)
def update_today_indicators(label_last_update, region_tabs):

    # today = date.today()
    today_ind = pd.to_datetime(gvars.latest_data, format='%Y-%m-%d')# TEMP
    yesterday = today_ind - timedelta(days=7) ### !!!!!!!! CHANGED to days=2 to comply with the temporary dfyesterday as dftoday
    today_ind = today_ind.strftime('%Y-%m-%d')
    yesterday = yesterday.strftime('%Y-%m-%d')

    if region_tabs == 'RMC':
        # !!!!!!!!! TEMPORARILY STORING dfyesterday as dftoday (WHILE I DONT IMPLEMENT A FALL-BACK IF THERES NO DATA TODAY)
        dftoday = gvars.dftcrmc_ind[gvars.dftcrmc_ind['datahora'] == today_ind]
        dfyesterday = gvars.dftcrmc_ind[gvars.dftcrmc_ind['datahora'] == yesterday]

    elif region_tabs == 'SP' or region_tabs == 'DRS':
        # !!!!!!!!! TEMPORARILY STORING dfyesterday as dftoday (WHILE I DONT IMPLEMENT A FALL-BACK IF THERES NO DATA TODAY)
        dftoday = gvars.dftc_ind[gvars.dftc_ind['datahora'] == today_ind] # todo update indicators to fetch latest data
        dfyesterday = gvars.dftc_ind[gvars.dftc_ind['datahora'] == yesterday]

    dftoday.loc[:, 'letalidade'] = dftoday['obitos'] / dftoday['casos']
    dfyesterday.loc[:, 'letalidade'] = dfyesterday['obitos'] / dfyesterday['casos']

    dftoday.loc[:, 'casos_pc'] = dftoday.loc[:, 'casos'] / (dftoday.loc[:, 'pop'] / 100000)
    dftoday.loc[:, 'obitos_pc'] = dftoday.loc[:, 'obitos'] / (dftoday.loc[:, 'pop'] / 100000)
    dftoday.loc[:, 'casos_pc'] = dftoday['casos_pc'].round(decimals=0)
    dftoday.loc[:, 'obitos_pc'] = dftoday['obitos_pc'].round(decimals=0)
    dfyesterday.loc[:, 'casos_pc'] = dfyesterday.loc[:, 'casos'] / (dfyesterday.loc[:, 'pop'] / 100000)
    dfyesterday.loc[:, 'obitos_pc'] = dfyesterday.loc[:, 'obitos'] / (dfyesterday.loc[:, 'pop'] / 100000)
    dfyesterday.loc[:, 'casos_pc'] = dfyesterday['casos_pc'].round(decimals=0)
    dfyesterday.loc[:, 'obitos_pc'] = dfyesterday['obitos_pc'].round(decimals=0)

    fontsize_ind = 24
    fontsize_title_ind = 12

    fig_ind = go.Figure()
    #fig_ind_r2 = go.Figure()
    #fig_ind_r3= go.Figure()

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos'].to_numpy()[0],
        number = {'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Total de casos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 0}),

        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_novos'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Novos casos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 1})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_pc'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Casos por<br>100 mil habitantes', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_pc'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 2})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Total de óbitos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 3})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_novos'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}}, # 'valueformat': ',',
        title = {'text': 'Novos óbitos<br>', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 4})
        )

    fig_ind.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_pc'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
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
     Input('region_tabs', 'value')],
    prevent_initial_call=True
)

@cache.memoize(timeout=86400)
def update_today_indicators_mobile(label_last_update, region_tabs):

    # today = date.today()
    today_ind = pd.to_datetime(gvars.latest_data, format='%Y-%m-%d')
    yesterday = today_ind - timedelta(days=7)
    today_ind = today_ind.strftime('%Y-%m-%d')
    yesterday = yesterday.strftime('%Y-%m-%d')

    if region_tabs == 'RMC':
        dftoday = gvars.dftcrmc_ind[gvars.dftcrmc_ind['datahora'] == today_ind]
        dfyesterday = gvars.dftcrmc_ind[gvars.dftcrmc_ind['datahora'] == yesterday]

    elif region_tabs == 'SP' or region_tabs == 'DRS':
        dftoday = gvars.dftc_ind[gvars.dftc_ind['datahora'] == today_ind]
        dfyesterday = gvars.dftc_ind[gvars.dftc_ind['datahora'] == yesterday]

    dftoday.loc[:, 'letalidade'] = dftoday['obitos'] / dftoday['casos']
    dfyesterday.loc[:, 'letalidade'] = dfyesterday['obitos'] / dfyesterday['casos']

    dftoday.loc[:,'casos_pc']= dftoday.loc[:,'casos']/(dftoday.loc[:,'pop']/100000)
    dftoday.loc[:,'obitos_pc']= dftoday.loc[:,'obitos']/(dftoday.loc[:,'pop']/100000)
    dftoday.loc[:,'casos_pc']= dftoday['casos_pc'].round(decimals=0)
    dftoday.loc[:,'obitos_pc']= dftoday['obitos_pc'].round(decimals=0)
    dfyesterday.loc[:,'casos_pc']= dfyesterday.loc[:,'casos']/(dfyesterday.loc[:,'pop']/100000)
    dfyesterday.loc[:,'obitos_pc']= dfyesterday.loc[:,'obitos']/(dfyesterday.loc[:,'pop']/100000)
    dfyesterday.loc[:,'casos_pc']= dfyesterday['casos_pc'].round(decimals=0)
    dfyesterday.loc[:,'obitos_pc']= dfyesterday['obitos_pc'].round(decimals=0)


    fontsize_ind = 20
    fontsize_title_ind = 10

    fig_ind_r1 = go.Figure()
    fig_ind_r2 = go.Figure()
    fig_ind_r3= go.Figure()

    fig_ind_r1.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos'].to_numpy()[0],
        number = {'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Total de casos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 0}),

        )

    fig_ind_r1.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_novos'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Novos casos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 1})
        )

    fig_ind_r1.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['casos_pc'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Casos por<br>100 mil habitantes', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['casos_pc'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 2})
        )

    fig_ind_r2.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Total de óbitos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 0})
        )

    fig_ind_r2.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_novos'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
        title = {'text': 'Novos óbitos', 'font': {'size': fontsize_title_ind}},
        delta = {'reference': dfyesterday['obitos_novos'].to_numpy()[0], 'increasing': {'color': '#d72a24'}, 'decreasing': {'color': 'green'}, 'relative': True},
        domain = {'row': 0, 'column': 1})
        )

    fig_ind_r2.add_trace(
        go.Indicator(
        mode = 'number+delta',
        value = dftoday['obitos_pc'].to_numpy()[0],
        number={'valueformat': ',', 'font': {'size': fontsize_ind}},
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
    [Input('button_print', 'n_clicks')],
    prevent_initial_call=True)

def printpdf(x):
    if x:
        return "window.print()"
    return ""



# @app.callback(
#     Output('r0_graphs', 'figure'),
#     [Input('label_last_update', 'children'),
#      Input('region_tabs', 'value')],
# )
#
# def build_r0_graphs(latest_data, region_tabs):
#
#     # Fetching initial Data Frames from gvars
#     #df_r0_sp = gvars.df.groupby('datahora').agg({'casos': 'sum'}).reset_index(drop=False)
#
#     #df_r0_drs = gvars.df_drs_gdate.loc[:,['nome_drs','datahora', 'casos']]
#
#     #df_r0_rmc = gvars.df_rmc.loc[:,['datahora', 'casos']]
#
#
#     # Calculating the ML value as well as the confidence intervals
#     #df_plot_r0 = get_R0(latest_date=latest_data, dfrmc=df_r0_rmc, dfdrs=df_r0_drs, dfsp=df_r0_sp)
#
#
#     # PLOT PLOT PLOT
#
#     #df_plot_r0 = df_plot_r0[df_plot_r0['state'] == 'RMC']
#     df_plot_r0 = pd.read_csv('df_r0_Campinas_27OUT_v3.csv') #27_out_GAMMA1.csv')
#
#
#
#     df_plot_r0 = df_plot_r0.loc[df_plot_r0['state'] == 'Campinas', :]  #'Campinas', :]
#
#     fig_r0 = go.Figure()
#
#     # df_plot_r0.index.get_level_values('date')
#     fig_r0.add_trace(go.Scatter(x=df_plot_r0['date'], y=df_plot_r0['ML'], mode='markers+lines'))#, color=df_plot_r0['ML'],
#                                 #colorscale=[[0, 'rgb(191,191,191)'], [1, 'rgb(217,56,20)']]))
#
#     fig_r0.update_traces(
#         hovertemplate="<b>R0</b>: %{y:,}<br>")#,)
#         #marker={'color': cyan, 'opacity': 0.5})  # azul_observatorio)
#     # )
#
#     # fig_bar_novos_casos.add_trace(go.Scatter(
#     #     x=df_moving_avg['datahora'],
#     #     y=df_moving_avg['media_movel_casos'],
#     #     customdata=df_moving_avg[['var_media_movel_casos', 'semana_epidem']],
#     #     mode='lines',
#     #     line=go.scatter.Line(color='#277373'),
#     #     showlegend=False,
#     #     text=df_moving_avg['var_media_movel_casos'],
#     #     name='',
#     #     hovertemplate='<b>Média móvel</b> (7 dias): %{y:,}<br><b>Var. média móvel</b> (14 dias): %{text:.2%}'))
#     #
#     # # SEMANAL
#     # fig_bar_novos_casos.add_trace(go.Bar(
#     #     x=dfplots['datahora'],
#     #     y=dfplots['casos_novos'],
#     #     customdata=dfplots[['var_casos_novos_semana', 'semana_epidem', 'letalidade']],
#     #     showlegend=False,
#     #     marker={'color': cyan, 'opacity': 0.75},
#     #     name='',
#     #     visible=False,
#     #     hoverinfo='all',
#     #     hovertemplate='<b>Semana Epidem.</b>: %{customdata[1]}<br><b>Novos casos</b>: %{y:,}<br><b>Letalidade</b>: %{customdata[2]:.2%}<br><b>Var.</b> (ref. semana anterior): %{customdata[0]:.2%}'))
#
#     fig_r0.update_layout(
#         title=dict(text='<b>R0</b>', xanchor='center', yanchor='top', x=0.5, y=1,
#                    pad=dict(t=17, r=0, b=20, l=0)),
#         titlefont=dict(size=13),
#         xaxis_title="",
#         yaxis=dict(rangemode='nonnegative'),
#         yaxis_title="R0",
#         hovermode='x unified',
#         margin=dict(l=0, r=0, t=30, b=60),
#         height=370,
#         dragmode=False,
#         selectdirection='h',
#         hoverlabel={'bordercolor': '#ced1d6', 'font': {'size': 10, 'color': '#5e6063'}, 'namelength': 5},
#         # xaxis_tickformat='%d %b',
#         # updatemenus=[
#         #     dict(
#         #         type="buttons",
#         #         direction="left",
#         #         buttons=list([
#         #             dict(
#         #                 args=[{"visible": [True, True, False]},
#         #                       {"title": {'text': "<b>Novos casos por dia de notificação</b>", 'font': {'size': 13},
#         #                                  'xanchor': 'center', 'yanchor': 'top', 'x': 0.5,
#         #                                  'y': 1, 'pad': dict(t=17, r=0, b=40, l=0)}}
#         #                       ],
#         #                 label="Diário | Média Móvel",
#         #                 method="update"
#         #             ),
#         #             dict(
#         #                 args=[{"visible": [False, False, True]},
#         #                       {"title": {'text': "<b>Novos casos por semana de notificação</b>", 'font': {'size': 13},
#         #                                  'xanchor': 'center',
#         #                                  'yanchor': 'top', 'x': 0.5, 'y': 1, 'pad': dict(t=17, r=0, b=40, l=0)}}
#         #                       ],
#         #                 label="Semana Epidemiológica",
#         #                 method="update"
#         #             )
#         #         ]),
#         #         pad={"r": 7, "t": 8},
#         #         showactive=True,
#         #         x=0.5,
#         #         xanchor="center",
#         #         y=-0.2,
#         #         yanchor="bottom",
#         #         font=dict(size=9)
#         #     )
#         # ])
#     )
#
#     fig_r0.update_xaxes(tickfont={'size': 8})
#
#     return fig_r0


# @app.callback(
#     Output('javascript', 'run'),
#     [Input('button_print', 'n_clicks')])
# def printpdf(x):
#     if x:
#         opt= {'javascript-delay': 1000, 'no-stop-slow-scripts': None, 'debug-javascript': None}
#         pdfkit.from_string(app.layout, 'test.pdf', options=opt)
#         return "window.print()"
#     return ""

# if __name__ == '__main__':
#    app.run_server(host="127.0.0.1", debug=True, port=8080)



if __name__ == '__main__':
     app.run_server(host="0.0.0.0", port=8080, debug=False)#, use_reloader=False)