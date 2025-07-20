import csv
from flask import Flask, request, jsonify
import psutil
import threading
import time
import os
import pandas as pd
lock = threading.Lock()

app = Flask(__name__)
request_count = 0

LOG_FILE = 'metrics_log.csv'
FIELDNAMES = ['timestamp', 'cpu', 'memory', 'requests']
if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0 or os.path.isdir(LOG_FILE):
    print("Creating new log file")
    df = pd.DataFrame(columns=FIELDNAMES)
    df.to_csv(LOG_FILE, index=False)

@app.route('/log_metrics', methods=['POST'])
def log_metrics():
    global request_count
    with lock:
        metric = {
            'timestamp': time.time(),
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'requests': request_count
        }
    # with open(LOG_FILE, 'a', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
    #     if csvfile.tell() == 0:
    #         writer.writeheader()
    #     writer.writerow(metric)
    # return jsonify(metric)
        # Read the current CSV (header is ensured above)
        # df = pd.read_csv(LOG_FILE)
        # Append new row
        df = pd.DataFrame([[metric['timestamp'], metric['cpu'], metric['memory'], metric['requests']]], columns=FIELDNAMES)
        # df_new = pd.DataFrame([metric])
        # df = pd.concat([df, df_new], ignore_index=True)
        # Write back to CSV
        df.to_csv(
            LOG_FILE,
            mode='a',
            header=False,
            index=False)
        request_count = 0
    return jsonify(metric)

@app.route('/reset_request', methods=['GET'])
def reset_request():
    # global request_count
    with lock:
        request_count = 0
    return jsonify({'status': 'request count reset'})

@app.route('/process', methods=['POST'])
def process():
    global request_count
    with lock:
        request_count += 1
    # Simulate work
    time.sleep(0.1)
    return jsonify({'status': 'processed'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)