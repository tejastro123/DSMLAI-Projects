import streamlit as st
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from src.preprocess import load_data
    from src.forecast import forecast_next
except ImportError:
    st.error("Could not import source modules. Please ensure you are running from the project root.")
    st.stop()

st.set_page_config(page_title="Demand Forecasting System", layout="wide")

st.title("Time Series Demand Forecasting System")
st.markdown("""
This system predicts future product sales based on historical data. 
Upload a CSV file with `date` and `sales` columns.
""")

# Sidebar for inputs
with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader("Upload Sales CSV", type=['csv'])
    days = st.slider("Forecast Horizon (Days)", min_value=7, max_value=90, value=30)
    
    run_forecast = st.button("Generate Forecast")

if uploaded_file:
    try:
        # Load and preprocess data
        df = load_data(uploaded_file)
        
        if df is not None:
            # Display historical data
            st.subheader("Historical Sales Data")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.line_chart(df['sales'])
            
            with col2:
                st.write("Recent Data:")
                st.dataframe(df.tail(10))
            
            if run_forecast:
                with st.spinner("Generating forecast..."):
                    # Generate forecast
                    # Note: forecast_next loads the model from disk. 
                    # If model was trained on different data structure/scale, results might be nonsense 
                    # if we upload a completely new dataset.
                    # Ideally we should retrain here or allow model selection.
                    # For this scope, user asked for "Forecast next N days" using "Best model".
                    # We assume the uploaded data is consistent with what the model expects (or valid for the model).
                    
                    forecast_df, model_name = forecast_next(df, days)
                    
                    if forecast_df is not None:
                        st.subheader(f"Forecast ({days} days)")
                        st.info(f"Using Model: **{model_name}**")
                        
                        # Plotting forecast
                        # We can combine history and forecast for a nice plot
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.plot(df.index[-60:], df['sales'].tail(60), label='Historical (Last 60 days)')
                        
                        # Forecast dates are in 'date' or 'ds' column depending on model
                        if 'ds' in forecast_df.columns:
                            # Prophet
                            dates = forecast_df['ds']
                            preds = forecast_df['yhat']
                        else:
                            # Random Forest / custom
                            dates = forecast_df['date']
                            preds = forecast_df['forecast']
                            
                        ax.plot(dates, preds, label='Forecast', linestyle='--', color='red')
                        ax.legend()
                        ax.set_title("Sales Forecast")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Sales")
                        st.pyplot(fig)
                        
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
                        st.error(model_name) # Error message is in second return value if first is None
                        
    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Please upload a CSV file to get started. You can use the dummy data generated in `data/raw/sales.csv` for testing.")
    
    # Optional: Load default data button
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_data_path = os.path.join(base_path, "data", "raw", "sales1.csv")
    if os.path.exists(default_data_path):
        if st.checkbox("Use dummy data"):
            # Mock uploaded file behavior
            df = load_data(default_data_path)
            st.subheader("Historical Sales Data (Dummy)")
            st.line_chart(df['sales'])
            
            if st.button("Forecast on Dummy Data"):
                 forecast_df, model_name = forecast_next(df, days)
                 if forecast_df is not None:
                    st.subheader(f"Forecast ({days} days)")
                    st.write(f"Model: {model_name}")
                    if 'ds' in forecast_df.columns:
                        st.line_chart(forecast_df.set_index('ds')['yhat'])
                    else:
                        st.line_chart(forecast_df.set_index('date')['forecast'])
