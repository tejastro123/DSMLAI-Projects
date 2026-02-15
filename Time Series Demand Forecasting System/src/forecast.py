import pickle
import pandas as pd
import os
import sys

# Add project root to path
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.append(project_root)

def forecast_next(df, days=7):
    """
    Generate forecast for the next 'days' days using the saved best model.
    """
    # Paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_path, "models")
    
    try:
        model_path = os.path.join(models_dir, "best_model.pkl")
        name_path = os.path.join(models_dir, "model_name.pkl")
        
        if not os.path.exists(model_path) or not os.path.exists(name_path):
             return None, "Model not found. Please train the model first."
             
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            
        with open(name_path, 'rb') as f:
            model_name = pickle.load(f)
    except Exception as e:
        return None, f"Error loading model: {e}"

    if model_name == "Prophet":
        # Prophet requires 'ds' and 'y' columns
        # df index is date, so reset index
        df_p = df.reset_index().rename(columns={'date':'ds','sales':'y'})
        
        # Prophet 'make_future_dataframe' might need the model to be fitted? 
        # The loaded model is already fitted.
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        
        # Return only the future part
        return forecast[['ds','yhat']].tail(days), "Prophet"

    else:
        # Random Forest (or other sklearn regressors)
        # Logic for lag-based iterative forecasting
        lags = 7
        if len(df) < lags:
            return None, "Not enough data for lag-based forecasting."
            
        last_values = df['sales'].values[-lags:].tolist()
        preds = []
        
        # Prepare for iterative prediction
        current_seq = last_values[:] 
        
        for _ in range(days):
            # Construct features: lag_1, lag_2, ..., lag_7
            # lag_1 is the most recent value (last in current_seq)
            # lag_k is (last - k + 1)-th value
            
            # features list: [lag_1, lag_2, ..., lag_7]
            features = [current_seq[-(i+1)] for i in range(lags)]
            
            pred = model.predict([features])[0]
            preds.append(pred)
            
            # Update sequence for next step
            current_seq.append(pred)
            current_seq.pop(0)

        dates = pd.date_range(df.index[-1], periods=days+1)[1:]
        result_df = pd.DataFrame({'date':dates, 'forecast':preds})
        return result_df, model_name
