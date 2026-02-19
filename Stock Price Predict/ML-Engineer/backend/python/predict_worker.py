import sys
import json
import joblib
import pandas as pd
import numpy as np
import yfinance as yf
import os

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Reusable feature engineering on a dataframe
def calculate_features(df_input):
    df = df_input.copy()
    
    # 1. Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # 2. MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # 3. RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 4. Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Middle'] + (df['Close'].rolling(window=20).std() * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['Close'].rolling(window=20).std() * 2)

    # 5. Lag Features
    for lag in [1, 2, 3, 5]:
        df[f'Lag_{lag}'] = df['Close'].shift(lag)

    # 6. Returns & Volatility
    df['Daily_Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Daily_Return'].rolling(window=21).std()
    
    return df

def get_latest_features_from_df(df_processed):
    # Select only the features used during training
    feature_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 
                    'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'MACD', 'Signal_Line', 
                    'RSI', 'BB_Middle', 'BB_Upper', 'BB_Lower', 'Lag_1', 'Lag_2', 
                    'Lag_3', 'Lag_5', 'Daily_Return', 'Volatility']
    
    # Check if all columns exist
    missing_cols = [col for col in feature_cols if col not in df_processed.columns]
    if missing_cols:
         raise ValueError(f"Missing features: {missing_cols}")

    return df_processed[feature_cols].iloc[-1:].values

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No ticker provided"}))
        sys.exit(1)

    ticker = sys.argv[1].upper()
    days_to_predict = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    # Load Artifacts
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "models", "xgb_model.pkl")
        scaler_path = os.path.join(script_dir, "models", "scaler.pkl")
        
        if not os.path.exists(model_path):
             print(json.dumps({"error": f"Model not found at {model_path}"}))
             sys.exit(1)

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load models: {str(e)}"}))
        sys.exit(1)

    # Fetch History
    try:
        # Fetch 1 year to ensure robustness for iterative updates
        df_full = yf.download(ticker, period="1y", progress=False)
        
        if isinstance(df_full.columns, pd.MultiIndex):
            df_full.columns = df_full.columns.droplevel(1)
            
        if df_full.empty:
             raise ValueError(f"No data found for {ticker}")

    except Exception as e:
        print(json.dumps({"error": f"Error fetching history: {str(e)}"}))
        sys.exit(1)

    try:
        forecast = []
        current_df = df_full.copy()
        
        # Iterative Prediction Loop
        for i in range(days_to_predict):
            # Calculate features on current_df
            df_features = calculate_features(current_df)
            
            # Get latest feature row
            features = get_latest_features_from_df(df_features)
            
            # Scale & Predict
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)
            predicted_price = float(prediction[0])
            
            forecast.append({
                "day": i + 1,
                "price": predicted_price
            })
            
            # Append prediction to current_df to serve as history for next iteration
            # We assume OHLC are all the predicted price for simplicity in this projection
            last_date = current_df.index[-1]
            next_date = last_date + pd.Timedelta(days=1)
            
            new_row = pd.DataFrame({
                "Open": [predicted_price],
                "High": [predicted_price],
                "Low": [predicted_price],
                "Close": [predicted_price],
                "Volume": [current_df['Volume'].iloc[-1]] # Assume steady volume
            }, index=[next_date])
            
            current_df = pd.concat([current_df, new_row])

        # Prepare Historical Data (Last 60 days for better context)
        # Use ORIGINAL df_full for history display, not the projected one with flat lines
        history_df = df_full.tail(60).reset_index()
        history_data = []
        for _, row in history_df.iterrows():
            history_data.append({
                "date": row['Date'].strftime('%Y-%m-%d'),
                "Close": float(row['Close']),
                "High": float(row['High']),
                "Low": float(row['Low']),
                "Open": float(row['Open'])
            })
            
        # Extract Latest Indicators from the original valid data
        df_indicators = calculate_features(df_full)
        latest_indicators = df_indicators.iloc[-1]

        current_indicators = {
            "RSI": float(latest_indicators['RSI']) if not pd.isna(latest_indicators['RSI']) else 50.0,
            "MACD": float(latest_indicators['MACD']) if not pd.isna(latest_indicators['MACD']) else 0.0,
            "Signal": float(latest_indicators['Signal_Line']) if not pd.isna(latest_indicators['Signal_Line']) else 0.0,
            "SMA_20": float(latest_indicators['SMA_20']) if not pd.isna(latest_indicators['SMA_20']) else 0.0,
            "SMA_50": float(latest_indicators['SMA_50']) if not pd.isna(latest_indicators['SMA_50']) else 0.0
        }

        result = {
            "ticker": ticker,
            "forecast": forecast,
            "sentiment": "Bullish" if forecast[-1]["price"] > float(df_full['Close'].iloc[-1]) else "Bearish",
            "current_price": float(df_full['Close'].iloc[-1]),
            "history": history_data,
            "indicators": current_indicators
        }
        print(json.dumps(result))
        
    except ValueError as val_err:
        print(json.dumps({"error": str(val_err)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
