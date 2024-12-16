import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib
import psycopg2
import requests
import pickle
from sqlalchemy import create_engine

# PostgreSQL configuration
DB_CONFIG = {
    'dbname': 'starinternational',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}


# Load cache from file
def load_cache_from_file(filename="road_name_cache.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}

# Save cache to file
def save_cache_to_file(cache, filename="road_name_cache.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(cache, file)

# Reverse geocode function using OpenRouteService
road_name_cache = load_cache_from_file()

def reverse_geocode_ors(lat, lon, api_key):
    key = (lat, lon)
    if key in road_name_cache:
        return road_name_cache[key]

    url = "https://api.openrouteservice.org/geocode/reverse"
    params = {
        "api_key": api_key,
        "point.lon": lon,
        "point.lat": lat,
        "layers": "street",
        "size": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        features = data.get("features", [])
        road_name = features[0]["properties"].get("name", "Unnamed Road") if features else "Unnamed Road"
        road_name_cache[key] = road_name  # Cache the result
        return road_name
    return "Unnamed Road"



# Function to fetch data from PostgreSQL
def fetch_data_from_db():
    try:
        # Create the SQLAlchemy engine
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        )
        query = "SELECT latitude, longitude, traffic_speed, timestamp FROM traffic_data"
        df = pd.read_sql_query(query, engine)  # Use SQLAlchemy engine here
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return None



def feature_engineering(traffic_df, api_key):
    # Drop rows with missing coordinates
    traffic_df = traffic_df.dropna(subset=["latitude", "longitude"])
    
    # Reverse geocode coordinates to get road names
    traffic_df["road_name"] = traffic_df.apply(
        lambda row: reverse_geocode_ors(row["latitude"], row["longitude"], api_key), axis=1
    )
    
    # Ensure 'Unnamed Road' is included for missing or unrecognized road names
    traffic_df["road_name"].fillna("Unnamed Road", inplace=True)
    
    # Add time-based features
    traffic_df["timestamp"] = pd.to_datetime(traffic_df["timestamp"])
    traffic_df["hour"] = traffic_df["timestamp"].dt.hour
    traffic_df["day_of_week"] = traffic_df["timestamp"].dt.dayofweek
    
    # Fill missing traffic speed with the mean
    traffic_df["traffic_speed"].fillna(traffic_df["traffic_speed"].mean(), inplace=True)
    
    # Ensure 'Unnamed Road' is part of the label encoding
    unique_road_names = traffic_df["road_name"].unique().tolist()
    if "Unnamed Road" not in unique_road_names:
        unique_road_names.append("Unnamed Road")

    # Fit the LabelEncoder with all unique road names
    le = LabelEncoder()
    le.fit(unique_road_names)
    traffic_df["encoded_road_name"] = le.transform(traffic_df["road_name"])

    return traffic_df, le



# Train and save model
def train_and_save_model(traffic_df, api_key, model_path="traffic_model.pkl"):
    # Use feature engineering to add road names and prepare the dataset
    traffic_df, le = feature_engineering(traffic_df, api_key)

    # Define features and target variable
    X = traffic_df[["encoded_road_name", "hour", "day_of_week"]]
    y = traffic_df["traffic_speed"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error: {mae}")

    # Save both the model and the LabelEncoder
    joblib.dump((model, le), model_path)
    print("Model and LabelEncoder saved successfully.")
    return model


# Main function
if __name__ == "__main__":
    api_key = "5b3ce3597851110001cf6248a37cf3ac181c44dd896df121fc6d23c4"  
    traffic_df = fetch_data_from_db()
    if traffic_df is not None and not traffic_df.empty:
        train_and_save_model(traffic_df, api_key)
    else:
        print("No data available to train the model.")
