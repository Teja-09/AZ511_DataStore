import requests
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv('AZ511_API_KEY')
BASE_URL = 'https://az511.com/api/v2'

# Fetch weather data from the API
def fetch_weather_data(endpoint):
    url = f"{BASE_URL}/get/{endpoint}"
    params = {'key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # Return weather data
    else:
        print(f"Error fetching weather data: {response.status_code}")
        return None

# Create a database connection
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

# Function to convert API data into the desired format
def convert_station_data(station):
    return {
        'Id': station['Id'],  # Assume Id is always present
        'CameraId': station.get('CameraId'),
        'Latitude': float(station['Latitude']) if station['Latitude'] else None,
        'Longitude': float(station['Longitude']) if station['Longitude'] else None,
        'AirTemperature': float(station['AirTemperature']) if station['AirTemperature'] else None,
        'SurfaceTemperature': float(station['SurfaceTemperature']) if station['SurfaceTemperature'] else None,
        'WindSpeed': float(station['WindSpeed']) if station['WindSpeed'] else None,
        'WindDirection': station.get('WindDirection'),
        'RelativeHumidity': int(station['RelativeHumidity']) if station['RelativeHumidity'] else None,
        'LevelOfGrip': station.get('LevelOfGrip'),
        'MaxWindSpeed': float(station['MaxWindSpeed']) if station['MaxWindSpeed'] else None,
        'last_updated': datetime.strptime(station['LastUpdated'], "%b %d %Y, %I:%M %p") if 'LastUpdated' in station else datetime.now()
    }

# Archive old weather data
def archive_weather_data(connection, original_id, existing_data):
    cursor = connection.cursor()

    # SQL for archiving data
    archive_sql = """
    INSERT INTO weather_stations_archive (original_id, camera_id, latitude, longitude,
        air_temperature, surface_temperature, wind_speed, wind_direction,
        relative_humidity, level_of_grip, max_wind_speed, last_updated)
    VALUES (%(original_id)s, %(camera_id)s, %(latitude)s, %(longitude)s,
            %(air_temperature)s, %(surface_temperature)s, %(wind_speed)s,
            %(wind_direction)s, %(relative_humidity)s, %(level_of_grip)s,
            %(max_wind_speed)s, %(last_updated)s);
    """
    
    try:
        weather_values = {
            'original_id': original_id,
            'camera_id': existing_data[1],  
            'latitude': existing_data[2],  
            'longitude': existing_data[3],  
            'air_temperature': existing_data[4],  
            'surface_temperature': existing_data[5],  
            'wind_speed': existing_data[6],  
            'wind_direction': existing_data[7],  
            'relative_humidity': existing_data[8],  
            'level_of_grip': existing_data[9],  
            'max_wind_speed': existing_data[10],  
            'last_updated': existing_data[11]  
        }
        cursor.execute(archive_sql, weather_values)
        connection.commit()
        print(f"Archived weather data for original ID {original_id}.")
    except Error as e:
        print(f"Error archiving weather data: {e}")
    finally:
        cursor.close()

# Update or insert new weather data
def update_weather_data(connection, weather_data):
    cursor = connection.cursor()

    # Prepare SQL query for selecting existing weather data
    select_existing_sql = """
    SELECT id, camera_id, latitude, longitude, air_temperature,
           surface_temperature, wind_speed, wind_direction,
           relative_humidity, level_of_grip, max_wind_speed, last_updated
    FROM weather_stations WHERE id = %(id)s;
    """
    
    insert_weather_sql = """
    INSERT INTO weather_stations (id, camera_id, latitude, longitude, air_temperature,
        surface_temperature, wind_speed, wind_direction, relative_humidity,
        level_of_grip, max_wind_speed, last_updated)
    VALUES (%(id)s, %(camera_id)s, %(latitude)s, %(longitude)s, %(air_temperature)s,
            %(surface_temperature)s, %(wind_speed)s, %(wind_direction)s,
            %(relative_humidity)s, %(level_of_grip)s, %(max_wind_speed)s,
            %(last_updated)s);
    """

    update_weather_sql = """
    UPDATE weather_stations 
    SET camera_id = %(camera_id)s,
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
    WHERE id = %(id)s;
    """

    try:
        for data in weather_data:
            # Convert the raw API data to the desired format
            station_values = convert_station_data(data)

            # Check if we have an existing record with the unique id
            cursor.execute(select_existing_sql, {'id': station_values['Id']})  # Use Id field
            existing_data = cursor.fetchone()

            # Archive the existing data unconditionally
            if existing_data:
                # Archive existing weather data
                archive_weather_data(connection, existing_data[0], existing_data)

            # Prepare the new data for inserting or updating
            weather_values = {
                'id': station_values['Id'],  # Ensure we use the Id from the fetched data
                'camera_id': station_values['CameraId'],
                'latitude': station_values['Latitude'],
                'longitude': station_values['Longitude'],
                'air_temperature': station_values['AirTemperature'],
                'surface_temperature': station_values['SurfaceTemperature'],
                'wind_speed': station_values['WindSpeed'],
                'wind_direction': station_values['WindDirection'],
                'relative_humidity': station_values['RelativeHumidity'],
                'level_of_grip': station_values['LevelOfGrip'],
                'max_wind_speed': station_values['MaxWindSpeed'],
                'last_updated': station_values['last_updated']  # Set last_updated to now
            }

            # Check if existing data found, then update it; otherwise insert new data
            if existing_data:
                cursor.execute(update_weather_sql, weather_values)
                print(f"Updated weather data for ID {existing_data[0]}.")
            else:
                cursor.execute(insert_weather_sql, weather_values)
                print(f"Inserted new weather data for Camera ID {station_values['CameraId']}.")

            connection.commit()  # Commit each operation
    except Error as e:
        print(f"Error updating weather data: {e}")
    finally:
        cursor.close()

# Run the process
def run_process():
    connection = create_db_connection()
    if connection:
        # Step 1: Fetch new weather data
        weather_data = fetch_weather_data('weatherstations')
        if weather_data:
            # Step 2: Update or insert weather data
            update_weather_data(connection, weather_data)

        connection.close()
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    run_process()
