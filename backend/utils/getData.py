import pandas as pd
import os

def read_data() -> pd.DataFrame:
    """
    Read data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
    Returns:
        DataFrame
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data','1_demand_forecasting', 'data.csv')
    return pd.read_csv(file_path, encoding='latin1')