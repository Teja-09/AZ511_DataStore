import requests
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv('AZ511_API_KEY')
BASE_URL = 'https://az511.com/api/v2'

def fetch_cameras():
    url = f"{BASE_URL}/get/cameras"
    params = {'key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json() # Limit to first 10 responses
    else:
        print(f"Error fetching cameras: {response.status_code}")
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

def insert_camera_data(connection, cameras):
    cursor = connection.cursor()
    
    # SQL queries
    camera_select_sql = "SELECT id FROM cameras WHERE id = %(id)s"
    
    camera_update_sql = """
    UPDATE cameras 
    SET 
        source = %(source)s,
        roadway = %(roadway)s,
        direction = %(direction)s,
        latitude = %(latitude)s,
        longitude = %(longitude)s,
        location = %(location)s
    WHERE 
        id = %(id)s
        AND (
            source != %(source)s OR
            roadway != %(roadway)s OR
            direction != %(direction)s OR
            latitude != %(latitude)s OR
            longitude != %(longitude)s OR
            location != %(location)s
        )
    """
    
    camera_insert_sql = """
    INSERT INTO cameras (id, source, roadway, direction, latitude, longitude, location)
    VALUES (%(id)s, %(source)s, %(roadway)s, %(direction)s, %(latitude)s, %(longitude)s, %(location)s)
    """
    
    view_select_sql = "SELECT id FROM camera_views WHERE id = %(id)s AND camera_id = %(camera_id)s"
    
    view_update_sql = """
    UPDATE camera_views 
    SET 
        url = %(url)s,
        status = %(status)s,
        description = %(description)s
    WHERE 
        id = %(id)s
        AND camera_id = %(camera_id)s
        AND (
            url != %(url)s OR
            status != %(status)s OR
            description != %(description)s
        )
    """
    
    view_insert_sql = """
    INSERT INTO camera_views (id, camera_id, url, status, description)
    VALUES (%(id)s, %(camera_id)s, %(url)s, %(status)s, %(description)s)
    """
    
    try:
        for camera in cameras:
            camera_values = {
                'id': camera['Id'],
                'source': camera['Source'],
                'roadway': camera['Roadway'],
                'direction': camera['Direction'],
                'latitude': camera['Latitude'],
                'longitude': camera['Longitude'],
                'location': camera['Location']
            }
            
            # Check if the camera exists
            cursor.execute(camera_select_sql, {'id': camera['Id']})
            if cursor.fetchone():
                # Camera exists; try to update it
                cursor.execute(camera_update_sql, camera_values)
            else:
                # Camera doesn't exist; insert a new one
                cursor.execute(camera_insert_sql, camera_values)
            
            for view in camera['Views']:
                view_values = {
                    'id': view['Id'],
                    'camera_id': camera['Id'],
                    'url': view['Url'],
                    'status': view['Status'],
                    'description': view['Description']
                }
                
                # Check if the view exists
                cursor.execute(view_select_sql, {'id': view['Id'], 'camera_id': camera['Id']})
                if cursor.fetchone():
                    # View exists; try to update it
                    cursor.execute(view_update_sql, view_values)
                else:
                    # View doesn't exist; insert a new one
                    cursor.execute(view_insert_sql, view_values)
        
        connection.commit()
        print(f"Processed {len(cameras)} cameras and their views.")
    except Error as e:
        print(f"Error processing camera data: {e}")
    finally:
        cursor.close()

def main():
    cameras = fetch_cameras()
    # print(cameras)
    if cameras:
        connection = create_db_connection()
        if connection:
            insert_camera_data(connection, cameras)
            connection.close()
        else:
            print("Failed to connect to the database")
    else:
        print("No camera data retrieved")

if __name__ == "__main__":
    main()