import pandas as pd

def load_data(path, store_id=None, product_id=None):
    """
    Load sales data from CSV, parse dates, set index, and fill missing values.
    Expects CSV with columns: 'date', 'sales' (or mapped equivalents).
    Optional filters: store_id, product_id
    Returns: 
        - df: Processed DataFrame
        - options: Dictionary with available 'stores' and 'products'
    """
    try:
        df = pd.read_csv(path)
        
        # Normalize column names: lowercase and replace spaces
        df.rename(columns=lambda x: x.strip().lower().replace(' ', '_'), inplace=True)
        
        # Map specific columns implies by sales2.csv structure
        if 'units_sold' in df.columns:
            df.rename(columns={'units_sold': 'sales'}, inplace=True)
            
        if 'date' not in df.columns or 'sales' not in df.columns:
            raise ValueError(f"CSV must contain 'date' and 'sales' columns. Found: {df.columns.tolist()}")
            
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract options for UI
        options = {
            'stores': sorted(df['store_id'].unique().tolist()) if 'store_id' in df.columns else [],
            'products': sorted(df['product_id'].unique().tolist()) if 'product_id' in df.columns else []
        }
        
        # Apply filters if provided
        if store_id:
            if 'store_id' in df.columns:
                df = df[df['store_id'] == store_id]
            else:
                print("Warning: store_id filter requested but column not found.")
                
        if product_id:
            if 'product_id' in df.columns:
                df = df[df['product_id'] == product_id]
            else:
                print("Warning: product_id filter requested but column not found.")
        
        # Aggregate logic for duplicate dates (e.g. if we didn't filter down to a single unique item)
        # This sums sales across all stores/products if no filter is applied, 
        # or for the specific selection.
        if 'store_id' in df.columns and 'product_id' in df.columns:
             # Use average price etc if needed later, but for now we just need sales sum
             pass
             
        df = df.groupby('date')['sales'].sum().reset_index()
        
        df = df.sort_values('date')
        df.set_index('date', inplace=True)

        # Resample to daily frequency and fill missing values
        df = df.asfreq('D')
        df['sales'] = df['sales'].fillna(method='ffill')
        df['sales'] = df['sales'].fillna(0) # Initial NaN

        return df, options
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, {'stores': [], 'products': []}
