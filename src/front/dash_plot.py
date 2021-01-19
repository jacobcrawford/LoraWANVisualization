import re
from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from src.geo_json.lora_geo_json import getLoraGEOJson
from src.storage import loradb_connecter

# https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth_mapbox.html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

center_coors = 55.579209, 9.510841 #TODO plot another center

device_ids = loradb_connecter.getAllUniqueDeviceIds()
device_selectors = [{'label':device_id, 'value': device_id } for device_id in device_ids]
device_selectors.append({'label':"Show all", 'value': 'None'})

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
            value='None',
    ),
    ]),
    dcc.Graph(id='graph-id')
])

@ app.callback(
    dash.dependencies.Output('graph-id', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('device-id-dropdown', 'value')]
)
def refreshGraph(start_date, end_date, value):
    device_id = str(value) if value != 'None' else None
    geojson, df = getLoraGEOJson(from_time=start_date, to_time=end_date,device_id=device_id)
    fig = px.choropleth_mapbox(
        df, geojson=geojson,
        locations="Signal",
        featureidkey="properties.title",
        center={"lat": center_coors[0], "lon": center_coors[1]},
        zoom=8,
        color="Signal",
        range_color=(-160, -50),
        opacity=0.5,
        height=800,
        width=800)
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_style="carto-positron"),
    return fig