# backend/utils/trend_wall_4_2.py
"""
Trend Wall utility functions.

Chart 4.2: Trend Wall (Metric Cards + Lines)
- KPI cards (YTD, YoY)
- Monthly lines with short forecast tails
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.getData import read_data
from utils.kpi_bullets_4_1 import (
    calculate_missions_per_population,
    calculate_sla_attainment,
    calculate_unmet_demand,
    calculate_transfer_success_rate,
    calculate_flight_hours,
    calculate_unit_cost,
    calculate_response_times
)


def calculate_ytd_metrics(df: pd.DataFrame, current_year: int, current_month: Optional[int] = None) -> Dict[str, Any]:
    """
    Calculate Year-to-Date (YTD) metrics.
    
    Args:
        df: Operational data DataFrame
        current_year: Current year
        current_month: Current month (if None, uses all months)
    
    Returns:
        Dictionary with YTD metrics
    """
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['year'] = df['tdate'].dt.year
    df['month'] = df['tdate'].dt.month
    
    # Filter for current year
    ytd_df = df[df['year'] == current_year].copy()
    
    if current_month is not None:
        ytd_df = ytd_df[ytd_df['month'] <= current_month]
    
    if len(ytd_df) == 0:
        return {
            'missions': 0,
            'sla_attainment': 0.0,
            'unmet_demand_rate': 0.0,
            'transfer_success_rate': 0.0,
            'flight_hours': 0.0,
            'unit_cost': 0.0
        }
    
    # Calculate metrics
    missions_metrics = calculate_missions_per_population(ytd_df, current_year)
    sla_metrics = calculate_sla_attainment(ytd_df)
    unmet_metrics = calculate_unmet_demand(ytd_df)
    transfer_metrics = calculate_transfer_success_rate(ytd_df)
    flight_hours_metrics = calculate_flight_hours(ytd_df)
    cost_metrics = calculate_unit_cost(ytd_df, current_year)
    
    return {
        'missions': missions_metrics['total_missions'],
        'missions_per_1000': missions_metrics['missions_per_1000'],
        'sla_attainment': sla_metrics['attainment_rate'],
        'median_response_time': sla_metrics['median_response_time'],
        'unmet_demand_rate': unmet_metrics['unmet_demand_rate'],
        'transfer_success_rate': transfer_metrics['success_rate'],
        'flight_hours': flight_hours_metrics['total_flight_hours'],
        'unit_cost': cost_metrics['unit_cost_per_mission']
    }


def calculate_yoy_change(current_value: float, previous_value: float) -> Dict[str, Any]:
    """
    Calculate Year-over-Year (YoY) change.
    
    Args:
        current_value: Current period value
        previous_value: Previous period value
    
    Returns:
        Dictionary with YoY change metrics
    """
    if previous_value == 0:
        if current_value == 0:
            pct_change = 0.0
        else:
            pct_change = 100.0  # Infinite growth
    else:
        pct_change = ((current_value - previous_value) / previous_value) * 100
    
    absolute_change = current_value - previous_value
    
    return {
        'absolute_change': float(absolute_change),
        'percentage_change': float(pct_change),
        'is_positive': pct_change > 0
    }


def get_monthly_metrics(df: pd.DataFrame, start_year: int = 2020, end_year: int = 2023) -> List[Dict[str, Any]]:
    """
    Get monthly metrics for trend lines.
    
    Args:
        df: Operational data DataFrame
        start_year: Start year for trend
        end_year: End year for trend
    
    Returns:
        List of monthly metric dictionaries
    """
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['year'] = df['tdate'].dt.year
    df['month'] = df['tdate'].dt.month
    df['year_month'] = df['tdate'].dt.to_period('M')
    
    monthly_data = []
    
    # Generate all months in range
    current_date = pd.Period(f'{start_year}-01', freq='M')
    end_date = pd.Period(f'{end_year}-12', freq='M')
    
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        
        # Filter for this month
        month_df = df[(df['year'] == year) & (df['month'] == month)]
        
        if len(month_df) > 0:
            # Calculate metrics
            missions_count = len(month_df)
            sla_metrics = calculate_sla_attainment(month_df)
            unmet_metrics = calculate_unmet_demand(month_df)
            transfer_metrics = calculate_transfer_success_rate(month_df)
            flight_hours_metrics = calculate_flight_hours(month_df)
            cost_metrics = calculate_unit_cost(month_df, year)
            
            monthly_data.append({
                'date': str(current_date),
                'year': year,
                'month': month,
                'missions': missions_count,
                'sla_attainment': sla_metrics['attainment_rate'],
                'unmet_demand_rate': unmet_metrics['unmet_demand_rate'],
                'transfer_success_rate': transfer_metrics['success_rate'],
                'flight_hours': flight_hours_metrics['total_flight_hours'],
                'unit_cost': cost_metrics['unit_cost_per_mission']
            })
        
        current_date += 1  # Move to next month
    
    return monthly_data


def get_forecast_tail(historical_data: List[Dict[str, Any]], months_ahead: int = 6) -> List[Dict[str, Any]]:
    """
    Generate a simple forecast tail for the next few months.
    
    Uses simple linear extrapolation based on recent trend.
    
    Args:
        historical_data: Historical monthly data
        months_ahead: Number of months to forecast
    
    Returns:
        List of forecast data points
    """
    if len(historical_data) < 3:
        return []
    
    # Get last 6 months for trend calculation
    recent_data = historical_data[-6:] if len(historical_data) >= 6 else historical_data
    
    # Calculate average monthly change
    metrics = ['missions', 'sla_attainment', 'unmet_demand_rate', 'transfer_success_rate', 'flight_hours', 'unit_cost']
    forecast_data = []
    
    # Get last data point
    last_point = recent_data[-1]
    last_period = pd.Period(last_point['date'])
    
    # Calculate trends
    trends = {}
    for metric in metrics:
        values = [d[metric] for d in recent_data if metric in d]
        if len(values) >= 2:
            # Simple linear trend
            trend = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
            trends[metric] = trend
        else:
            trends[metric] = 0
    
    # Generate forecast
    for i in range(1, months_ahead + 1):
        forecast_period = last_period + i
        forecast_point = {
            'date': str(forecast_period),
            'year': forecast_period.year,
            'month': forecast_period.month,
            'is_forecast': True
        }
        
        for metric in metrics:
            forecast_value = last_point.get(metric, 0) + (trends.get(metric, 0) * i)
            # Apply bounds
            if 'rate' in metric or 'attainment' in metric:
                forecast_value = max(0, min(100, forecast_value))
            elif 'cost' in metric:
                forecast_value = max(0, forecast_value)
            else:
                forecast_value = max(0, forecast_value)
            
            forecast_point[metric] = forecast_value
        
        forecast_data.append(forecast_point)
    
    return forecast_data


def get_trend_wall_data(
    current_year: int = 2023,
    current_month: Optional[int] = None,
    forecast_months: int = 6
) -> Dict[str, Any]:
    """
    Main function to get trend wall data.
    
    Args:
        current_year: Current year
        current_month: Current month (if None, uses all months)
        forecast_months: Number of months to forecast ahead
    
    Returns:
        Dictionary with trend wall data
    """
    df = read_data()
    
    # Calculate YTD metrics
    ytd_metrics = calculate_ytd_metrics(df, current_year, current_month)
    
    # Calculate previous year metrics for YoY comparison
    previous_year = current_year - 1
    previous_ytd_metrics = calculate_ytd_metrics(df, previous_year, current_month)
    
    # Calculate YoY changes
    yoy_changes = {}
    for metric in ['missions', 'sla_attainment', 'unmet_demand_rate', 'transfer_success_rate', 'flight_hours', 'unit_cost']:
        yoy_changes[metric] = calculate_yoy_change(
            ytd_metrics.get(metric, 0),
            previous_ytd_metrics.get(metric, 0)
        )
    
    # Get monthly historical data
    start_year = max(2020, current_year - 3)  # Last 3-4 years
    monthly_data = get_monthly_metrics(df, start_year=start_year, end_year=current_year)
    
    # Get forecast tail
    forecast_data = []
    if len(monthly_data) > 0:
        forecast_data = get_forecast_tail(monthly_data, months_ahead=forecast_months)
    
    # Prepare KPI cards
    kpi_cards = [
        {
            'id': 'missions',
            'title': 'Total Missions',
            'current_value': ytd_metrics['missions'],
            'previous_value': previous_ytd_metrics['missions'],
            'yoy_change': yoy_changes['missions'],
            'unit': 'missions',
            'subtitle': f"{ytd_metrics.get('missions_per_1000', 0):.2f} per 1,000 pop"
        },
        {
            'id': 'sla_attainment',
            'title': 'SLA Attainment',
            'current_value': ytd_metrics['sla_attainment'],
            'previous_value': previous_ytd_metrics['sla_attainment'],
            'yoy_change': yoy_changes['sla_attainment'],
            'unit': '%',
            'subtitle': f"Median: {ytd_metrics.get('median_response_time', 0):.1f} min"
        },
        {
            'id': 'unmet_demand_rate',
            'title': 'Unmet Demand Rate',
            'current_value': ytd_metrics['unmet_demand_rate'],
            'previous_value': previous_ytd_metrics['unmet_demand_rate'],
            'yoy_change': yoy_changes['unmet_demand_rate'],
            'unit': '%'
        },
        {
            'id': 'transfer_success_rate',
            'title': 'Transfer Success Rate',
            'current_value': ytd_metrics['transfer_success_rate'],
            'previous_value': previous_ytd_metrics['transfer_success_rate'],
            'yoy_change': yoy_changes['transfer_success_rate'],
            'unit': '%'
        },
        {
            'id': 'flight_hours',
            'title': 'Flight Hours',
            'current_value': ytd_metrics['flight_hours'],
            'previous_value': previous_ytd_metrics['flight_hours'],
            'yoy_change': yoy_changes['flight_hours'],
            'unit': 'hours'
        },
        {
            'id': 'unit_cost',
            'title': 'Unit Cost per Mission',
            'current_value': ytd_metrics['unit_cost'],
            'previous_value': previous_ytd_metrics['unit_cost'],
            'yoy_change': yoy_changes['unit_cost'],
            'unit': '$'
        }
    ]
    
    # Prepare trend lines (combine historical + forecast)
    trend_lines = {}
    for metric in ['missions', 'sla_attainment', 'unmet_demand_rate', 'transfer_success_rate', 'flight_hours', 'unit_cost']:
        historical_points = [
            {'date': d['date'], 'value': d[metric], 'is_forecast': False}
            for d in monthly_data if metric in d
        ]
        forecast_points = [
            {'date': d['date'], 'value': d[metric], 'is_forecast': True}
            for d in forecast_data if metric in d
        ]
        trend_lines[metric] = historical_points + forecast_points
    
    return {
        'current_year': current_year,
        'current_month': current_month,
        'kpi_cards': kpi_cards,
        'trend_lines': trend_lines,
        'metadata': {
            'calculation_date': datetime.now().isoformat(),
            'historical_months': len(monthly_data),
            'forecast_months': len(forecast_data)
        }
    }

