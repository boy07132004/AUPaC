import os
import time
import pandas as pd
from datetime import datetime, timedelta
from influxdb import DataFrameClient


TZ              = os.environ["TZ"]
CSVFOLDER       = os.environ["CSVFOLDER"]
USER            = os.environ['INFLUXDB_ADMIN_USER']
PASSWORD        = os.environ['INFLUXDB_ADMIN_PASSWORD']
DATABASE        = os.environ['INFLUXDB_DB']
DATABASEHOST    = os.environ["DATABASE_IP"]

CLIENTDF  = DataFrameClient(host=DATABASEHOST, username=USER, password=PASSWORD, database=DATABASE)


while True:
    try:        
        _ = CLIENTDF.ping()
        break
        
    except:
        time.sleep(5)
        print("Connection failed. Retry in 5 seconds....")


query     = "SELECT * FROM sps30 WHERE time > now()-1d"
df = CLIENTDF.query(query)['sps30']
df.index = df.index.tz_convert(tz=TZ)

if not df.empty:
    yesterday = datetime.now() - timedelta(1)
    df.to_csv(f"../{CSVFOLDER}{yesterday.strftime('%Y%m%d')}.csv")
