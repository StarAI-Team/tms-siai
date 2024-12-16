import openrouteservice
import psycopg2
from datetime import datetime

# ORS API configuration
ORS_API_KEY = "5b3ce3597851110001cf6248a37cf3ac181c44dd896df121fc6d23c4"
client = openrouteservice.Client(key=ORS_API_KEY)

# PostgreSQL configuration
DB_CONFIG = {
    'dbname': 'starinternational',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


# Function to save data to PostgreSQL
def save_to_db(data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        for road_name, lat, lng, speed in data:
            cursor.execute(
                """
                INSERT INTO traffic_data (road_name, latitude, longitude, traffic_speed)
                VALUES (%s, %s, %s, %s)
                """,
                (road_name, lat, lng, speed)
            )
        conn.commit()
        print("Data saved successfully.")
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

def fetch_from_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM traffic_data")
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
