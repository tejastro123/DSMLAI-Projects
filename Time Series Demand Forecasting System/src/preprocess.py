import pandas as pd

def load_data(path):
    """
    Load sales data from CSV, parse dates, set index, and fill missing values.
    Expects CSV with columns: 'date', 'sales'
    """
    try:
        df = pd.read_csv(path)
        # Ensure column names are lower case for consistency
        df.columns = [c.lower() for c in df.columns]
        
        if 'date' not in df.columns or 'sales' not in df.columns:
            raise ValueError("CSV must contain 'date' and 'sales' columns.")
            
        df['date'] = pd.to_datetime(df['date'])
        
        # Aggregate logic for duplicate dates
        df = df.groupby('date')['sales'].sum().reset_index()
        
        df = df.sort_values('date')
        df.set_index('date', inplace=True)

        # Resample to daily frequency and fill missing values
        df = df.asfreq('D')
        df['sales'] = df['sales'].fillna(method='ffill')
        
        # specific handling for initial missing values if any remain
        df['sales'] = df['sales'].fillna(0) # or method='bfill'

        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
