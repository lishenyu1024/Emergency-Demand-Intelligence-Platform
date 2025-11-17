# backend/utils/cost_benefit_4_3.py
"""
Cost-Benefit-Throughput Dual-Axis utility functions.

Chart 4.3: Cost–Benefit–Throughput Dual-Axis
- Unit service cost vs. social benefit / revenue
- Annotate key inflection points and scenario labels
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from utils.getData import read_data
from utils.kpi_bullets_4_1 import calculate_unit_cost, calculate_missions_per_population


def calculate_unit_cost_trend(df: pd.DataFrame, start_year: int = 2020, end_year: int = 2023) -> List[Dict[str, Any]]:
    """
    Calculate unit cost trend over time.
    
    Args:
        df: Operational data DataFrame
        start_year: Start year
        end_year: End year
    
    Returns:
        List of cost data points by year/month
    """
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['year'] = df['tdate'].dt.year
    df['month'] = df['tdate'].dt.month
    df['year_month'] = df['tdate'].dt.to_period('M')
    
    cost_trend = []
    
    # Calculate monthly
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            month_df = df[(df['year'] == year) & (df['month'] == month)]
            
            if len(month_df) > 0:
                cost_metrics = calculate_unit_cost(month_df, year)
                
                cost_trend.append({
                    'date': f'{year}-{month:02d}',
                    'year': year,
                    'month': month,
                    'unit_cost': cost_metrics['unit_cost_per_mission'],
                    'total_cost': cost_metrics['estimated_annual_cost'],
                    'missions': cost_metrics['total_missions']
                })
    
    return cost_trend


def calculate_throughput_trend(df: pd.DataFrame, start_year: int = 2020, end_year: int = 2023) -> List[Dict[str, Any]]:
    """
    Calculate throughput (missions) trend over time.
    
    Args:
        df: Operational data DataFrame
        start_year: Start year
        end_year: End year
    
    Returns:
        List of throughput data points by year/month
    """
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['year'] = df['tdate'].dt.year
    df['month'] = df['tdate'].dt.month
    
    throughput_trend = []
    
    # Calculate monthly
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            month_df = df[(df['year'] == year) & (df['month'] == month)]
            
            if len(month_df) > 0:
                missions_metrics = calculate_missions_per_population(month_df, year)
                
                throughput_trend.append({
                    'date': f'{year}-{month:02d}',
                    'year': year,
                    'month': month,
                    'missions': missions_metrics['total_missions'],
                    'missions_per_1000': missions_metrics['missions_per_1000']
                })
    
    return throughput_trend


def estimate_social_benefit(missions: int, avg_cost_per_mission: float) -> float:
    """
    Estimate social benefit from missions.
    
    This is a simplified calculation. In reality, social benefit would include:
    - Lives saved / health outcomes improved
    - Economic value of preventing disability/death
    - Healthcare cost savings
    
    For now, we use missions as a proxy for social benefit, scaled by a multiplier.
    
    Args:
        missions: Number of missions
        avg_cost_per_mission: Average cost per mission
    
    Returns:
        Estimated social benefit value
    """
    # Rough estimate: assume each mission provides social value equivalent to
    # multiple times the cost (e.g., 3-5x for critical care transport)
    social_value_multiplier = 4.0  # Conservative estimate
    social_benefit = missions * avg_cost_per_mission * social_value_multiplier
    
    return float(social_benefit)


def identify_inflection_points(cost_data: List[Dict[str, Any]], throughput_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify key inflection points in cost and throughput trends.
    
    Looks for significant changes in slopes or trend reversals.
    
    Args:
        cost_data: Unit cost trend data
        throughput_data: Throughput trend data
    
    Returns:
        List of inflection point annotations
    """
    inflection_points = []
    
    if len(cost_data) < 3 or len(throughput_data) < 3:
        return inflection_points
    
    # Calculate cost changes
    cost_values = [d['unit_cost'] for d in cost_data]
    throughput_values = [d['missions'] for d in throughput_data]
    
    # Find significant changes (e.g., >20% change from previous period)
    for i in range(1, len(cost_data)):
        if i >= len(cost_values) or i >= len(throughput_values):
            continue
        
        prev_cost = cost_values[i-1]
        curr_cost = cost_values[i]
        prev_throughput = throughput_values[i-1]
        curr_throughput = throughput_values[i]
        
        if prev_cost > 0 and prev_throughput > 0:
            cost_change_pct = abs((curr_cost - prev_cost) / prev_cost) * 100
            throughput_change_pct = abs((curr_throughput - prev_throughput) / prev_throughput) * 100
            
            # Significant change threshold
            if cost_change_pct > 15 or throughput_change_pct > 20:
                inflection_points.append({
                    'date': cost_data[i]['date'],
                    'type': 'significant_change',
                    'cost_change_pct': cost_change_pct,
                    'throughput_change_pct': throughput_change_pct,
                    'label': f"Significant change at {cost_data[i]['date']}"
                })
    
    # Find minimum cost point
    if len(cost_values) > 0:
        min_cost_idx = np.argmin(cost_values)
        inflection_points.append({
            'date': cost_data[min_cost_idx]['date'],
            'type': 'min_cost',
            'value': cost_values[min_cost_idx],
            'label': f"Lowest cost: ${cost_values[min_cost_idx]:.0f}"
        })
    
    # Find maximum throughput point
    if len(throughput_values) > 0:
        max_throughput_idx = np.argmax(throughput_values)
        inflection_points.append({
            'date': throughput_data[max_throughput_idx]['date'],
            'type': 'max_throughput',
            'value': throughput_values[max_throughput_idx],
            'label': f"Peak throughput: {throughput_values[max_throughput_idx]:.0f} missions"
        })
    
    return inflection_points


def get_cost_benefit_throughput_data(
    start_year: int = 2020,
    end_year: int = 2023,
    aggregation: str = 'month'  # 'month' or 'year'
) -> Dict[str, Any]:
    """
    Main function to get cost-benefit-throughput dual-axis data.
    
    Args:
        start_year: Start year for analysis
        end_year: End year for analysis
        aggregation: Aggregation level ('month' or 'year')
    
    Returns:
        Dictionary with cost-benefit-throughput data
    """
    df = read_data()
    
    # Calculate trends
    cost_trend = calculate_unit_cost_trend(df, start_year, end_year)
    throughput_trend = calculate_throughput_trend(df, start_year, end_year)
    
    # Merge cost and throughput data by date
    cost_dict = {d['date']: d for d in cost_trend}
    throughput_dict = {d['date']: d for d in throughput_trend}
    
    # Combine data
    combined_data = []
    all_dates = sorted(set(list(cost_dict.keys()) + list(throughput_dict.keys())))
    
    for date in all_dates:
        cost_point = cost_dict.get(date, {})
        throughput_point = throughput_dict.get(date, {})
        
        missions = throughput_point.get('missions', 0)
        unit_cost = cost_point.get('unit_cost', 0)
        
        # Calculate social benefit
        social_benefit = estimate_social_benefit(missions, unit_cost) if missions > 0 and unit_cost > 0 else 0
        
        combined_data.append({
            'date': date,
            'year': cost_point.get('year') or throughput_point.get('year'),
            'month': cost_point.get('month') or throughput_point.get('month'),
            'unit_cost': unit_cost,
            'total_cost': cost_point.get('total_cost', 0),
            'missions': missions,
            'missions_per_1000': throughput_point.get('missions_per_1000', 0),
            'social_benefit': social_benefit,
            'benefit_cost_ratio': social_benefit / unit_cost if unit_cost > 0 else 0
        })
    
    # Sort by date
    combined_data.sort(key=lambda x: x['date'])
    
    # Aggregate by year if requested
    if aggregation == 'year':
        yearly_data = {}
        for point in combined_data:
            year = point['year']
            if year not in yearly_data:
                yearly_data[year] = {
                    'year': year,
                    'date': f'{year}',
                    'total_cost': 0,
                    'total_missions': 0,
                    'unit_costs': [],
                    'social_benefits': []
                }
            
            yearly_data[year]['total_cost'] += point.get('total_cost', 0)
            yearly_data[year]['total_missions'] += point.get('missions', 0)
            if point.get('unit_cost', 0) > 0:
                yearly_data[year]['unit_costs'].append(point['unit_cost'])
            if point.get('social_benefit', 0) > 0:
                yearly_data[year]['social_benefits'].append(point['social_benefit'])
        
        # Calculate averages
        combined_data = []
        for year, data in yearly_data.items():
            avg_unit_cost = np.mean(data['unit_costs']) if data['unit_costs'] else 0
            avg_social_benefit = np.mean(data['social_benefits']) if data['social_benefits'] else 0
            
            combined_data.append({
                'date': data['date'],
                'year': year,
                'month': None,
                'unit_cost': avg_unit_cost,
                'total_cost': data['total_cost'],
                'missions': data['total_missions'],
                'missions_per_1000': 0,  # Would need population for this
                'social_benefit': avg_social_benefit,
                'benefit_cost_ratio': avg_social_benefit / avg_unit_cost if avg_unit_cost > 0 else 0
            })
        
        combined_data.sort(key=lambda x: x['date'])
    
    # Identify inflection points
    inflection_points = identify_inflection_points(cost_trend, throughput_trend)
    
    return {
        'start_year': start_year,
        'end_year': end_year,
        'aggregation': aggregation,
        'data': combined_data,
        'inflection_points': inflection_points,
        'metadata': {
            'calculation_date': datetime.now().isoformat(),
            'data_points': len(combined_data),
            'avg_unit_cost': np.mean([d['unit_cost'] for d in combined_data if d['unit_cost'] > 0]) if combined_data else 0,
            'avg_missions': np.mean([d['missions'] for d in combined_data if d['missions'] > 0]) if combined_data else 0
        }
    }

