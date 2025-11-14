from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pandas as pd
from config import config
from utils.heatmap import generate_city_demand_heatmap, map_to_html
from utils.getData import read_data
from utils.responseTime import calculate_response_time
from utils.veh_count import calculate_veh_count
from utils.predicting.predict_demand import predict_demand as forecast_demand

app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS for cross-origin requests from frontend
CORS(app)

@app.route('/api/veh_count', methods=['GET'])
def get_veh_count():
    """Get veh count data"""
    df = read_data()
    veh_count = calculate_veh_count(df,2023)
    
    # Map vehicle codes to names
    veh_name_map = {
        'LF1': 'Helicopter based out of Bangor',
        'LF2': 'Helicopter based out of Lewiston',
        'LF3': 'Airplane based out of Bangor',
        'LF4': 'Helicopter based out of Sanford'
    }
    
    # Transform data to include vehicle names
    for item in veh_count:
        veh_code = item['id']
        if veh_code in veh_name_map:
            item['id'] = f"{veh_name_map[veh_code]} ({veh_code})"
    
    return jsonify({
        'status': 'success',
        'message': 'Veh count data fetched successfully',
        'data': veh_count
    })

@app.route('/api/heatmap',methods=['GET'])
def get_heatmap():
    """Get heatmap visualization"""
    df = read_data()
    map_obj = generate_city_demand_heatmap(df)
    html_map = map_to_html(map_obj)

    return html_map

@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    """Get indicator data"""
    df = read_data()
    # 1 total missions
    total_missions = df['yearwithrc'].nunique()
    total_missions_formatted = f"{total_missions:,}" 
    # 2 Total Cities Covered
    total_cities_covered = df['PU City'].nunique()
    # 3 Monthly Average Response Time
    mart_str = calculate_response_time(df,2023,12)
    # 4 Yearly Average Response Time
    yart_str = calculate_response_time(df,2023)
    
    # Convert timedelta string to "X min Y sec" format
    def extract_minutes_seconds(timedelta_str):
        if timedelta_str == "N/A":
            return "N/A"
        try:
            # Parse timedelta string like "0 days 00:22:09.824561403"
            td = pd.Timedelta(timedelta_str)
            total_seconds = int(td.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes} min {seconds} sec"
        except:
            return "N/A"
    
    mart = extract_minutes_seconds(mart_str)
    yart = extract_minutes_seconds(yart_str)
    
    return jsonify({
        'status': 'success',
        'message': 'Indicator data fetched successfully',
        'data': {
            'total_missions': total_missions_formatted,
            'total_cities_covered': total_cities_covered,
            'mart': mart,
            'yart': yart
        }
    })

@app.route('/api/hourly_departure', methods=['GET'])
def get_hourly_departure():
    """Get hourly departure density data"""
    
    df = read_data()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['Year'] = df['tdate'].dt.year
    df = df[df['Year'] == 2023]

    df['enrtime_dt'] = pd.to_datetime(df['enrtime'], errors='coerce').dt.time
    df.dropna(subset=['enrtime_dt'], inplace=True)
    df['enr_hour'] = pd.to_datetime(df['enrtime_dt'].astype(str)).dt.hour
    
    def get_season(month):
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Autumn'
        else:
            return 'Winter'
    
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['season'] = df['tdate'].dt.month.apply(get_season)
    
    all_hours = list(range(24))
    
    overall_counts = df['enr_hour'].value_counts().sort_index()
    overall_density = overall_counts / overall_counts.sum()
    
    overall_data = []
    for hour in all_hours:
        count = int(overall_counts.get(hour, 0))
        density = float(overall_density.get(hour, 0))
        overall_data.append({
            'hour': hour,
            'count': count,
            'density': density
        })
    
    
    season_data = {}
    for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
        season_df = df[df['season'] == season]
        season_counts = season_df['enr_hour'].value_counts().sort_index()
        season_density = season_counts / season_counts.sum()
        
        season_hourly = []
        for hour in all_hours:
            count = int(season_counts.get(hour, 0))
            density = float(season_density.get(hour, 0))
            season_hourly.append({
                'hour': hour,
                'count': count,
                'density': density
            })
        season_data[season] = season_hourly
    
    return jsonify({
        'status': 'success',
        'data': {
            'overall': overall_data,
            'by_season': season_data
        }
    })



@app.route('/api/predict_demand', methods=['POST'])
def predict_demand():
    try:
        data = request.get_json()
        
        if data is None:
            model_name = request.args.get('model_name', 'prophet')
            years = int(request.args.get('years', 3))
        else:
            model_name = data.get('model_name', 'prophet')
            years = int(data.get('years', 3))
        
        if model_name not in ['prophet', 'arima']:
            return jsonify({
                'status': 'error',
                'message': f"Unsupported model type: {model_name}. Please use 'prophet' or 'arima'"
            }), 400
        
        if years < 1 or years > 10:
            return jsonify({
                'status': 'error',
                'message': 'Years must be between 1 and 10'
            }), 400
        
        result = forecast_demand(model_name, years)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except FileNotFoundError as e:
        return jsonify({
            'status': 'error',
            'message': f'Model file not found: {str(e)}'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Backend is working correctly',
        'data': {
            'timestamp': '2024-01-01T00:00:00Z',
            'test': True
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

