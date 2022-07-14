import os
import queue
import json
import time
import serial
import threading
import logging
from datetime import datetime
from aupac_log import aupac_log_init
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
                        p = Point("sps30").tag("location", data['location'])
                        for k, v in data.items():
                            if k != 'location': p.field(k, v)
                        p.time(datetime.utcnow())
                        self.dataQueue.put(p)
                        
            except Exception as e:
                logging.error(f"ESP mesh json loads error\n{e}")
   
    
def insert(dataQueue):
    payload = ""

    while not dataQueue.empty():
        payload += (dataQueue.get().to_line_protocol() + "\n")

    CLIENT.write_api(write_options=SYNCHRONOUS).write(bucket=BUCKET, record=payload)
    
def main():
    dataQueue = queue.Queue(maxsize=0)
    host = esp32_mesh_host(PORT, BAUDRATE, dataQueue)
    host.start()
         
    while True:
        if not dataQueue.empty():
            insert(dataQueue)
        else:
            logging.warning(f"{datetime.now()} -> Queue empty")
        time.sleep(5)
            
if __name__ == "__main__":
    aupac_log_init("/mesh_to_sql_log.txt")
    CLIENT = InfluxDBClient(url=f'http://{DATABASEHOST}:8086', token=f'{USER}:{PASSWORD}', org='-')
    
    while not CLIENT.ping():
        time.sleep(5)
        logging.warning("Connection failed. Retry in 5 seconds....")

    main()
