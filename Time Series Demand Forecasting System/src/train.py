import pickle
import sys
import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from prophet import Prophet
import warnings

# Add project root to path to allow importing from src and accessing data/models via relative paths from root
# This assumes the script is run from the project root or src directory
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.append(project_root)

try:
    from src.preprocess import load_data
except ImportError:
    # Fallback if running from src directly without package structure
    from preprocess import load_data

warnings.filterwarnings("ignore")

def create_lags(data, lags=7):
    df_lag = data.copy()
    for i in range(1, lags+1):
        df_lag[f'lag_{i}'] = df_lag['sales'].shift(i)
    df_lag.dropna(inplace=True)
    return df_lag

def train_models():
    print("Loading data...")
    # absolute path or relative from root. Assuming run from root for paths to work nicely
    # process paths to be robust
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_path, "data", "raw", "sales1.csv")
    
    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}")
        return

    df = load_data(data_path)
    
    if df is None:
        print("Failed to load data.")
        return

    # Train-test split
    train = df[:-30]
    test = df[-30:]
    
    # Check if we have enough data
    if len(train) < 7:
        print("Not enough data to train.")
        return

    results = {}
    models = {}

    print("Training Prophet...")
    # ---------- Model 1: Prophet ----------
    try:
        prophet_df = train.reset_index().rename(columns={'date':'ds','sales':'y'})
        model_p = Prophet()
        model_p.fit(prophet_df)

        future = model_p.make_future_dataframe(periods=30)
        forecast = model_p.predict(future)
        pred_p = forecast['yhat'][-30:].values

        mae_p = mean_absolute_error(test['sales'], pred_p)
        results['Prophet'] = mae_p
        models['Prophet'] = model_p
    except Exception as e:
        print(f"Prophet training failed: {e}")

    print("Training Random Forest...")
    # ---------- Model 2: Random Forest ----------
    try:
        lag_df = create_lags(df)
        # Re-split after lag creation as some initial rows are dropped
        # We need to ensure we don't leak test data. 
        # But lag_df drops first 7 rows. 
        # We should split lag_df carefully.
        
        # Determine split index based on date
        split_date = test.index[0]
        train_lag = lag_df[lag_df.index < split_date]
        test_lag = lag_df[lag_df.index >= split_date]

        X_train = train_lag.drop('sales', axis=1)
        y_train = train_lag['sales']
        X_test = test_lag.drop('sales', axis=1)
        y_test = test_lag['sales']

        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        pred_rf = rf.predict(X_test)

        mae_rf = mean_absolute_error(y_test, pred_rf)
        results['RandomForest'] = mae_rf
        models['RandomForest'] = rf
    except Exception as e:
        print(f"Random Forest training failed: {e}")

    # ---------- Select Best ----------
    if not results:
        print("No models trained successfully.")
        return

    best_model_name = min(results, key=results.get)
    best_model = models[best_model_name]

    print("Model Results (MAE):", results)
    print("Best Model:", best_model_name)

    # Save models
    models_dir = os.path.join(base_path, "models")
    
    with open(os.path.join(models_dir, "best_model.pkl"), 'wb') as f:
        pickle.dump(best_model, f)
        
    with open(os.path.join(models_dir, "model_name.pkl"), 'wb') as f:
        pickle.dump(best_model_name, f)
    
    # Save individual models too if needed
    if 'Prophet' in models:
        with open(os.path.join(models_dir, "prophet.pkl"), 'wb') as f:
            pickle.dump(models['Prophet'], f)
    if 'RandomForest' in models:
        with open(os.path.join(models_dir, "rf.pkl"), 'wb') as f:
            pickle.dump(models['RandomForest'], f)
        
    print("Models saved.")

if __name__ == "__main__":
    train_models()
