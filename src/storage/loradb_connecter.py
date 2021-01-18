from influxdb import DataFrameClient
import pandas as pd
from config import INFLUXSERVER,INFLUXPORT,INFLUXDB

client = DataFrameClient(host=INFLUXSERVER, port=INFLUXPORT, database=INFLUXDB)

def get(device_id=None,from_time=None, to_time=None):
    first = True
    query_string = f'SELECT * FROM "adeunis-gps"'
    if from_time != None:
        query_string +=  f' WHERE time >= \'{from_time}\''
        first = False
    if to_time != None:
        if first:
            query_string += ' WHERE time < \'{to_time}\''
            first = False
        else:
            query_string += f' AND time < \'{to_time}\''
    if device_id != None:
        if first:
            query_string += f' WHERE "device_id" = \'{device_id}\''
            first = False 
        else: 
            query_string += ' AND "device_id" = \'{device_id}\''
    result_dict = client.query(query_string)
    result = pd.concat(result_dict, axis=1)
    result.columns = result.columns.droplevel() 
    return result



