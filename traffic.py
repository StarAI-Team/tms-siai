import openrouteservice
from datetime import datetime

# ORS API configuration
ORS_API_KEY = "5b3ce3597851110001cf6248b8cfbe4289d44b6d97f0bd42cfa75622"
client = openrouteservice.Client(key=ORS_API_KEY)

def fetch_traffic_data(origin_coords, destination_coords):
    try:
        route = client.directions(
            coordinates=[origin_coords, destination_coords],
            profile='driving-hgv',
            format='geojson',
        )
        if not route.get('features'):
            print("No features found in the API response.")
            return []

        traffic_data = []
        for feature in route['features']:
            road_name = str(feature['properties'].get('summary', 'Unnamed Road'))
            segments = feature['properties'].get('segments', [])
            for segment in segments:
                duration = segment.get('duration', 0)
                distance = segment.get('distance', 1)
                if distance > 0:
                    distance_km = distance / 1000  # Convert meters to kilometers
                    duration_hours = duration / 3600  # Convert seconds to hours
                    traffic_speed = distance_km / duration_hours if duration_hours > 0 else 0
                else:
                    traffic_speed = 0
                
                for coord in feature['geometry']['coordinates']:
                    lat, lng = coord[1], coord[0]
                    traffic_data.append((road_name, float(lat), float(lng), float(traffic_speed)))
        
        return traffic_data
    except Exception as e:
        print(f"Error fetching traffic data: {e}")
        return []
