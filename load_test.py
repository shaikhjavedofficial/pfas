import requests, time, random

while True:
    try:
        requests.post('http://localhost:8080/process')
    except:
        pass
    time.sleep(random.uniform(0.05, 0.2))
