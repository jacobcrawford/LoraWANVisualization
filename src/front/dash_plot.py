import re
from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from src.geo_json.lora_geo_json import getLoraGEOJson

# https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth_mapbox.html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

center_coors = 55.579209, 9.510841 #TODO plot another center

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div(id='output-container-date-picker-range'),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2021, 1, 12),
        max_date_allowed=date.today(),
        initial_visible_month=date(2021, 1, 1),
        end_date=date.today(),
        start_date=date(2021, 1, 12)
    ),
    dcc.Graph(id='graph-id')
])


@ app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix

@ app.callback(
    dash.dependencies.Output('graph-id', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')]
)
def refreshGraph(start_date, end_date):
    geojson, df = getLoraGEOJson(from_time=start_date, to_time=end_date)
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