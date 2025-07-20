import requests
import time
import pickle
import subprocess
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

current_scale = 1
loop_count = 0
# Load your trained model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

MODEL_PATH = 'model.pkl'
DATA_PATH = 'metrics_log.csv'
RETRAIN_INTERVAL = 1 # Retrain every 50 cycles (adjust as needed)

def retrain_model_if_needed(loop_count):
    if os.path.exists(DATA_PATH) and loop_count % RETRAIN_INTERVAL == 0:
        print("here")
        try:
            df = pd.read_csv(DATA_PATH)
            print(df)
            if len(df) >= 5:
                X = df[['cpu', 'memory', 'requests']].values
                y = df['requests'].values
                print(X,y)
                new_model = RandomForestRegressor()
                new_model.fit(X, y)
                with open(MODEL_PATH, 'wb') as f:
                    pickle.dump(new_model, f)
                model = new_model
                print("Model retrained on live data!")
        except pd.errors.EmptyDataError:
            print("CSV file is empty. Skipping model retraining.")
        except Exception as e:
            print("Error during model retraining:", e)

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
def get_desired_count(predicted):
    if predicted < 100:
        return 1
    elif predicted < 500:
        return 2
    else:
        return 3  # or 4 if you want, add another elif for > 1000

def scaleUp_backend(running, predicted):
    desired = get_desired_count(predicted)
    if desired != running:
        print(f"Scaling to: {desired} (from {running})")
        subprocess.run(["docker-compose", "up", "--scale", f"backend={desired}", "-d"])
        subprocess.run(["docker", "image", "prune", "-f"])
        reset_request()
    else:
        print(f"No scaling needed: running={running}, predicted={predicted}")
    # if predicted < 100 and running > 1:
    #     count = 1
    #     print(f"Scaling down to: {current_scale}")
    #     subprocess.run(["docker-compose", "up", "--scale", f"backend={count}", "-d"])
    #     subprocess.run(["docker", "image", "prune", "f"])
    #     reset_request()
    # if predicted > 100 and predicted < 500 and running == 1:
    #     count = 2
    #     print(f"Scaling to: {count}")
    #     subprocess.run(["docker-compose", "up", "--scale", f"backend={count}", "-d"])
    #     subprocess.run(["docker", "image", "prune", "f"])
    #     reset_request()

    # if predicted > 500 and running == 2 and running != 3:
    #     count = 3
    #     print(f"Scaling to: {count}")
    #     subprocess.run(["docker-compose", "up", "--scale", f"backend={count}", "-d"])
    #     subprocess.run(["docker", "image", "prune", "f"])
    #     reset_request()

def reset_request():
    try:
        return requests.get('http://localhost:8080/reset_request').json()
    except Exception as e:
        print("Error resetting request count:", e)

# def scaleDown_backend(count):
#     subprocess.run(["docker", "rm", "-f", f"backend-{count}"])


# def get_metrics():
#     try:
#         return requests.get('http://localhost:8080/metrics').json()

#     except Exception as e:
#         print("Error fetching metrics:", e)
#         return None
    
def get_metrics_from_log():
    try:
        return requests.post('http://localhost:8080/log_metrics').json()
    except: pass

while True:
    metrics = get_metrics_from_log()
    print(metrics)
    new_model = retrain_model_if_needed(loop_count)
    if new_model:
            model = new_model
    if metrics:
        X = [[metrics['cpu'], metrics['memory'], metrics['requests']]]
        predicted = model.predict(X)[0]
        print(f"Predicted requests: {predicted}")

        # running = client.containers.list(filters={"ancestor": "pfas-backend"})
        running = get_backend_container_count()
        print(f"Running containers: {running}")
        if running >= 1:
            scaleUp_backend(running, predicted)

        # if predicted > 90 and running < 3:
            # client.containers.run('pfas-backend', detach=True, ports={'5000/tcp': None}, network='backendnet')
            # current_scale = running + 1
            # print(f"Scaling up to: {current_scale}")
            # scaleUp_backend(running, predicted)
        # elif predicted < 90 and running > 1:
            # current_scale = running - 1
            # print(f"Scaling down to: {current_scale}")
            # scaleUp_backend(running, predicted)
            # running[-1].stop()
    loop_count += 1

    time.sleep(30)