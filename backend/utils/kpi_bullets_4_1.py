# backend/utils/kpi_bullets_4_1.py
"""
Core KPI Bullet Charts utility functions.

This module provides functions to calculate and format core KPIs for executive dashboards.

Chart 4.1: Core KPI Bullet Charts (Board Summary)
- Missions (total / per 1,000 pop)
- SLA attainment (median/95th response time)
- Unmet demand
- Transfer success rate
- Flight hours
- Unit cost
- Bullet charts vs target/historic trend
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


def calculate_response_times(df: pd.DataFrame) -> pd.Series:
    """
    Calculate response times for missions.
    
    Args:
        df: Operational data DataFrame
    
    Returns:
        Series with response times in minutes
    """
    df = df.copy()
    
    # Parse times
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['disptime'] = df['disptime'].astype(str).str[:5]
    df['enrtime'] = df['enrtime'].astype(str).str[:5]
    
    df['disptime_dt'] = pd.to_datetime(
        df['tdate'].astype(str) + ' ' + df['disptime'],
        format='%Y-%m-%d %H:%M',
        errors='coerce'
    )
    df['enrtime_dt'] = pd.to_datetime(
        df['tdate'].astype(str) + ' ' + df['enrtime'],
        format='%Y-%m-%d %H:%M',
        errors='coerce'
    )
    
    # Calculate response time
    response_times = []
    for _, row in df.iterrows():
        if pd.notna(row['disptime_dt']) and pd.notna(row['enrtime_dt']):
            if row['enrtime_dt'] < row['disptime_dt']:
                rt = (row['enrtime_dt'] + pd.Timedelta(days=1) - row['disptime_dt']).total_seconds() / 60
            else:
                rt = (row['enrtime_dt'] - row['disptime_dt']).total_seconds() / 60
            response_times.append(rt)
        else:
            response_times.append(None)
    
    return pd.Series(response_times)


def calculate_sla_attainment(df: pd.DataFrame, sla_target_minutes: int = 20) -> Dict[str, float]:
    """
    Calculate SLA attainment metrics.
    
    Args:
        df: Operational data DataFrame
        sla_target_minutes: SLA target in minutes (default: 20)
    
    Returns:
        Dictionary with SLA metrics
    """
    response_times = calculate_response_times(df)
    valid_rt = response_times.dropna()
    
    if len(valid_rt) == 0:
        return {
            'attainment_rate': 0.0,
            'median_response_time': 0.0,
            'p95_response_time': 0.0,
            'mean_response_time': 0.0,
            'within_sla_count': 0,
            'total_count': 0
        }
    
    within_sla = (valid_rt <= sla_target_minutes).sum()
    total = len(valid_rt)
    attainment_rate = (within_sla / total * 100) if total > 0 else 0.0
    
    return {
        'attainment_rate': float(attainment_rate),
        'median_response_time': float(valid_rt.median()),
        'p95_response_time': float(valid_rt.quantile(0.95)),
        'mean_response_time': float(valid_rt.mean()),
        'within_sla_count': int(within_sla),
        'total_count': int(total)
    }


def calculate_transfer_success_rate(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate transfer success rate.
    
    Args:
        df: Operational data DataFrame
    
    Returns:
        Dictionary with transfer success metrics
    """
    if 'Status' not in df.columns:
        return {
            'success_rate': 100.0,
            'successful_transfers': len(df),
            'total_transfers': len(df)
        }
    
    total = len(df)
    
    # Count successful transfers: Status indicates completion (Closed, Billed, Verified, Complete)
    # and Cancel Reason is <NONE> or empty
    successful_statuses = ['Closed', 'Billed', 'Verified', 'Complete']
    
    if 'Cancel Reason' in df.columns:
        # Successful: status indicates completion AND no cancellation
        successful = len(df[
            (df['Status'].isin(successful_statuses)) & 
            ((df['Cancel Reason'].isna()) | (df['Cancel Reason'] == '<NONE>'))
        ])
        # Cancelled: has a cancellation reason
        cancelled = len(df[
            (df['Cancel Reason'].notna()) & (df['Cancel Reason'] != '<NONE>')
        ])
        # Other cases (status not in successful list but no cancellation)
        # This might include pending/in-progress cases
    else:
        # If no Cancel Reason column, assume successful statuses are successful
        successful = len(df[df['Status'].isin(successful_statuses)])
        cancelled = total - successful
    
    success_rate = (successful / total * 100) if total > 0 else 0.0
    
    return {
        'success_rate': float(success_rate),
        'successful_transfers': int(successful),
        'cancelled_transfers': int(cancelled),
        'total_transfers': int(total)
    }


def calculate_flight_hours(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate flight hours from operational data.
    
    Uses enrtime (en route time) to atdtime (arrived at destination time) for flight duration.
    Falls back to estimated duration based on mileage if times not available.
    
    Args:
        df: Operational data DataFrame
    
    Returns:
        Dictionary with flight hour metrics
    """
    df = df.copy()
    
    # Parse times
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['enrtime'] = df['enrtime'].astype(str).str[:5]
    
    # Try to parse atdtime
    if 'atdtime' in df.columns and 'atddate' in df.columns:
        df['atdtime'] = df['atdtime'].astype(str).str[:5]
        
        df['enrtime_dt'] = pd.to_datetime(
            df['tdate'].astype(str) + ' ' + df['enrtime'],
            format='%Y-%m-%d %H:%M',
            errors='coerce'
        )
        df['atdtime_dt'] = pd.to_datetime(
            df['atddate'].astype(str) + ' ' + df['atdtime'],
            format='%Y-%m-%d %H:%M',
            errors='coerce'
        )
        
        # Calculate flight duration
        flight_hours = []
        for _, row in df.iterrows():
            if pd.notna(row['enrtime_dt']) and pd.notna(row['atdtime_dt']):
                if row['atdtime_dt'] < row['enrtime_dt']:
                    duration = (row['atdtime_dt'] + pd.Timedelta(days=1) - row['enrtime_dt']).total_seconds() / 3600
                else:
                    duration = (row['atdtime_dt'] - row['enrtime_dt']).total_seconds() / 3600
                
                # Filter out unrealistic durations (e.g., negative or > 10 hours)
                if 0 < duration <= 10:
                    flight_hours.append(duration)
                else:
                    flight_hours.append(None)
            else:
                flight_hours.append(None)
        
        valid_hours = pd.Series(flight_hours).dropna()
        
        if len(valid_hours) > 0:
            return {
                'total_flight_hours': float(valid_hours.sum()),
                'avg_flight_hours_per_mission': float(valid_hours.mean()),
                'total_missions': int(len(valid_hours))
            }
    
    # Fallback: Estimate flight hours based on mileage
    # Assume average speed of 120 mph (helicopter) or 300 mph (airplane)
    if 'Mileage - Loaded' in df.columns:
        mileage = pd.to_numeric(df['Mileage - Loaded'], errors='coerce').dropna()
        if len(mileage) > 0:
            # Estimate: average speed ~120 mph for helicopters
            # Adjust based on vehicle type if available
            avg_speed_mph = 120  # Default for helicopters
            estimated_hours = mileage / avg_speed_mph
            
            return {
                'total_flight_hours': float(estimated_hours.sum()),
                'avg_flight_hours_per_mission': float(estimated_hours.mean()),
                'total_missions': int(len(estimated_hours)),
                'note': 'Estimated from mileage'
            }
    
    # Last resort: Use a default estimate
    total_missions = len(df)
    avg_hours_per_mission = 1.5  # Conservative estimate
    estimated_total = total_missions * avg_hours_per_mission
    
    return {
        'total_flight_hours': float(estimated_total),
        'avg_flight_hours_per_mission': float(avg_hours_per_mission),
        'total_missions': int(total_missions),
        'note': 'Estimated default'
    }


def calculate_missions_per_population(df: pd.DataFrame, year: Optional[int] = None) -> Dict[str, float]:
    """
    Calculate missions per 1,000 population.
    
    Args:
        df: Operational data DataFrame
        year: Year to filter (if None, uses all data)
    
    Returns:
        Dictionary with missions per population metrics
    """
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    
    if year:
        df['year'] = df['tdate'].dt.year
        df = df[df['year'] == year]
    
    total_missions = len(df)
    
    # Load population data
    try:
        from utils.getData import read_data
        import json
        from pathlib import Path
        
        backend_dir = Path(__file__).parent.parent
        
        # Try to get county population for the year
        county_pop_path = backend_dir / 'data' / 'processed' / 'county_population_2020_2024.csv'
        if county_pop_path.exists():
            county_pop = pd.read_csv(county_pop_path)
            
            if year and year in county_pop['year'].values:
                total_population = county_pop[county_pop['year'] == year]['population'].sum()
            else:
                # Use most recent year
                latest_year = county_pop['year'].max()
                total_population = county_pop[county_pop['year'] == latest_year]['population'].sum()
        else:
            # Estimate: Maine population ~1.3M
            total_population = 1300000
        
        missions_per_1000 = (total_missions / total_population * 1000) if total_population > 0 else 0.0
        
    except Exception as e:
        print(f"Warning: Could not load population data: {e}")
        # Fallback: use estimate
        total_population = 1300000
        missions_per_1000 = (total_missions / total_population * 1000) if total_population > 0 else 0.0
    
    return {
        'total_missions': int(total_missions),
        'total_population': int(total_population),
        'missions_per_1000': float(missions_per_1000)
    }


def calculate_unit_cost(df: pd.DataFrame, year: Optional[int] = None) -> Dict[str, float]:
    """
    Calculate unit cost per mission.
    
    Args:
        df: Operational data DataFrame
        year: Year to filter (if None, uses all data)
    
    Returns:
        Dictionary with unit cost metrics
    """
    # Estimate costs based on fleet size and missions
    # This is a simplified calculation - in reality, would use actual cost data
    
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    
    if year:
        df['year'] = df['tdate'].dt.year
        df = df[df['year'] == year]
    
    total_missions = len(df)
    
    # Estimate annual operational cost (simplified)
    # Assume: 3 aircraft, 2 crews per aircraft, 3 bases
    fleet_size = df['veh'].nunique() if 'veh' in df.columns else 3
    estimated_annual_cost = fleet_size * 100000  # $100k per aircraft/year (simplified)
    
    # Add base costs
    base_count = 3  # Estimated
    estimated_annual_cost += base_count * 500000  # $500k per base/year
    
    unit_cost = estimated_annual_cost / total_missions if total_missions > 0 else 0.0
    
    return {
        'unit_cost_per_mission': float(unit_cost),
        'estimated_annual_cost': float(estimated_annual_cost),
        'total_missions': int(total_missions)
    }


def calculate_unmet_demand(df: pd.DataFrame, sla_target_minutes: int = 20) -> Dict[str, float]:
    """
    Estimate unmet demand based on SLA violations.
    
    Args:
        df: Operational data DataFrame
        sla_target_minutes: SLA target in minutes
    
    Returns:
        Dictionary with unmet demand metrics
    """
    response_times = calculate_response_times(df)
    valid_rt = response_times.dropna()
    
    if len(valid_rt) == 0:
        return {
            'unmet_demand_missions': 0.0,
            'unmet_demand_rate': 0.0,
            'sla_violations': 0,
            'total_missions': 0
        }
    
    sla_violations = (valid_rt > sla_target_minutes).sum()
    total = len(valid_rt)
    unmet_rate = (sla_violations / total * 100) if total > 0 else 0.0
    
    return {
        'unmet_demand_missions': float(sla_violations),
        'unmet_demand_rate': float(unmet_rate),
        'sla_violations': int(sla_violations),
        'total_missions': int(total)
    }


def get_historical_trends(df: pd.DataFrame, metric: str, years: List[int]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get historical trends for a metric.
    
    Args:
        df: Operational data DataFrame
        metric: Metric name ('missions', 'sla_attainment', etc.)
        years: List of years to calculate
    
    Returns:
        Dictionary with historical data points
    """
    df = df.copy()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['year'] = df['tdate'].dt.year
    
    historical_data = []
    
    for year in years:
        year_df = df[df['year'] == year]
        
        if metric == 'missions':
            value = len(year_df)
            historical_data.append({'year': year, 'value': value})
        
        elif metric == 'sla_attainment':
            sla_metrics = calculate_sla_attainment(year_df)
            historical_data.append({'year': year, 'value': sla_metrics['attainment_rate']})
        
        elif metric == 'unmet_demand':
            unmet = calculate_unmet_demand(year_df)
            historical_data.append({'year': year, 'value': unmet['unmet_demand_rate']})
        
        elif metric == 'transfer_success':
            success = calculate_transfer_success_rate(year_df)
            historical_data.append({'year': year, 'value': success['success_rate']})
        
        elif metric == 'flight_hours':
            hours = calculate_flight_hours(year_df)
            historical_data.append({'year': year, 'value': hours['total_flight_hours']})
        
        elif metric == 'unit_cost':
            cost = calculate_unit_cost(year_df, year)
            historical_data.append({'year': year, 'value': cost['unit_cost_per_mission']})
    
    return {
        'metric': metric,
        'data': historical_data
    }


def get_kpi_bullets(
    year: int = 2023,
    sla_target_minutes: int = 20,
    include_historical: bool = True
) -> Dict[str, Any]:
    """
    Main function to get all KPI bullets data.
    
    Args:
        year: Year to calculate KPIs for
        sla_target_minutes: SLA target in minutes
        include_historical: Whether to include historical trends
    
    Returns:
        Dictionary with all KPI bullet chart data
    """
    from utils.getData import read_data
    
    df = read_data()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['year'] = df['tdate'].dt.year
    
    # Filter by year
    year_df = df[df['year'] == year].copy()
    
    if len(year_df) == 0:
        # Use all data if year not found
        year_df = df
    
    # Calculate all KPIs
    missions_metrics = calculate_missions_per_population(year_df, year)
    sla_metrics = calculate_sla_attainment(year_df, sla_target_minutes)
    unmet_metrics = calculate_unmet_demand(year_df, sla_target_minutes)
    transfer_metrics = calculate_transfer_success_rate(year_df)
    flight_hours_metrics = calculate_flight_hours(year_df)
    cost_metrics = calculate_unit_cost(year_df, year)
    
    # Prepare bullet chart data
    bullets = []
    
    # 1. Missions
    bullets.append({
        'id': 'missions',
        'title': 'Total Missions',
        'current_value': missions_metrics['total_missions'],
        'target_value': missions_metrics['total_missions'] * 1.1,  # 10% growth target
        'qualitative_ranges': [
            {'from': 0, 'to': missions_metrics['total_missions'] * 0.8, 'color': 'red'},
            {'from': missions_metrics['total_missions'] * 0.8, 'to': missions_metrics['total_missions'] * 0.95, 'color': 'yellow'},
            {'from': missions_metrics['total_missions'] * 0.95, 'to': missions_metrics['total_missions'] * 1.1, 'color': 'green'}
        ],
        'subtitle': f"{missions_metrics['missions_per_1000']:.2f} per 1,000 population",
        'unit': 'missions'
    })
    
    # 2. SLA Attainment
    bullets.append({
        'id': 'sla_attainment',
        'title': 'SLA Attainment',
        'current_value': sla_metrics['attainment_rate'],
        'target_value': 90.0,  # 90% target
        'qualitative_ranges': [
            {'from': 0, 'to': 70, 'color': 'red'},
            {'from': 70, 'to': 85, 'color': 'yellow'},
            {'from': 85, 'to': 100, 'color': 'green'}
        ],
        'subtitle': f"Median: {sla_metrics['median_response_time']:.1f} min, P95: {sla_metrics['p95_response_time']:.1f} min",
        'unit': '%'
    })
    
    # 3. Unmet Demand
    bullets.append({
        'id': 'unmet_demand',
        'title': 'Unmet Demand Rate',
        'current_value': unmet_metrics['unmet_demand_rate'],
        'target_value': 5.0,  # Target: <5%
        'qualitative_ranges': [
            {'from': 0, 'to': 5, 'color': 'green'},
            {'from': 5, 'to': 10, 'color': 'yellow'},
            {'from': 10, 'to': 100, 'color': 'red'}
        ],
        'subtitle': f"{unmet_metrics['unmet_demand_missions']:.0f} missions exceeded SLA",
        'unit': '%'
    })
    
    # 4. Transfer Success Rate
    bullets.append({
        'id': 'transfer_success',
        'title': 'Transfer Success Rate',
        'current_value': transfer_metrics['success_rate'],
        'target_value': 95.0,  # 95% target
        'qualitative_ranges': [
            {'from': 0, 'to': 90, 'color': 'red'},
            {'from': 90, 'to': 95, 'color': 'yellow'},
            {'from': 95, 'to': 100, 'color': 'green'}
        ],
        'subtitle': f"{transfer_metrics['successful_transfers']:,} successful / {transfer_metrics['total_transfers']:,} total",
        'unit': '%'
    })
    
    # 5. Flight Hours
    bullets.append({
        'id': 'flight_hours',
        'title': 'Total Flight Hours',
        'current_value': flight_hours_metrics['total_flight_hours'],
        'target_value': flight_hours_metrics['total_flight_hours'] * 1.1,  # 10% growth
        'qualitative_ranges': [
            {'from': 0, 'to': flight_hours_metrics['total_flight_hours'] * 0.8, 'color': 'red'},
            {'from': flight_hours_metrics['total_flight_hours'] * 0.8, 'to': flight_hours_metrics['total_flight_hours'] * 0.95, 'color': 'yellow'},
            {'from': flight_hours_metrics['total_flight_hours'] * 0.95, 'to': flight_hours_metrics['total_flight_hours'] * 1.1, 'color': 'green'}
        ],
        'subtitle': f"Avg: {flight_hours_metrics['avg_flight_hours_per_mission']:.2f} hours per mission",
        'unit': 'hours'
    })
    
    # 6. Unit Cost
    # Use a large number instead of infinity for JSON compatibility
    max_cost = cost_metrics['unit_cost_per_mission'] * 2.0  # 2x current cost as upper bound
    qualitative_ranges = [
        {'from': cost_metrics['unit_cost_per_mission'] * 1.1, 'to': max_cost, 'color': 'red'},
        {'from': cost_metrics['unit_cost_per_mission'] * 0.9, 'to': cost_metrics['unit_cost_per_mission'] * 1.1, 'color': 'yellow'},
        {'from': 0, 'to': cost_metrics['unit_cost_per_mission'] * 0.9, 'color': 'green'}
    ]
    
    bullets.append({
        'id': 'unit_cost',
        'title': 'Unit Cost per Mission',
        'current_value': cost_metrics['unit_cost_per_mission'],
        'target_value': cost_metrics['unit_cost_per_mission'] * 0.9,  # 10% reduction target
        'qualitative_ranges': qualitative_ranges,
        'subtitle': f"Annual: ${cost_metrics['estimated_annual_cost']/1000000:.2f}M",
        'unit': '$'
    })
    
    # Get historical trends if requested
    historical_trends = {}
    if include_historical:
        available_years = sorted(df['year'].dropna().unique().astype(int).tolist())
        # Get last 5 years
        recent_years = available_years[-5:] if len(available_years) > 5 else available_years
        
        for metric in ['missions', 'sla_attainment', 'unmet_demand', 'transfer_success', 'flight_hours', 'unit_cost']:
            historical_trends[metric] = get_historical_trends(df, metric, recent_years)
    
    return {
        'year': year,
        'sla_target_minutes': sla_target_minutes,
        'bullets': bullets,
        'historical_trends': historical_trends,
        'metadata': {
            'calculation_date': datetime.now().isoformat(),
            'data_year_range': {
                'min': int(df['year'].min()) if 'year' in df.columns else year,
                'max': int(df['year'].max()) if 'year' in df.columns else year
            }
        }
    }

