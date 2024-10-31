import requests
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv('AZ511_API_KEY')
BASE_URL = 'https://az511.com/api/v2'

def fetch_data(endpoint):
    url = f"{BASE_URL}/get/{endpoint}"
    params = {'key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {endpoint}: {response.status_code}")
        return None

def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def insert_weather_station_data(connection, weather_stations):
    cursor = connection.cursor()
    
    # First, let's get all existing camera IDs
    cursor.execute("SELECT id FROM cameras")
    existing_camera_ids = set(row[0] for row in cursor.fetchall())
    
    select_sql = "SELECT id FROM weather_stations WHERE id = %(id)s"
    
    update_sql = """
    UPDATE weather_stations 
    SET 
        camera_id = %(camera_id)s,
        latitude = %(latitude)s,
        longitude = %(longitude)s,
        air_temperature = %(air_temperature)s,
        surface_temperature = %(surface_temperature)s,
        wind_speed = %(wind_speed)s,
        wind_direction = %(wind_direction)s,
        relative_humidity = %(relative_humidity)s,
        level_of_grip = %(level_of_grip)s,
        max_wind_speed = %(max_wind_speed)s,
        last_updated = %(last_updated)s
    WHERE 
        id = %(id)s
        AND (
            camera_id != %(camera_id)s OR
            latitude != %(latitude)s OR
            longitude != %(longitude)s OR
            air_temperature != %(air_temperature)s OR
            surface_temperature != %(surface_temperature)s OR
            wind_speed != %(wind_speed)s OR
            wind_direction != %(wind_direction)s OR
            relative_humidity != %(relative_humidity)s OR
            level_of_grip != %(level_of_grip)s OR
            max_wind_speed != %(max_wind_speed)s OR
            last_updated != %(last_updated)s
        )
    """
    
    insert_sql = """
    INSERT INTO weather_stations (
        id, camera_id, latitude, longitude, air_temperature, surface_temperature,
        wind_speed, wind_direction, relative_humidity, level_of_grip, max_wind_speed, last_updated
    ) VALUES (
        %(id)s, %(camera_id)s, %(latitude)s, %(longitude)s, %(air_temperature)s, %(surface_temperature)s,
        %(wind_speed)s, %(wind_direction)s, %(relative_humidity)s, %(level_of_grip)s, %(max_wind_speed)s, %(last_updated)s
    )
    """
    
    try:
        for station in weather_stations:
            # Convert CameraId to int and check if it exists in cameras table
            try:
                camera_id = int(station['CameraId'])
                if camera_id not in existing_camera_ids:
                    print(f"Warning: Camera ID {camera_id} does not exist in cameras table. Skipping this weather station.")
                    continue
            except ValueError:
                print(f"Warning: Invalid Camera ID {station['CameraId']}. Skipping this weather station.")
                continue

            station_values = {
                'id': station['Id'],
                'camera_id': camera_id,
                'latitude': station['Latitude'],
                'longitude': station['Longitude'],
                'air_temperature': float(station['AirTemperature']) if station['AirTemperature'] else None,
                'surface_temperature': float(station['SurfaceTemperature']) if station['SurfaceTemperature'] else None,
                'wind_speed': float(station['WindSpeed']) if station['WindSpeed'] else None,
                'wind_direction': station['WindDirection'],
                'relative_humidity': int(station['RelativeHumidity']) if station['RelativeHumidity'] else None,
                'level_of_grip': station['LevelOfGrip'],
                'max_wind_speed': float(station['MaxWindSpeed']) if station['MaxWindSpeed'] else None,
                'last_updated': datetime.strptime(station['LastUpdated'], "%b %d %Y, %I:%M %p")
            }
            
            cursor.execute(select_sql, {'id': station['Id']})
            if cursor.fetchone():
                cursor.execute(update_sql, station_values)
            else:
                cursor.execute(insert_sql, station_values)
        
        connection.commit()
        print(f"Processed {len(weather_stations)} weather stations.")
    except Error as e:
        print(f"Error processing weather station data: {e}")
    finally:
        cursor.close()

def main():
    weather_stations = fetch_data('weatherstations')
    if weather_stations:
        connection = create_db_connection()
        if connection:
            insert_weather_station_data(connection, weather_stations)
            connection.close()
        else:
            print("Failed to connect to the database")
    else:
        print("No weather station data retrieved")

if __name__ == "__main__":
    main()