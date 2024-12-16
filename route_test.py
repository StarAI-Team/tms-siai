from flask import Flask, request, jsonify, render_template
import joblib
import logging
from database import fetch_from_db

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Load model and LabelEncoder
try:
    model, le = joblib.load("traffic_model.pkl")
except FileNotFoundError:
    print("Model file not found. Please train the model first.")
    model, le = None, None

@app.route('/')
def home_page():
    return render_template('route_planning.html')

@app.route('/predict_traffic', methods=['POST'])
def predict_traffic():
    if model is None or le is None:
        return jsonify({"error": "Model not loaded. Please train the model first."}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract and validate input
        road_name = data.get('road_name')
        hour = data.get('hour')
        day_of_week = data.get('day_of_week')

        if not road_name or hour is None or day_of_week is None:
            return jsonify({"error": "Invalid input. 'road_name', 'hour', and 'day_of_week' are required."}), 400

        # Encode road name, handling unseen labels
        try:
            encoded_road_name = le.transform([road_name])[0]
        except ValueError:
            app.logger.warning(f"Road name '{road_name}' not seen during training. Using 'Unnamed Road'.")
            encoded_road_name = le.transform(['Unnamed Road'])[0]

        # Prepare features and predict
        features = [[encoded_road_name, hour, day_of_week]]
        predicted_speed = model.predict(features)[0]

        return jsonify({'predicted_speed': predicted_speed})

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({"error": f"Prediction error: {e}"}), 500


@app.route('/fetch_traffic', methods=['GET'])
def fetch_traffic():
    records = fetch_from_db()
    return jsonify(records)

if __name__ == "__main__":
    app.run(debug=True, port=5003)
