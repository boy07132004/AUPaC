import os
import queue
import json
import time
import ciso8601
from datetime import datetime
from influxdb import InfluxDBClient


USER 		= os.environ['INFLUXDB_ADMIN_USER']
PASSWORD 	= os.environ['INFLUXDB_ADMIN_PASSWORD']
DATABASE 	= os.environ['INFLUXDB_DB']
DATABASEHOST 	= os.environ["DATABASE_IP"]

    
client = InfluxDBClient(DATABASEHOST, 8086, USER, PASSWORD, DATABASE)
r = client.query('select * from sps30 where time>now()-3d AND location=\'C\'').get_points()
r = list(r)
timeInterval = []

for i in range(len(r)-1):
    itv = (ciso8601.parse_datetime(r[i+1]['time'])-ciso8601.parse_datetime(r[i]['time'])).total_seconds()
    if itv>1000: print(r[i])
    else:
        timeInterval.append(itv)
