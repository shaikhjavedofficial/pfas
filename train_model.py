# train_model.py
import pickle
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# Dummy training data
X = np.random.rand(100, 3) * 100  # cpu, memory, requests
y = X[:, 2] + np.random.randn(100) * 10  # Predict requests

model = RandomForestRegressor()
model.fit(X, y)

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)