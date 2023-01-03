#Import all modules
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from flask import Flask
import plotly.express as px
import dash_daq as daq
import pandas as pd
import numpy as np
import requests
import yfinance as yf


#Initiate the app
server=Flask(__name__)
app=dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.UNITED, dbc.icons.BOOTSTRAP])
server=app.server
#for running on render


#Read the files
data = yf.Ticker("TSLA")
df = data.history(period="max")
df.reset_index(inplace=True)
df['Year'] = pd.DatetimeIndex(df['Date']).year
df['Month'] = pd.DatetimeIndex(df['Date']).month



#Build the header component
header_component=html.H1("Stock Price App", style={'color':'darkcyan', 'text-align':'center', 'font-size':'72px'})



#Define Options
month_options=df['Month'].unique()
year_options=df['Year'].unique()



#Design Layout
app.layout=html.Div([
    dbc.Row([header_component]),
    dbc.Row([dbc.Col([html.H2("Choose Year", style={'color':'darkcyan', 'text-align':'left', 'font-size':'30px'})]),
            dbc.Col([html.H2("Choose Month", style={'color':'darkcyan', 'text-align':'left', 'font-size':'30px'})])]),

    dbc.Row([dbc.Col([dcc.Checklist(["All Years"], [], id="year-all-checklist", inline=True),
                dcc.Checklist(year_options, [], id="year-checklist", inline=True)]),

            dbc.Col([dcc.Checklist(["All Months"], [], id="month-all-checklist", inline=True),
                dcc.Checklist(month_options, [], id="month-checklist", inline=True)])]),

    dbc.Row([html.H3("Choose Plot Variable", style={'color':'darkcyan', 'text-align':'center', 'font-size':'36px'})]),

    dbc.Row([
        dcc.Dropdown(id='x-axis-dropdown', 
                        options=[
                            {'label':i, 'value':i}
                            for i in df.columns
                        ], value=None)
    ]),

    dbc.Row([html.H3("Choose Stock", style={'color':'darkcyan', 'text-align':'center', 'font-size':'36px'})]),

    dbc.Row([
        dcc.Dropdown(
            id='stock-dropdown',
            options=[
                {'label': 'Tesla, Inc.', 'value': 'TSLA'},
                {'label': 'Amazon.com, Inc.', 'value': 'AMZN'},
                {'label': 'Meta Platforms, Inc.', 'value': 'META'},
                {'label': 'Netflix, Inc', 'value': 'NFLX'},
                {'label': 'Alphabet Inc.', 'value': 'GOOG'},
                {'label': 'Apple Inc.', 'value': 'AAPL'}
            ], value='TSLA'       
        )
    ]),

    dbc.Row(dcc.Graph(id='line-graph')),

    dbc.Row([html.H3("At a Glance", style={'color':'darkcyan', 'text-align':'center', 'font-size':'36px'})]),

    dbc.Row([
        dbc.Col([daq.LEDDisplay(
        id='open',
        label="Open",
        value=df['Open'].values[-1]
    )]),
        dbc.Col([daq.LEDDisplay(
        id='high',
        label="High",
        value=df['High'].values[-1]
    )]),
        dbc.Col([daq.LEDDisplay(
        id='low',
        label="Low",
        value=df['Low'].values[-1]
    )]),
        dbc.Col([daq.LEDDisplay(
        id='close',
        label="Close",
        value=df['Close'].values[-1]
    )]),
        dbc.Col([daq.LEDDisplay(
        id='volume',
        label="Volume",
        value=df['Volume'].values[-1]
    )])
    ])
])



#Callback for syncing year checklist
@app.callback(
    Output("year-checklist", "value"),
    Output("year-all-checklist", "value"),
    Input("year-checklist", "value"),
    Input("year-all-checklist", "value"),
)
def sync_checklists(years_selected, all_selected):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "year-checklist":
        all_selected = ["All Years"] if set(years_selected) == set(year_options) else []
    else:
        years_selected = year_options if all_selected else []
    return years_selected, all_selected



#Callback for syncing months checklist
@app.callback(
    Output("month-checklist", "value"),
    Output("month-all-checklist", "value"),
    Input("month-checklist", "value"),
    Input("month-all-checklist", "value"),
)
def sync_checklists(months_selected, all_selected):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "month-checklist":
        all_selected = ["All Months"] if set(months_selected) == set(month_options) else []
    else:
        months_selected = month_options if all_selected else []
    return months_selected, all_selected



#Callback for Line Graph
@app.callback(
    Output(component_id='line-graph', component_property='figure'),
    Input(component_id='x-axis-dropdown', component_property='value'),
    Input(component_id='year-checklist', component_property='value'),
    Input(component_id='month-checklist', component_property='value'),
    Input(component_id='stock-dropdown', component_property='value'),
)
def update_graph(x_axis, selected_year, selected_month, selected_stock):

    data = yf.Ticker(selected_stock)
    df = data.history(period="max")
    df.reset_index(inplace=True)
    df['Year'] = pd.DatetimeIndex(df['Date']).year
    df['Month'] = pd.DatetimeIndex(df['Date']).month

    dff = df[(df['Year'].isin(selected_year)) & (df['Month'].isin(selected_month))]
    line_fig=px.line(dff,
                   x='Date', y=x_axis,
                   title=f'Plot of {x_axis} ')
    return line_fig



#Callback for Open Values
@app.callback(
    Output('open', 'value'),
    Input('stock-dropdown', 'value')
)
def update_output(selected_stock):
    data = yf.Ticker(selected_stock)
    df = data.history(period="max")
    df.reset_index(inplace=True)
    value = df['Open'].values[-1]
    return str(value)



#Callback for High Values
@app.callback(
    Output('high', 'value'),
    Input('stock-dropdown', 'value')
)
def update_output(selected_stock):
    data = yf.Ticker(selected_stock)
    df = data.history(period="max")
    df.reset_index(inplace=True)
    value = df['High'].values[-1]
    return str(value)



#Callback for Low Values
@app.callback(
    Output('low', 'value'),
    Input('stock-dropdown', 'value')
)
def update_output(selected_stock):
    data = yf.Ticker(selected_stock)
    df = data.history(period="max")
    df.reset_index(inplace=True)
    value = df['Low'].values[-1]
    return str(value)



#Callback for Close Values
@app.callback(
    Output('close', 'value'),
    Input('stock-dropdown', 'value')
)
def update_output(selected_stock):
    data = yf.Ticker(selected_stock)
    df = data.history(period="max")
    df.reset_index(inplace=True)
    value = df['Close'].values[-1]
    return str(value)



#Callback for Volume Values
@app.callback(
    Output('volume', 'value'),
    Input('stock-dropdown', 'value')
)
def update_output(selected_stock):
    data = yf.Ticker(selected_stock)
    df = data.history(period="max")
    df.reset_index(inplace=True)
    value = df['Volume'].values[-1]
    return str(value)


#Run app
app.run_server(debug=True)#True/False
