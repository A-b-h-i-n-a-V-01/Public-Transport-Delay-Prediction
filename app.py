import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Load model
MODEL_PATH = 'delay_prediction_model.pkl'
CSV_PATH = 'public_transport_delays.csv'

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file {MODEL_PATH} not found.")

model = joblib.load(MODEL_PATH)
expected_features = model.feature_names_in_.tolist()

# Load CSV and prepare lookups
if os.path.exists(CSV_PATH):
    df_data = pd.read_csv(CSV_PATH)
    # Parse dates and times to compute duration
    df_data['scheduled_departure'] = pd.to_datetime(df_data['scheduled_departure'], format='%H:%M:%S', errors='coerce')
    df_data['scheduled_arrival'] = pd.to_datetime(df_data['scheduled_arrival'], format='%H:%M:%S', errors='coerce')
    df_data['duration'] = (df_data['scheduled_arrival'] - df_data['scheduled_departure']).dt.total_seconds() / 60
    # Correct negative durations
    df_data.loc[df_data['duration'] < 0, 'duration'] += 24 * 60
    
    # 1. Lookups
    # (origin, destination, transport_type) -> route_id
    route_lookup = df_data.groupby(['origin_station', 'destination_station', 'transport_type'])['route_id'].first().to_dict()
    # (origin, destination) -> mean duration
    duration_lookup = df_data.groupby(['origin_station', 'destination_station'])['duration'].mean().to_dict()
    
    # Unique lists for dropdowns
    unique_stations = sorted(list(df_data['origin_station'].dropna().unique()))
    unique_transports = sorted(list(df_data['transport_type'].dropna().unique()))
else:
    route_lookup = {}
    duration_lookup = {}
    unique_stations = [f"Station_{i}" for i in range(1, 51)]
    unique_transports = ['Bus', 'Metro', 'Train', 'Tram']

station_names_mapping = {
    "Station_1": "King's Cross St. Pancras",
    "Station_2": "Paddington Hub",
    "Station_3": "Waterloo International",
    "Station_4": "Euston Terminus",
    "Station_5": "Victoria Interchange",
    "Station_6": "Liverpool Street Station",
    "Station_7": "London Bridge Hub",
    "Station_8": "Charing Cross Station",
    "Station_9": "Marylebone Terminus",
    "Station_10": "Piccadilly Circus",
    "Station_11": "Covent Garden",
    "Station_12": "Westminster Central",
    "Station_13": "Oxford Circus",
    "Station_14": "Leicester Square",
    "Station_15": "Baker Street Hub",
    "Station_16": "Bond Street",
    "Station_17": "Green Park",
    "Station_18": "South Kensington",
    "Station_19": "Knightsbridge",
    "Station_20": "Canary Wharf Terminal",
    "Station_21": "Stratford International",
    "Station_22": "Tottenham Court Road",
    "Station_23": "Holborn Station",
    "Station_24": "Blackfriars Hub",
    "Station_25": "Farringdon Terminus",
    "Station_26": "Elephant & Castle",
    "Station_27": "Hammersmith Interchange",
    "Station_28": "White City Hub",
    "Station_29": "Wembley Park",
    "Station_30": "Greenwich North",
    "Station_31": "Richmond Station",
    "Station_32": "Wimbledon Terminal",
    "Station_33": "Camden Town",
    "Station_34": "Hampstead Central",
    "Station_35": "Brixton Terminus",
    "Station_36": "Chelsea Harbour",
    "Station_37": "Battersea Power Station",
    "Station_38": "Vauxhall Station",
    "Station_39": "Clapham Junction",
    "Station_40": "Earl's Court",
    "Station_41": "Kensington Palace",
    "Station_42": "Notting Hill Gate",
    "Station_43": "Shepherd's Bush",
    "Station_44": "Paddington Basin",
    "Station_45": "Regent's Park",
    "Station_46": "St. James's Park",
    "Station_47": "Temple Station",
    "Station_48": "Mansion House",
    "Station_49": "Tower Hill",
    "Station_50": "Aldgate East"
}

def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    stations_data = []
    for station_id in unique_stations:
        stations_data.append({
            'id': station_id,
            'name': station_names_mapping.get(station_id, station_id.replace('_', ' '))
        })
    return jsonify({
        'stations': stations_data,
        'transport_types': unique_transports
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json or {}
        
        origin = data.get('origin', 'Station_31')
        destination = data.get('destination', 'Station_6')
        departure_time_str = data.get('departure_time', '05:00') # HH:MM format
        transport_type = data.get('transport_type', 'Tram')
        
        # Get current date/time parameters
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        day_of_week = now.weekday() # 0-6 (Mon-Sun)
        weekday_num = day_of_week
        
        # Parse departure hour and minute
        try:
            dep_time = datetime.strptime(departure_time_str, "%H:%M")
            departure_hour = dep_time.hour
            departure_minute = dep_time.minute
        except ValueError:
            departure_hour = 5
            departure_minute = 0
            
        # Peak Hour rule: standard morning (7-9) and evening (16-19) peak hours
        peak_hour = 1 if (7 <= departure_hour <= 9 or 16 <= departure_hour <= 19) else 0
        
        # Holiday rule (simulate as 0, or 1 if it's weekend/custom)
        holiday = 1 if day_of_week in [5, 6] else 0
        
        # Estimate trip duration using historical lookup
        duration = duration_lookup.get((origin, destination), 30.0)
        
        # Compute arrival hour and minute
        arrival_minutes = departure_hour * 60 + departure_minute + int(duration)
        arrival_hour = (arrival_minutes // 60) % 24
        arrival_minute = arrival_minutes % 60
        
        # Find matching route_id
        route_id = route_lookup.get((origin, destination, transport_type))
        if not route_id:
            # Try origin-destination fallback
            routes_subset = [r for (o, d, t), r in route_lookup.items() if o == origin and d == destination]
            route_id = routes_subset[0] if routes_subset else 'Route_15'
            
        # Get simulated contextual features as requested
        # User entered or default:
        temperature_C = float(data.get('temperature_C', 30.0))
        humidity_percent = float(data.get('humidity_percent', 82.0))
        wind_speed_kmh = float(data.get('wind_speed_kmh', 15.0))
        precipitation_mm = float(data.get('precipitation_mm', 2.0))
        traffic_congestion_index = float(data.get('traffic_congestion_index', 65.0))
        event_attendance_est = float(data.get('event_attendance_est', 0.0))
        
        weather_condition = data.get('weather_condition', 'Rain')
        event_type = data.get('event_type', 'Unknown')
        season = get_season(month)
        
        # Construct prediction DataFrame matching model expected columns
        input_row = pd.DataFrame(0.0, index=[0], columns=expected_features)
        
        # Continuous numerical variables
        input_row['temperature_C'] = temperature_C
        input_row['humidity_percent'] = humidity_percent
        input_row['wind_speed_kmh'] = wind_speed_kmh
        input_row['precipitation_mm'] = precipitation_mm
        input_row['event_attendance_est'] = event_attendance_est
        input_row['traffic_congestion_index'] = traffic_congestion_index
        input_row['scheduled_trip_duration_min'] = duration
        
        # Date & Time features
        input_row['holiday'] = float(holiday)
        input_row['peak_hour'] = float(peak_hour)
        input_row['weekday'] = float(weekday_num)
        input_row['day_of_week'] = float(day_of_week)
        input_row['month'] = float(month)
        input_row['year'] = float(year)
        input_row['departure_hour'] = float(departure_hour)
        input_row['departure_minute'] = float(departure_minute)
        input_row['arrival_hour'] = float(arrival_hour)
        input_row['arrival_minute'] = float(arrival_minute)
        
        # Categorical dummies
        # 1. Transport Type
        transport_col = f'transport_type_{transport_type}'
        if transport_col in expected_features:
            input_row[transport_col] = 1.0
            
        # 2. Route ID
        route_col = f'route_id_{route_id}'
        if route_col in expected_features:
            input_row[route_col] = 1.0
            
        # 3. Origin Station
        origin_col = f'origin_station_{origin}'
        if origin_col in expected_features:
            input_row[origin_col] = 1.0
            
        # 4. Destination Station
        dest_col = f'destination_station_{destination}'
        if dest_col in expected_features:
            input_row[dest_col] = 1.0
            
        # 5. Weather Condition
        weather_col = f'weather_condition_{weather_condition}'
        if weather_col in expected_features:
            input_row[weather_col] = 1.0
            
        # 6. Event Type
        event_col = f'event_type_{event_type}'
        if event_col in expected_features:
            input_row[event_col] = 1.0
            
        # 7. Season
        season_col = f'season_{season}'
        if season_col in expected_features:
            input_row[season_col] = 1.0
            
        # Perform prediction
        pred = int(model.predict(input_row)[0])
        prob = model.predict_proba(input_row)[0].tolist()
        
        return jsonify({
            'success': True,
            'prediction': pred,
            'probability_ontime': prob[0],
            'probability_delayed': prob[1],
            'context': {
                'temperature_C': temperature_C,
                'humidity_percent': humidity_percent,
                'wind_speed_kmh': wind_speed_kmh,
                'precipitation_mm': precipitation_mm,
                'traffic_congestion_index': traffic_congestion_index,
                'event_attendance_est': event_attendance_est,
                'weather_condition': weather_condition,
                'event_type': event_type,
                'season': season,
                'route_id': route_id,
                'estimated_duration_min': round(duration, 1),
                'peak_hour': peak_hour,
                'holiday': holiday
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
