# backend/utils/safety_spc_4_4.py
"""
Safety & Quality SPC Control Charts utility functions.

Chart 4.4: Safety & Quality SPC Control Charts
- Incident rates with mean/UCL/LCL
- Call out assignable-cause points
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.getData import read_data
from utils.kpi_bullets_4_1 import calculate_response_times


def calculate_incident_rate(
    df: pd.DataFrame,
    aggregation: str = 'month'  # 'month', 'week', 'year'
) -> List[Dict[str, Any]]:
    """
    Calculate incident rate based on cancelled/failed missions and response time anomalies.
    
    Uses:
    1. Cancelled missions (Status != 'Closed' or Cancel Reason != '<NONE>')
    2. Response time anomalies (excessive response times)
    
    Args:
        df: Operational data DataFrame
        aggregation: Aggregation level ('month', 'week', 'year')
    
    Returns:
        List of incident rate data points
    """
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    
    # Calculate response times
    response_times = calculate_response_times(df)
    # Ensure index alignment
    df['response_time_minutes'] = response_times.values if len(response_times) == len(df) else response_times
    
    # Define incidents based on quality/safety metrics
    # Since we don't have explicit incident data, we use quality indicators:
    # 1. Response time anomalies (excessive response time)
    # 2. Status issues (if not successful status)
    # 3. Cancelled missions
    
    # 1. Response time anomalies (excessive response time)
    # Use 75th percentile OR fixed 30 min threshold, whichever is lower (more sensitive)
    valid_rt = df['response_time_minutes'].dropna()
    if len(valid_rt) > 0:
        rt_threshold_percentile = valid_rt.quantile(0.75)  # 75th percentile
        rt_threshold_fixed = 30.0  # 30 minutes fixed threshold
        # Use the lower threshold to catch more issues (more sensitive)
        rt_threshold = min(rt_threshold_percentile, rt_threshold_fixed)
        df['rt_anomaly'] = df['response_time_minutes'] > rt_threshold
    else:
        df['rt_anomaly'] = False
    
    # 2. Non-successful status (if not Closed/Billed/Verified/Complete)
    if 'Status' in df.columns:
        successful_statuses = ['Closed', 'Billed', 'Verified', 'Complete']
        df['status_failed'] = ~df['Status'].isin(successful_statuses)
    else:
        df['status_failed'] = False
    
    # 3. Cancelled missions (if Cancel Reason exists and is not <NONE>)
    if 'Cancel Reason' in df.columns:
        df['cancelled'] = (df['Cancel Reason'].notna()) & (df['Cancel Reason'] != '<NONE>')
    else:
        df['cancelled'] = False
    
    # Combine incident indicators
    # Use response time anomalies as primary metric since they're most common
    df['is_incident'] = df['rt_anomaly'] | df['status_failed'] | df['cancelled']
    
    # Aggregate by time period
    if aggregation == 'month':
        df['period'] = df['tdate'].dt.to_period('M')
    elif aggregation == 'week':
        df['period'] = df['tdate'].dt.to_period('W')
    elif aggregation == 'year':
        df['period'] = df['tdate'].dt.year
    else:
        raise ValueError("aggregation must be 'month', 'week', or 'year'")
    
    incident_data = []
    
    for period, group_df in df.groupby('period'):
        total_missions = len(group_df)
        incidents = int(group_df['is_incident'].sum())
        
        if total_missions > 0:
            incident_rate = (incidents / total_missions) * 100  # Percentage
            
            # Calculate breakdown of incident types
            cancelled_count = int(group_df['cancelled'].sum()) if 'cancelled' in group_df.columns else 0
            status_failed_count = int(group_df['status_failed'].sum()) if 'status_failed' in group_df.columns else 0
            rt_anomaly_count = int(group_df['rt_anomaly'].sum()) if 'rt_anomaly' in group_df.columns else 0
            
            incident_data.append({
                'period': str(period),
                'date': group_df['tdate'].min() if len(group_df) > 0 else None,
                'total_missions': int(total_missions),
                'incidents': incidents,
                'incident_rate': float(incident_rate),
                'cancelled': cancelled_count,
                'status_failed': status_failed_count,
                'rt_anomaly': rt_anomaly_count
            })
    
    # Sort by period
    incident_data.sort(key=lambda x: x['period'])
    
    return incident_data


def calculate_control_limits(
    rates: List[float],
    method: str = '3sigma'  # '3sigma' or 'individual'
) -> Dict[str, float]:
    """
    Calculate SPC control limits.
    
    Args:
        rates: List of incident rates (percentages)
        method: Method for calculating limits ('3sigma' or 'individual')
    
    Returns:
        Dictionary with mean, UCL, LCL
    """
    if not rates:
        return {
            'mean': 0.0,
            'ucl': 0.0,
            'lcl': 0.0,
            'sigma': 0.0
        }
    
    rates_series = pd.Series(rates)
    mean = float(rates_series.mean())
    
    if method == '3sigma':
        # Standard 3-sigma control limits
        sigma = float(rates_series.std())
        ucl = mean + (3 * sigma)
        lcl = max(0, mean - (3 * sigma))  # Lower limit cannot be negative
    else:  # 'individual'
        # Individual moving range method
        # For small samples, use moving range
        if len(rates) > 1:
            moving_ranges = [abs(rates[i] - rates[i-1]) for i in range(1, len(rates))]
            avg_mr = np.mean(moving_ranges)
            sigma = avg_mr / 1.128  # d2 constant for n=2
        else:
            sigma = float(rates_series.std())
        
        ucl = mean + (3 * sigma)
        lcl = max(0, mean - (3 * sigma))
    
    return {
        'mean': mean,
        'ucl': float(ucl),
        'lcl': float(lcl),
        'sigma': float(sigma)
    }


def identify_assignable_causes(
    data: List[Dict[str, Any]],
    control_limits: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Identify assignable-cause points (points outside control limits).
    
    Args:
        data: List of incident rate data points
        control_limits: Dictionary with mean, UCL, LCL
    
    Returns:
        List of assignable-cause points
    """
    assignable_points = []
    
    for point in data:
        rate = point['incident_rate']
        is_out_of_control = False
        cause_type = None
        
        if rate > control_limits['ucl']:
            is_out_of_control = True
            cause_type = 'above_ucl'
        elif rate < control_limits['lcl']:
            is_out_of_control = True
            cause_type = 'below_lcl'
        
        # Also check for runs (8 consecutive points on same side of mean)
        # This is a simplified check - could be enhanced
        if is_out_of_control:
            assignable_points.append({
                'period': point['period'],
                'date': point['date'],
                'incident_rate': rate,
                'total_missions': point['total_missions'],
                'incidents': point['incidents'],
                'cause_type': cause_type,
                'violation': 'UCL' if cause_type == 'above_ucl' else 'LCL',
                'details': {
                    'cancelled': point.get('cancelled', 0),
                    'status_failed': point.get('status_failed', 0),
                    'rt_anomaly': point.get('rt_anomaly', 0)
                }
            })
    
    return assignable_points


def get_safety_spc_data(
    start_year: int = 2020,
    end_year: int = 2023,
    aggregation: str = 'month',
    method: str = '3sigma'
) -> Dict[str, Any]:
    """
    Main function to get safety SPC control chart data.
    
    Args:
        start_year: Start year for analysis
        end_year: End year for analysis
        aggregation: Aggregation level ('month', 'week', 'year')
        method: Control limit calculation method ('3sigma' or 'individual')
    
    Returns:
        Dictionary with SPC control chart data
    """
    df = read_data()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['year'] = df['tdate'].dt.year
    
    # Filter by year range
    df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    
    if len(df) == 0:
        return {
            'start_year': start_year,
            'end_year': end_year,
            'aggregation': aggregation,
            'data': [],
            'control_limits': {
                'mean': 0.0,
                'ucl': 0.0,
                'lcl': 0.0
            },
            'assignable_causes': [],
            'metadata': {
                'calculation_date': datetime.now().isoformat(),
                'data_points': 0
            }
        }
    
    # Calculate incident rates
    incident_data = calculate_incident_rate(df, aggregation=aggregation)
    
    if len(incident_data) == 0:
        return {
            'start_year': start_year,
            'end_year': end_year,
            'aggregation': aggregation,
            'data': [],
            'control_limits': {
                'mean': 0.0,
                'ucl': 0.0,
                'lcl': 0.0
            },
            'assignable_causes': [],
            'metadata': {
                'calculation_date': datetime.now().isoformat(),
                'data_points': 0
            }
        }
    
    # Calculate control limits
    rates = [d['incident_rate'] for d in incident_data]
    control_limits = calculate_control_limits(rates, method=method)
    
    # Identify assignable-cause points
    assignable_causes = identify_assignable_causes(incident_data, control_limits)
    
    return {
        'start_year': start_year,
        'end_year': end_year,
        'aggregation': aggregation,
        'method': method,
        'data': incident_data,
        'control_limits': control_limits,
        'assignable_causes': assignable_causes,
        'metadata': {
            'calculation_date': datetime.now().isoformat(),
            'data_points': len(incident_data),
            'total_periods': len(incident_data),
            'total_missions': sum(d['total_missions'] for d in incident_data),
            'total_incidents': sum(d['incidents'] for d in incident_data),
            'overall_rate': (sum(d['incidents'] for d in incident_data) / 
                           sum(d['total_missions'] for d in incident_data) * 100) 
                           if sum(d['total_missions'] for d in incident_data) > 0 else 0.0
        }
    }

