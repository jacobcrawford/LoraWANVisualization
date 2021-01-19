from datetime import datetime as dt

import geojsoncontour
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from numpy import linspace
from plotly.offline import iplot
from scipy.interpolate import griddata

from src.storage import loradb_connecter

def roundToTen(x):
    rest = x % 10
    return x - rest

def extractDataFromloraDBConnecterResults(data):
    z = [roundToTen(i) for i in data['gateway_rssi']]
    x = [_ for _ in data['device_lon']] 
    y = [_ for _ in data['device_lat']] 
    return x,y,z

def getTestData():
    data = [(56.152264, 10.161392, -100), (56.152646, 10.225937, -100),
            (56.132261, 10.210292, -100), (56.132883, 10.155790, -100)]

    input_data = []
    for data_point in data:
        input_data.append(data_point)
        # North
        for i in range(5):
            (lat, lon, _) = data_point
            input_data.append((lat+1, lon, -50))
            input_data.append((lat+0.005, lon, -20))
        # south
        for i in range(5):
            (lat, lon, _) = data_point
            input_data.append((lat-0.001, lon, -50))
            input_data.append((lat-0.005, lon, -20))
        # east
        for i in range(5):
            (lat, lon, _) = data_point
            input_data.append((lat, lon-0.001, -50))
            input_data.append((lat, lon-0.005, -25))
        # west
        for i in range(5):
            (lat, lon, _) = data_point
            input_data.append((lat, lon+0.001, -50))
            input_data.append((lat, lon+0.005, -20))
    
    ############# FAKE DATA END ############

    #Extract the coordinates and signal values
    z = [-1*t[2] for t in input_data]
    y = [t[0] for t in input_data]
    x = [t[1] for t in input_data]
    return x,y,z

def getLoraGEOJson(device_id=None,from_time=None, to_time=None,gateway_id=None):
    data = loradb_connecter.get(device_id=device_id,gateway_id=gateway_id,from_time=from_time, to_time=to_time)

    x,y,z = extractDataFromloraDBConnecterResults(data)

    # Interpolating values to get better coverage
    xi = linspace(min(x), max(x), 100)
    yi = linspace(min(y), max(y), 100)
    zi = griddata((x, y), z, (xi[None, :], yi[:, None]), method='linear')

    check = [np.Inf if np.isnan(i) else i for i in zi.flatten()]
    min_value = min(check)
    # Creating contour plot with a step size of 1000
    step_size = 10
    start_value = int(min_value - (min_value % step_size))

    value_range = range(
        start_value, int(np.nanmax(zi))+step_size, step_size)
    cs = plt.contourf(xi, yi, zi, levels=value_range, cmap=plt.cm.jet)

    # Converting matplotplib contour plot to geojson
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=cs,
        ndigits=3,
    )

    signal_geojson = eval(geojson)

    # Creating empty array to fill with "signal values"
    arr_temp = np.ones([len(signal_geojson["features"]), 2])

    # Title is the interval e.g. -130--140. We need to extract -130
    for i in range(0, len(signal_geojson["features"])):
        signal_geojson["features"][i]["properties"]["title"] = -1*np.float64(signal_geojson["features"][i]["properties"]["title"].split(
            "-")[1])

    for i in range(0, len(signal_geojson["features"])):
        signal_geojson["features"][i]["id"] = i
        arr_temp[i, 0] = i
        signal = signal_geojson["features"][i]["properties"]["title"]
        arr_temp[i, 1] = signal

    # Transforming array to df
    df_contour = pd.DataFrame(arr_temp, columns=["Id", "Signal"])

    return signal_geojson, df_contour