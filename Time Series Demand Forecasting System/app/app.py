import streamlit as st
import pandas as pd
import sys
import os
import pickle
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import backend modules
try:
    from src.preprocess import load_data
    from src.train import train_models
    from src.forecast import forecast_next
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

st.set_page_config(page_title="Demand Forecasting System", layout="wide")

st.title("Time Series Demand Forecasting System")

# Sidebar for controls
st.sidebar.header("Configuration")

days = st.sidebar.slider("Forecast Horizon (days)", 7, 90, 30)

# Upload section
st.header("1. Upload Data")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Logic to handle uploaded file OR default file
df = None
data_path = None

if uploaded_file is not None:
    df, _ = load_data(uploaded_file)
else:
    # Use default
    st.info("Using default dataset (sales2.csv) since no file uploaded.")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_data_path = os.path.join(base_path, "data", "raw", "sales2.csv")
    if os.path.exists(default_data_path):
        df, _ = load_data(default_data_path)

if df is not None:
    st.success("Data loaded successfully!")
    
    # Display historical data
    st.header("2. Historical Sales Data")
    
    # Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['sales'], mode='lines', name='Sales'))
    fig.update_layout(title="Historical Sales", xaxis_title="Date", yaxis_title="Sales", hovermode="x unified")
    st.plotly_chart(fig, width='stretch', height='stretch')
    
    # Model training and forecasting
    st.header("3. Training & Forecast")
    if st.button("Train Models & Forecast"):
        with st.spinner("Training models and generating forecast..."):
            # Train models using the loaded dataframe
            best_model, model_name, metrics = train_models(df=df)
            
            if best_model:
                st.success(f"Training Complete! Best Model: **{model_name}**")
                
                # Show Comparison
                if metrics:
                    st.subheader("Model Comparison (MAE)")
                    st.table(pd.DataFrame.from_dict(metrics, orient='index', columns=['MAE']))
                
                # Generate forecast
                forecast_df, model_name = forecast_next(df, days)
                
                if forecast_df is not None:
                    st.header(f"Forecast ({days} days)")
                    
                    # Plot forecast
                    fig_forecast = go.Figure()
                    
                    # Historical data (last 60 days for context)
                    history_subset = df.tail(60)
                    fig_forecast.add_trace(go.Scatter(
                        x=history_subset.index,
                        y=history_subset['sales'],
                        mode='lines',
                        name='Historical Sales',
                        line=dict(color='blue')
                    ))
                    
                    # Forecast data
                    if 'ds' in forecast_df.columns:
                        # Prophet
                        fig_forecast.add_trace(go.Scatter(
                            x=forecast_df['ds'],
                            y=forecast_df['yhat'],
                            mode='lines',
                            name='Forecast',
                            line=dict(color='orange')
                        ))
                        # Confidence Interval
                        if 'yhat_lower' in forecast_df.columns and 'yhat_upper' in forecast_df.columns:
                             fig_forecast.add_trace(go.Scatter(
                                x=forecast_df['ds'],
                                y=forecast_df['yhat_upper'],
                                mode='lines',
                                name='Upper Bound',
                                line=dict(width=0),
                                showlegend=False
                            ))
                             fig_forecast.add_trace(go.Scatter(
                                x=forecast_df['ds'],
                                y=forecast_df['yhat_lower'],
                                mode='lines',
                                fill='tonexty',
                                fillcolor='rgba(255, 165, 0, 0.2)',
                                name='Confidence Interval',
                                line=dict(width=0),
                                showlegend=False
                            ))
                        
                    else:
                        # RF
                        fig_forecast.add_trace(go.Scatter(
                            x=forecast_df['date'],
                            y=forecast_df['forecast'],
                            mode='lines',
                            name='Forecast',
                            line=dict(color='orange')
                        ))
                    
                    fig_forecast.update_layout(
                        title='Sales Forecast',
                        xaxis_title='Date',
                        yaxis_title='Sales',
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig_forecast, use_container_width=True)
                    
                    st.write("Forecast Data:")
                    st.dataframe(forecast_df)
                    
                    # Download button
                    csv = forecast_df.to_csv(index=False)
                    st.download_button(
                        label="Download Forecast CSV",
                        data=csv,
                        file_name="forecast.csv",
                        mime="text/csv",
                    )
                else:
                    st.error("Failed to generate forecast.") 
            else:
                 st.error("Training failed.")
