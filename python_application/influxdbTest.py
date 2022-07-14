import os
import time
import pandas as pd
from datetime import datetime, timedelta
from influxdb import DataFrameClient, InfluxDBClient


TZ              = os.environ["TZ"]
CSVFOLDER       = os.environ["CSVFOLDER"]
USER            = os.environ['INFLUXDB_ADMIN_USER']
PASSWORD        = os.environ['INFLUXDB_ADMIN_PASSWORD']
DATABASE        = os.environ['INFLUXDB_DB']
DATABASEHOST    = os.environ["DATABASE_IP"]

CLIENT = InfluxDBClient(host=DATABASEHOST, username=USER, password=PASSWORD, database=DATABASE)
CLIENTDF  = DataFrameClient(host=DATABASEHOST, username=USER, password=PASSWORD, database=DATABASE)


while True:
    try:        
        _ = CLIENTDF.ping()
        break
        
    except:
        time.sleep(5)
        print("Connection failed. Retry in 5 seconds....")


def dfq(query):
    return CLIENTDF.query(query)

def q(query):
    return CLIENT.query(query)
