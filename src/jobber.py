import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

import schedule
import time
from src.server import process_pending
from src import app, db
from datetime import datetime

def job():
    try:
        print("Executing the job at {}".format(datetime.now()))
        process_pending(app, db)
    except Exception as err:
        print(err)

# schedule.every(30).seconds.do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(10)
job()