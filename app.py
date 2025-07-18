from flask import Flask, request, jsonify
import psutil
import threading
import time

lock = threading.Lock()

app = Flask(__name__)
request_count = 0

@app.route('/process', methods=['POST'])
def process():
    global request_count
    with lock:
        request_count += 1
    # Simulate work
    time.sleep(0.1)
    return jsonify({'status': 'processed'})

@app.route('/metrics')
def metrics():
    return jsonify({
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'requests': request_count
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)