import os
import time
import datetime
import json
import plotly
import pandas as pd
import plotly.graph_objects as go
from influxdb import InfluxDBClient, DataFrameClient
from flask import Flask, render_template, request, make_response


app = Flask(__name__) 
USER            = os.environ['INFLUXDB_ADMIN_USER']
PASSWORD        = os.environ['INFLUXDB_ADMIN_PASSWORD']
DATABASE        = os.environ['INFLUXDB_DB']
DATABASEHOST    = os.environ["DATABASE_IP"]
TZ              = os.environ["TZ"]
CLIENT          = InfluxDBClient(host=DATABASEHOST, username=USER, password=PASSWORD, database=DATABASE)
CLIENTDF        = DataFrameClient(host=DATABASEHOST, username=USER, password=PASSWORD, database=DATABASE)


while True:
    try:        
        _ = CLIENT.ping()
        break
        
    except:
        time.sleep(5)
        print("Connection failed. Retry in 5 seconds....")


def get_query_location():
    query  = 'SHOW TAG VALUES FROM sps30 WITH key="location" WHERE time>now()-10m'
    locationResults = CLIENT.query(query).get_points()
    locationList = [ result['value'] for result in list(locationResults) ]
    locationList.sort()
    return locationList

@app.route('/')
@app.route('/realtime')
def realtime_plot():
    return render_template('real-time.html', locationList = get_query_location())

@app.route('/callback', methods=["GET"])
def plot_graph():
    try:
        ret = json.loads(request.args.get('returnJSON'))
        locations = ret['location']
        locationString = "' OR location='".join(locations)
        
        if 'startDate' in ret:
            startDate = ret['startDate']
            endDate = ret['endDate']
            query = f"SELECT * FROM sps30 WHERE location='{locationString}' AND time>'{startDate}' AND time<'{endDate}'"
        else:
            query = f"SELECT * FROM sps30 WHERE location='{locationString}' AND time> now()-5m"
        
        df = CLIENTDF.query(query)['sps30']
        df['time'] = df.index.tz_convert(tz=TZ)
        df.reset_index(drop=True, inplace=True)
        
        if ret['downloadFile']:
            fileLocation = "_".join(ret['location'])
            filename = f"{fileLocation}_{ret['startDate']}_{ret['endDate']}.csv"
            resp = make_response(df.to_csv())
            resp.headers['Content-Disposition'] = f"attachment; filename={filename}"
            resp.headers['Content-type'] = 'text/csv'
            
            return resp
        
        sizeSelected = ret['sizeBinary']
        dataframeReturned = {}
        for location in locations:
            _sizeSelected = sizeSelected
            _df = df[ df['location']==location ]
        
            if _df.empty : continue
            if not ('startDate' in ret): _df = _df.tail(20) # For real-time page
                
            _fig = go.FigureWidget()
            
            for size in ['nc0p5', 'nc1p0', 'nc2p5']:
                if _sizeSelected %2 :
                    _fig.add_scatter(x=_df.time, y=_df[size], name=size)
                _sizeSelected = _sizeSelected>>1
    
            dataframeReturned[location] = json.dumps(_fig, cls=plotly.utils.PlotlyJSONEncoder)
        return json.dumps(dataframeReturned)
    
    except Exception as e:
        print(f"Callback error. \n{e}")
        
@app.route("/history")
def history():
    locationList = get_query_location()
    startDate    = datetime.date.today()
    endDate      = datetime.date.today() + datetime.timedelta(days = 1)
    return render_template('history.html', locationList=locationList, startDate=startDate, endDate=endDate)

@app.route("/delete", methods=["GET"])
def delete_history():
    ret = json.loads(request.args.get('returnJSON'))
    locations = ret['location']
    startDate = ret['startDate']
    endDate = ret['endDate']
    
    locationString = "' OR location='".join(locations)
    deleteSQL = f"DELETE FROM sps30 WHERE (location='{locationString}') AND (time>'{startDate}' AND time<'{endDate}');"     
    
    CLIENT.query(deleteSQL)
    return make_response("Ok", 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False)
    
