import logging
from logging.handlers import RotatingFileHandler

def aupac_log_init(filename="log.txt", level=logging.INFO):
    
    logFile = filename
    logHandler = RotatingFileHandler(logFile, mode="a", maxBytes=10*1024*1024,
                                    backupCount=2, encoding=None, delay=0)
    logFormatter = logging.Formatter("%(asctime)s %(levelname)s -> %(message)s")
    logHandler.setFormatter(logFormatter)
    logHandler.setLevel(level)
    meshLog = logging.getLogger("root")
    meshLog.setLevel(level)
    meshLog.addHandler(logHandler)