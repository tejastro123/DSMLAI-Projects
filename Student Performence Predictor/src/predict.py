import joblib
import numpy as np

model = joblib.load("models/best_model.pkl")
scaler = joblib.load("models/scaler.pkl")

def predict_score(features):
    features = np.array(features).reshape(1, -1)
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)
    return prediction[0]
