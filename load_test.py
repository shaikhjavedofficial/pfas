import requests, time, random

while True:
    try:
        requests.post('http://localhost:8080/process')
    except:
        pass
    # time.sleep(random.uniform(0.05, 0.2))
    time.sleep(0.0000005)  # 200+ requests every 30s

