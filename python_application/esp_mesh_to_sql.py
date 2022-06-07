import os
import queue
import json
import time
import serial
import threading
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

PORT            = '/dev/ttyUSB0'
BAUDRATE        = 115200
USER            = os.environ['INFLUXDB_ADMIN_USER']
PASSWORD        = os.environ['INFLUXDB_ADMIN_PASSWORD']
DATABASE        = os.environ['INFLUXDB_DB']
DATABASEHOST    = os.environ["DATABASE_IP"]
RETENTIONPOLICY = 'autogen'
BUCKET          = f'{DATABASE}/{RETENTIONPOLICY}'


class esp32_mesh_host(threading.Thread):
    def __init__(self, port, baudrate, dataQueue):
        threading.Thread.__init__(self)
        self.port = port
        self.baudrate = baudrate
        self.dataQueue = dataQueue
    
    def run(self):
        self.ser = serial.Serial(self.port, self.baudrate)
        while True:
            try:
                while self.ser.in_waiting:
                    data = self.ser.readline().decode()
                    if data[:7] == "[AUPAC]":
                        message = data.split("[AUPAC]")[1]
                        data = json.loads(message)
                        
                        self.dataQueue.put(
                            Point("sps30") \
                            .tag("location", data['location']) \
                            .field("nc0p5", data['NC0.5']) \
                            .field("nc1p0", data['NC1.0']) \
                            .field("nc2p5", data['NC2.5']) \
                            .time(datetime.utcnow())
                        )
                        
            except Exception as e:
                print(f"ESP mesh json loads error\n{e}")
   
    
def insert(dataQueue):
    payload = ""
    count   = 0

    while not dataQueue.empty():
        payload += (dataQueue.get().to_line_protocol() + "\n")
        count+=1

    s = time.time()
    CLIENT.write_api(write_options=SYNCHRONOUS).write(bucket=BUCKET, record=payload)
    #print(f"Upload {count} data, cost {time.time()-s:.4} seconds")
    
def main():
    dataQueue = queue.Queue(maxsize=0)
    host = esp32_mesh_host(PORT, BAUDRATE, dataQueue)
    host.start()
         
    while True:
        if not dataQueue.empty():
            insert(dataQueue)
        else:
            print(f"{datetime.now()} -> Queue empty")
        time.sleep(5)
            
if __name__ == "__main__":
    CLIENT = InfluxDBClient(url=f'http://{DATABASEHOST}:8086', token=f'{USER}:{PASSWORD}', org='-')
    
    while not CLIENT.ping():
        time.sleep(5)
        print("Connection failed. Retry in 5 seconds....")

    main()
