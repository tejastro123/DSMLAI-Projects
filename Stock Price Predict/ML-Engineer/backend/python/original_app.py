# ==========================================
# 10. DEPLOYMENT DESIGN (FastAPI)
# ==========================================

# START of app.py content representation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import yfinance as yf

# Initialize App
app = FastAPI(title="Stock Price Predictor API", version="1.0")

# Load Artifacts (Ensure paths are correct relative to app.py)
try:
    model = joblib.load("./models/xgb_model.pkl")
    scaler = joblib.load("./models/scaler.pkl")
    print("Artifacts loaded successfully.")
except:
    print("Warning: Models not found. Ensure training is run first.")

class StockRequest(BaseModel):
    ticker: str
    days: int = 1

def get_latest_features(ticker):
    # Fetch recent data (enough to calculate Lookback/Moving Averages)
    df = yf.download(ticker, period="3mo", progress=False)

    # Fix for yfinance returning MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    
    # 1. Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # 2. MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # 3. RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 4. Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Middle'] + (df['Close'].rolling(window=20).std() * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['Close'].rolling(window=20).std() * 2)

    # 5. Lag Features (Autocorrelation)
    for lag in [1, 2, 3, 5]:
        df[f'Lag_{lag}'] = df['Close'].shift(lag)

    # 6. Daily Returns & Volatility
    df['Daily_Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Daily_Return'].rolling(window=21).std()

    # Cleanup
    df.dropna(inplace=True)
    
    if df.empty:
        raise ValueError(f"Insufficient data for ticker {ticker}. Verify the ticker symbol is correct.")
    
    # Select only the features used during training
    # (Assuming these are the columns based on the logic above)
    feature_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 
                    'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'MACD', 'Signal_Line', 
                    'RSI', 'BB_Middle', 'BB_Upper', 'BB_Lower', 'Lag_1', 'Lag_2', 
                    'Lag_3', 'Lag_5', 'Daily_Return', 'Volatility']
    
    return df[feature_cols].iloc[-1:].values

@app.get("/")
def home():
    return {"message": "Stock Prediction API is Live"}

@app.post("/predict")
def predict(request: StockRequest):
    try:
        # 1. Fetch & Prep Data
        features = get_latest_features(request.ticker)
        
        # 2. Scale
        features_scaled = scaler.transform(features)
        
        # 3. Predict
        prediction = model.predict(features_scaled)
        
        return {
            "ticker": request.ticker,
            "days_ahead": request.days,
            "predicted_price": float(prediction[0]),
            "sentiment": "Bullish"
        }
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# END of app.py content representation