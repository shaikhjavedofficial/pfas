import requests
import time
import pickle
import subprocess

current_scale = 1

def get_backend_container_count():
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "ancestor=pfas-backend", "--format", "{{.ID}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        )
        container_ids = result.stdout.strip().splitlines()
        return len(container_ids)
    except subprocess.CalledProcessError:
        return 0

def scaleUp_backend(count):
    subprocess.run(["docker-compose", "up", "--scale", f"backend={count}", "-d"])

def scaleDown_backend(count):
    subprocess.run(["docker", "rm", "-f", f"backend-{count}"])

# Load your trained model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

def get_metrics():
    try:
        return requests.get('http://localhost:8080/metrics').json()
        # return requests.get('http://backend:5000/metrics').json()
    except Exception as e:
        print("Error fetching metrics:", e)
        return None

while True:
    metrics = get_metrics()
    if metrics:
        X = [[metrics['cpu'], metrics['memory'], metrics['requests']]]
        predicted = model.predict(X)[0]
        print(f"Predicted requests: {predicted}")

        # running = client.containers.list(filters={"ancestor": "pfas-backend"})
        running = get_backend_container_count()
        print(f"Running containers: {running}")

        if predicted > 92 and running < 3:
            # print("Scaling up: starting new container")
            # client.containers.run('pfas-backend', detach=True, ports={'5000/tcp': None}, network='backendnet')
            current_scale += 1
            print(f"Scaling up to: {current_scale}")
            scaleUp_backend(current_scale)
        elif running > 1:
            current_scale -= 1
            print(f"Scaling down to: {current_scale}")
            scaleUp_backend(current_scale)
            # running[-1].stop()
    time.sleep(5)