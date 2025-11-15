# backend/utils/seasonality.py
"""
Seasonality & Day-of-Week/Hour Heatmap utility functions.

This module provides functions to calculate seasonal patterns in demand,
aggregating by month × weekday × hour for heatmap visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from pathlib import Path
import os


def get_population_data(year: int, location_level: str = 'system', location_value: Optional[str] = None) -> int:
    """
    Get population data for the given year and location.
    
    Args:
        year: Year to get population for
        location_level: 'system', 'state', 'county', or 'city'
        location_value: Specific location value (e.g., county name, city name)
    
    Returns:
        Population count for the specified location and year
    """
    backend_dir = Path(__file__).parent.parent
    
    if location_level == 'system' or location_level == 'state':
        # Use state-level population
        pop_path = backend_dir / 'data' / 'processed' / 'population_parsed.csv'
        if pop_path.exists():
            pop_df = pd.read_csv(pop_path)
            pop_data = pop_df[pop_df['year'] == year]
            if len(pop_data) > 0:
                return int(pop_data['population'].iloc[0])
        # Fallback: use latest available year or estimate
        return 1329192  # Default Maine population (2012)
    
    elif location_level == 'county':
        # Use county-level population
        county_pop_path = backend_dir / 'data' / 'processed' / 'county_population_2020_2024.csv'
        if county_pop_path.exists() and location_value:
            county_pop_df = pd.read_csv(county_pop_path)
            county_pop_df['county'] = county_pop_df['county'].str.upper()
            filtered = county_pop_df[
                (county_pop_df['county'] == location_value.upper()) & 
                (county_pop_df['year'] == year)
            ]
            if len(filtered) > 0:
                return int(filtered['population'].iloc[0])
            # If year not in range, use closest year
            available_years = county_pop_df['year'].unique()
            if len(available_years) > 0:
                closest_year = min(available_years, key=lambda x: abs(x - year))
                filtered = county_pop_df[
                    (county_pop_df['county'] == location_value.upper()) & 
                    (county_pop_df['year'] == closest_year)
                ]
                if len(filtered) > 0:
                    return int(filtered['population'].iloc[0])
        # Fallback: estimate from state population / 16 counties
        pop_path = backend_dir / 'data' / 'processed' / 'population_parsed.csv'
        if pop_path.exists():
            pop_df = pd.read_csv(pop_path)
            pop_data = pop_df[pop_df['year'] == year]
            if len(pop_data) > 0:
                return int(pop_data['population'].iloc[0] / 16)  # Rough estimate
        return 80000  # Default county population estimate
    
    elif location_level == 'city':
        # For cities, use county population as proxy (or state/n_cities)
        # This is a simplification - ideally we'd have city-level population
        pop_path = backend_dir / 'data' / 'processed' / 'population_parsed.csv'
        if pop_path.exists():
            pop_df = pd.read_csv(pop_path)
            pop_data = pop_df[pop_df['year'] == year]
            if len(pop_data) > 0:
                # Rough estimate: state population / number of cities (use 348 from mapping)
                return int(pop_data['population'].iloc[0] / 348)
        return 4000  # Default city population estimate
    
    return 1329192  # Default fallback


def calculate_seasonality_heatmap(
    df: pd.DataFrame,
    year: int,
    location_level: str = 'system',
    location_value: Optional[str] = None,
    month: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate seasonality heatmap data (Hour × Weekday, optionally filtered by month).
    
    This is for Chart 1.2: Seasonality & Day-of-Week/Hour Heatmap
    - Aggregates deployments to (month × weekday × hour)
    - Heatmap intensity = average missions per 1,000 population
    
    Args:
        df: DataFrame containing operational data
        year: Year to filter by
        location_level: 'system', 'state', 'county', or 'city'
        location_value: Specific location value (e.g., 'Washington' for county, 'MACHIAS' for city)
        month: Optional month (1-12) to filter. If None, returns data for all months
    
    Returns:
        Dictionary containing:
        - heatmap_data: List of dictionaries with hour, weekday, count, missions_per_1000
        - metadata: Year, location info, population, etc.
    """
    # Filter by year
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['Year'] = df['tdate'].dt.year
    df_filtered = df[df['Year'] == year].copy()
    
    # Filter by location if specified
    if location_level == 'county' and location_value:
        df_filtered = df_filtered[df_filtered['PU City.1'].str.upper() == location_value.upper()]
    elif location_level == 'city' and location_value:
        df_filtered = df_filtered[df_filtered['PU City'].str.upper() == location_value.upper()]
    elif location_level == 'state' and location_value:
        df_filtered = df_filtered[df_filtered['PU State'].str.upper() == location_value.upper()]
    # For 'system', no filtering needed
    
    # Extract time features
    df_filtered['month'] = df_filtered['tdate'].dt.month
    df_filtered['weekday'] = df_filtered['tdate'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_filtered['weekday_name'] = df_filtered['tdate'].dt.day_name()
    
    # Extract hour from enrtime
    df_filtered['enrtime_dt'] = pd.to_datetime(df_filtered['enrtime'], errors='coerce')
    df_filtered['hour'] = df_filtered['enrtime_dt'].dt.hour
    
    # Filter out rows with missing time data
    df_filtered = df_filtered.dropna(subset=['month', 'weekday', 'hour'])
    
    # Filter by month if specified
    if month is not None:
        df_filtered = df_filtered[df_filtered['month'] == month]
    
    # Get population for normalization
    population = get_population_data(year, location_level, location_value)
    
    # Aggregate by (month, weekday, hour) or (weekday, hour) if month specified
    if month is not None:
        group_cols = ['weekday', 'hour']
    else:
        group_cols = ['month', 'weekday', 'hour']
    
    aggregated = df_filtered.groupby(group_cols).size().reset_index(name='count')
    
    # Calculate missions per 1,000 population
    # For each (month, weekday, hour) combination, calculate per 1000
    aggregated['missions_per_1000'] = (aggregated['count'] / population) * 1000
    
    # Prepare heatmap data
    heatmap_data = []
    for _, row in aggregated.iterrows():
        data_point = {
            'hour': int(row['hour']),
            'weekday': int(row['weekday']),
            'weekday_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][int(row['weekday'])],
            'count': int(row['count']),
            'missions_per_1000': float(row['missions_per_1000'])
        }
        if month is None:
            data_point['month'] = int(row['month'])
        heatmap_data.append(data_point)
    
    # Calculate metadata
    total_missions = df_filtered.shape[0]
    avg_missions_per_day = total_missions / 365.25 if total_missions > 0 else 0
    
    metadata = {
        'year': year,
        'location_level': location_level,
        'location_value': location_value,
        'month': month,
        'population': population,
        'total_missions': int(total_missions),
        'avg_missions_per_day': round(avg_missions_per_day, 2),
        'date_range': {
            'start': df_filtered['tdate'].min().strftime('%Y-%m-%d') if len(df_filtered) > 0 else None,
            'end': df_filtered['tdate'].max().strftime('%Y-%m-%d') if len(df_filtered) > 0 else None
        }
    }
    
    return {
        'heatmap_data': heatmap_data,
        'metadata': metadata
    }


def get_seasonality_heatmap(
    year: int,
    location_level: str = 'system',
    location_value: Optional[str] = None,
    month: Optional[int] = None
) -> Dict[str, Any]:
    """
    Main function to get seasonality heatmap data.
    
    Args:
        year: Year to analyze
        location_level: 'system', 'state', 'county', or 'city'
        location_value: Specific location value
        month: Optional month (1-12) to filter
    
    Returns:
        Dictionary with heatmap data and metadata
    """
    from utils.getData import read_data
    
    df = read_data()
    return calculate_seasonality_heatmap(df, year, location_level, location_value, month)

