# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 07:44:15 2020

@author: RanjaniSubramanyan
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

#%%
# import excel sheets to load information about confirmed, death and recovered cases to display it in a table
CONFIRMED_GLOBAL = pd.read_csv('time_series_covid19_confirmed_global.csv')
DEATH_GLOBAL = pd.read_csv('time_series_covid19_deaths_global.csv')
RECOVERED_GLOBAL = pd.read_csv('time_series_covid19_recovered_global.csv')

CONSOLIDATED_DF = CONFIRMED_GLOBAL.iloc[:, 0:4]
CONSOLIDATED_DF['Confirmed'] = CONFIRMED_GLOBAL.iloc[:, -1]
CONSOLIDATED_DF['Deaths'] = DEATH_GLOBAL.iloc[:, -1]
CONSOLIDATED_DF['Recovered'] = RECOVERED_GLOBAL.iloc[:, -1]
CONSOLIDATED_DF['Active'] = CONSOLIDATED_DF['Confirmed'] - CONSOLIDATED_DF['Recovered'] - CONSOLIDATED_DF['Deaths']
GLOBAL_AGG = CONSOLIDATED_DF.groupby(['Country/Region'], as_index=False).sum()
# sort for the top 10 affected countries according to the last date (5th April, 2020)
GLOBAL_AGG = GLOBAL_AGG.sort_values(['Confirmed'], ascending= (False))
DISPLAY_DF = GLOBAL_AGG.drop(['Lat', 'Long'], axis=1)
#%%
# to plot graph for overall global status
CONFIRMED_GLOBAL_AGG = CONFIRMED_GLOBAL.groupby(['Country/Region'], as_index=False).sum()
DEATH_GLOBAL_AGG = DEATH_GLOBAL.groupby(['Country/Region'], as_index=False).sum()
RECOVERED_GLOBAL_AGG = RECOVERED_GLOBAL.groupby(['Country/Region'], as_index=False).sum()
CONFIRMED_GLOBAL_AGG_TR = CONFIRMED_GLOBAL_AGG.transpose().drop(['Country/Region', 'Lat', 'Long']).sum(axis=1).to_frame()
CONFIRMED_GLOBAL_AGG_TR.columns = ['Confirmed']
DEATH_GLOBAL_AGG_TR = DEATH_GLOBAL_AGG.transpose().drop(['Country/Region', 'Lat', 'Long']).sum(axis=1).to_frame()
DEATH_GLOBAL_AGG_TR.columns = ['Death']
RECOVERED_GLOBAL_AGG_TR = RECOVERED_GLOBAL_AGG.transpose().drop(['Country/Region', 'Lat', 'Long']).sum(axis=1).to_frame()
RECOVERED_GLOBAL_AGG_TR.columns = ['Recovered']
CONFIRMED_GLOBAL_AGG_TR['Death'] = DEATH_GLOBAL_AGG_TR['Death']
CONFIRMED_GLOBAL_AGG_TR['Recovered'] = RECOVERED_GLOBAL_AGG_TR['Recovered']
#%%
# dropdown list countries
list_of_countries = GLOBAL_AGG['Country/Region'].unique()
#%%
WORST_CONFIRMED = CONFIRMED_GLOBAL_AGG.sort_values(by=CONFIRMED_GLOBAL_AGG.columns[-1], ascending=(False))
worst_x = WORST_CONFIRMED.iloc[0:10, 3:]
n = WORST_CONFIRMED.iloc[0:10, 3:].shape[1]
def SetColor(x):
        if(x < 10):
            return "white"
        elif(10 <= x < 100):
            return "#ff7f0e"
        elif(100<= x <=10000):
            return "#8c564b"
        elif(x > 10000):
            return "#d62728"
trace = []
for i in range(0, 10):
    worst_y = [WORST_CONFIRMED.iloc[i, 0]] * n
    trace.append(go.Scatter(x=list(WORST_CONFIRMED.columns.values)[3:], y=worst_y, # Data
                        mode='markers', name=WORST_CONFIRMED.iloc[i, 0],
                        text = str(WORST_CONFIRMED.iloc[i, 0])  + ' : ' + str(WORST_CONFIRMED.iloc[i, -1]), hoverinfo = 'text',
                        marker = dict(size=8, color=list(map(SetColor, WORST_CONFIRMED.iloc[i, 3:]))),
                        #hovertemplate = '%{}',
                        line=dict(color='rgb(200,200,200)')))
layout = dict(title='Top 10 affected countries in the world', xaxis=dict(title='Date over the year 2020'), 
              yaxis=dict(title='Affected country'), hovermode="x unified")
fig = go.Figure(data=trace, layout=layout)
#%%
# main page
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H4(children='COVID-19 (Global Status)',
            style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        dcc.Graph(
        id='worst 10 countries',
        figure=fig
    ),
        html.Div(children='Select a country to get more information', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
        html.Div(dcc.Dropdown(
                id='country-list',
                options=[{'label': i, 'value': i} for i in list_of_countries],
                value='India'
            ),
        ),
        html.Div(dcc.Graph(id='country-graph')),
        
])
@app.callback(
Output('country-graph', 'figure'), 
[Input('country-list', 'value')]
)
def update_graph(value):
    number_confirmed = CONFIRMED_GLOBAL_AGG.loc[CONFIRMED_GLOBAL_AGG['Country/Region'].str.match(value)].iloc[:, 4:].transpose()
    number_confirmed.columns = ['Confirmed']
    number_recovered = RECOVERED_GLOBAL_AGG.loc[RECOVERED_GLOBAL_AGG['Country/Region'].str.match(value)].iloc[:, 4:].transpose()
    number_recovered.columns = ['Recovered']
    number_death = DEATH_GLOBAL_AGG.loc[DEATH_GLOBAL_AGG['Country/Region'].str.match(value)].iloc[:, 4:].transpose()
    number_death.columns = ['Death']
    title_country = 'Status in ' + value
    return {
            'data': [
                go.Scatter(
                      x=number_confirmed.index,
                      y=number_confirmed['Confirmed'],
                      line=dict(color='rgb(255, 0, 0)'),
                      opacity=0.8,
                      name='Confirmed'),
                go.Scatter(
                      x=number_recovered.index,
                      y=number_recovered['Recovered'],
                      line=dict(color='rgb(0, 255, 0)'),
                      opacity=0.8,
                      name='Recovered'),
                go.Scatter(
                      x=number_death.index,
                      y=number_death['Death'],
                      line=dict(color='rgb(0, 0, 255)'),
                      opacity=0.8,
                      name='Death'),
            ],
            'layout': go.Layout(title=title_country, 
                                xaxis_title='Days in the year', yaxis_title='Number of people')
        }
"""
@app.callback(
Output('worst 10 countries', 'figure'), 
[Input('worst 10 countries', 'hoverData')]
)
def update_(hoverData):
    label = []
    for i in hoverData['points']:
        text = str(WORST_CONFIRMED[0:10]['Country/Region']) + ' : ' + str(WORST_CONFIRMED[0:10][i['x']])
        label.append(text)
    #print(label)"""
if __name__ == '__main__':
    app.run_server(debug=True)

