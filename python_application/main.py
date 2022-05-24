from email import header
import mimetypes
import os
import time
import json
from httplib2 import Response
import plotly
import datetime
import pandas as pd
import gstools as gs
from io import StringIO
from numpy import array, arange
import plotly.graph_objects as go
from pykrige.ok import OrdinaryKriging
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
        
        query+= f" tz('{TZ}')"
        df = CLIENTDF.query(query)['sps30']
        df['time'] = df.index.tz_convert(tz=TZ)
        df.reset_index(drop=True, inplace=True)
        
        if ret['downloadFile']:
            fileBuffer = StringIO()
            df.to_csv(fileBuffer, encoding='utf-8')
            csvOutput = fileBuffer.getvalue()
            fileBuffer.close()

            fileLocation = "_".join(ret['location'])
            filename = f"{fileLocation}_{ret['startDate']}_{ret['endDate']}.csv"
            resp = make_response(csvOutput)
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

@app.route("/contour")
def contour_map():
    return render_template("contour.html")

@app.route("/contourCallback", methods=["GET"])
def contour_callback():
    size = request.args.get('size')
    validSize = ['nc0p5', 'nc1p0', 'nc2p5']
    if not size in validSize:
        return make_response("Size error", 404)
    
    query = f"select last({size}) from sps30 group by location"
    pixelMap = {"C":[2.5, 3.0],
                "A": [2.5, 27.0],
                "D": [22.5, 3.0],
                "B": [22.5, 27.0]                
    }
    gridx = arange(0.0, 25.0, 1.0)
    gridy = arange(0.0, 30.0, 1.0)
    queryResult = CLIENTDF.query(query)
    result = []
    while queryResult:
        item = queryResult.popitem()
        location, value = item[0][1][0][1], item[1].values[0][0]
        if location in pixelMap:
            result.append( pixelMap[location] + [value])
    
    result = array(result)
    cov_model = gs.Gaussian(dim=2, len_scale=3, anis=2, var=1, nugget=0.1)
    OK1 = OrdinaryKriging(result[:, 0], result[:, 1], result[:, 2], cov_model)
    z1, ss1 = OK1.execute("grid", gridx, gridy)
    fig = go.Figure(data = go.Contour(z=pd.DataFrame(z1.data),
                                  colorscale="rdylgn",
                                  reversescale=True,
                                  zmin=0,
                                  zmax=100
                            )
    )
    fig.update_traces(contours_coloring="fill", contours_showlabels=True)
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False)
    
