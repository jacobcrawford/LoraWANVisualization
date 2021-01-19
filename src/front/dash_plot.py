import re
from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import datetime as dt

from src.geo_json.lora_geo_json import getLoraGEOJson
from src.storage import loradb_connecter

# https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth_mapbox.html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

center_coors = 55.579209, 9.510841 #TODO plot another center


device_selectors = [{'label':device_id, 'value': device_id } for device_id in loradb_connecter.getAllUniqueDeviceIds()]
device_selectors.append({'label':"Show all", 'value': 'None'})


gateway_selectors = [{'label':gateway_id, 'value': gateway_id } for gateway_id in loradb_connecter.getAllUniqueGatewayIds()]
gateway_selectors.append({'label':"Show all", 'value': 'None'})

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div("Select date interval to show only data collected in that interval"),
    html.Div([
        dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2021, 1, 12),
        max_date_allowed=date.today(),
        initial_visible_month=date(2021, 1, 1),
        end_date=date.today(),
        start_date=date(2021, 1, 12)
    ),
    ]),
    html.Div("Select device_id to show only data collected by that device"),
    html.Div(
        style={'width': "400px"},
        children=[
            dcc.Dropdown(
            id='device-id-dropdown',
            options=device_selectors,
            value='None',),
            ]
    ),
    html.Div("Select gateway_id to show only data collected from that gateway"),
    html.Div(
        style={'width': "400px"},
        children=[
            dcc.Dropdown(
            id='gateway-id-dropdown',
            options=gateway_selectors,
            value='None'),
            ]
    ),
    dcc.Graph(id='graph-id'),
    html.Div(id="update-id"),
    dcc.Interval(
            id='interval-component',
            interval=1*30000, # in milliseconds
            n_intervals=0
        )
])

@ app.callback(
    dash.dependencies.Output('graph-id', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('device-id-dropdown', 'value'),
     dash.dependencies.Input('gateway-id-dropdown', 'value'),
     dash.dependencies.Input('interval-component', 'n_intervals'),
     ]
)
def refreshGraph(start_date, end_date, device_id_selected,gateway_id_selected,_):
    device_id = str( device_id_selected) if  device_id_selected != 'None' else None
    gateway_id = str( gateway_id_selected) if  gateway_id_selected != 'None' else None

    geojson, df = getLoraGEOJson(from_time=start_date, to_time=end_date,device_id=device_id, gateway_id=gateway_id)
    fig = px.choropleth_mapbox(
        df, geojson=geojson,
        locations="Signal",
        featureidkey="properties.title",
        center={"lat": center_coors[0], "lon": center_coors[1]},
        zoom=8,
        color="Signal",
        range_color=(-140, -50),
        opacity=0.5,
        height=800,
        width=800)
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_style="carto-positron"),
    return fig



@ app.callback(
    dash.dependencies.Output('update-id', component_property='children'),
    [dash.dependencies.Input('interval-component', 'n_intervals'),]
)
def setLastUpdates(n):
    t = dt.datetime.now() + dt.timedelta(hours=1)
    date_string = dt.datetime.strftime(t, "%d-%B-%Y %H:%M:%S")
    return f"Last updated at {date_string}"
