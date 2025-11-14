# backend/utils/predicting/predict_demand.py
import joblib
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

def predict_demand(model_name: str, years: int) -> Dict[str, Any]:
    """Predict future demand (including historical data)"""

    # Get model file path (using absolute path, more reliable)
    current_file = Path(__file__).resolve()  
    backend_dir = current_file.parent.parent.parent
    model_dir = backend_dir / 'model'
    
    # Validate paths
    if not backend_dir.exists():
        raise FileNotFoundError(f"Backend directory not found: {backend_dir}")
    if not model_dir.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")
    
    # Validate parameters
    if model_name.lower() not in ['prophet', 'arima']:
        raise ValueError(f"Unsupported model type: {model_name}. Please use 'prophet' or 'arima'")
    
    if years < 1 or years > 10:
        raise ValueError(f"Prediction years must be between 1 and 10, current value: {years}")
    
    forecast_months = years * 12
    
    # Get historical data (2012-2023)
    historical_data = _get_historical_data(backend_dir)
    
    try:
        if model_name.lower() == 'prophet':
            forecast_result = _predict_prophet(model_dir, forecast_months)
        else:  # arima
            forecast_result = _predict_arima(model_dir, forecast_months)
        
        # Merge results
        result = {
            'model_type': forecast_result['model_type'],
            'historical_data': historical_data,
            'forecast_data': forecast_result['forecast_data'],
            'total_months': len(historical_data) + len(forecast_result['forecast_data'])
        }
        
        return result
        
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Model file not found: {e}")
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {str(e)}")


def _get_historical_data(backend_dir: Path) -> List[Dict[str, Any]]:
    """
    获取历史月度数据（2012年7月 - 2023年12月）
    
    返回:
    - list: 历史数据列表
    """
    # Read original data
    data_path = backend_dir / 'data' / '1_demand_forecasting' / 'data.csv'
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path, encoding='latin1')
    
    # Convert date format
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df = df[df['tdate'].notna()]
    
    # Aggregate by month
    monthly_data = df.groupby(df['tdate'].dt.to_period('M')).size().reset_index(name='count')
    monthly_data['date'] = monthly_data['tdate'].astype(str) + '-01'
    monthly_data['date'] = pd.to_datetime(monthly_data['date'])
    
    # Ensure only data up to 2023-12-01
    monthly_data = monthly_data[monthly_data['date'] <= pd.Timestamp('2023-12-01')]
    
    # Sort by date
    monthly_data = monthly_data.sort_values('date')
    
    # Convert to dictionary format
    historical_data = []
    for _, row in monthly_data.iterrows():
        historical_data.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'count': int(row['count'])
        })
    
    return historical_data


def _predict_prophet(model_dir: Path, forecast_months: int) -> Dict[str, Any]:
    """Predict demand using Prophet model"""
    model_path = model_dir / 'model_prophet.pkl'
    
    if not model_path.exists():
        raise FileNotFoundError(f"Prophet model file not found: {model_path}")
    
    # Load model
    model = joblib.load(model_path)
    
    # Create future dataframe and predict (from 2024-01-01)
    # Prophet will automatically predict from the last date of historical data
    future = model.make_future_dataframe(periods=forecast_months, freq='M')
    forecast = model.predict(future)
    
    # Extract future prediction (only return future part, from 2024-01-01)
    # Filter out data from 2024-01-01 and onwards
    forecast['ds'] = pd.to_datetime(forecast['ds'])
    future_forecast = forecast[forecast['ds'] >= pd.Timestamp('2024-01-01')]
    future_forecast = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(forecast_months)

    result = {
        'model_type': 'prophet',
        'forecast_months': forecast_months,
        'forecast_data': []
    }
    
    for _, row in future_forecast.iterrows():
        result['forecast_data'].append({
            'date': row['ds'].strftime('%Y-%m-%d'),
            'predicted_count': int(round(row['yhat'])),
            'lower_bound': int(round(row['yhat_lower'])),
            'upper_bound': int(round(row['yhat_upper']))
        })
    
    return result


def _predict_arima(model_dir: Path, forecast_months: int) -> Dict[str, Any]:
    """Predict demand using ARIMA model"""
    model_path = model_dir / 'model_arima.pkl'
    
    if not model_path.exists():
        raise FileNotFoundError(f"ARIMA model file not found: {model_path}")
    
    # Load model
    model = joblib.load(model_path)
    
    # ARIMA model uses get_forecast method to get prediction and confidence interval
    forecast_result = model.get_forecast(steps=forecast_months)
    forecast_values = forecast_result.predicted_mean
    forecast_ci = forecast_result.conf_int()
    
    # Convert to numpy array for indexing
    if hasattr(forecast_values, 'values'):
        pred_array = forecast_values.values
    elif isinstance(forecast_values, pd.Series):
        pred_array = forecast_values.values
    else:
        pred_array = np.array(forecast_values)
    
    # Generate future dates (from 2024-01-01)
    start_date = pd.Timestamp('2024-01-01')
    future_dates = pd.date_range(start=start_date, periods=forecast_months, freq='M')
    
    # Convert to dictionary format
    result = {
        'model_type': 'arima',
        'forecast_months': forecast_months,
        'forecast_data': []
    }
    
    for i, date in enumerate(future_dates):
        # Get prediction and confidence interval
        pred_value = float(pred_array[i])
        
        # Handle confidence interval (DataFrame format)
        if isinstance(forecast_ci, pd.DataFrame):
            lower = float(forecast_ci.iloc[i, 0])
            upper = float(forecast_ci.iloc[i, 1])
        else:
            # If numpy array
            lower = float(forecast_ci[i, 0])
            upper = float(forecast_ci[i, 1])
        
        result['forecast_data'].append({
            'date': date.strftime('%Y-%m-%d'),
            'predicted_count': int(round(pred_value)),
            'lower_bound': int(round(lower)),
            'upper_bound': int(round(upper))
        })
    
    return result