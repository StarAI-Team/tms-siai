from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random 24-byte string
CORS(app)
PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'

# Store hashed passwords
users = {
    "user1": generate_password_hash("password1"),
    "user2": generate_password_hash("password2")
}

def get_ip_address():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Get JSON payload
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')  # Capture role from JSON

    try:
        # Hash the password before sending it to Redpanda service
        hashed_password = generate_password_hash(password)

        # Create a new payload with the hashed password
        payload = {
            "username": username,
            "password": hashed_password,  # Send the hashed password
            "role": role
        }

        # Send the payload with the hashed password to the Redpanda service
        response = requests.post(
            PROCESSING_FLASK_URL,  # External backend URL (Redpanda service)
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        # Check if the username exists and password is correct
        if username in users and check_password_hash(users[username], password):
            session['client_id'] = username  # Use the username as the client ID
            session['session_id'] = str(uuid.uuid4())  # Generate a session ID
            
            # Return success response with client_id and role
            return jsonify({"message": "Login successful", "client_id": username, "role": role}), 200
        else:
            return jsonify({"message": "Login failed. Please check your credentials and try again."}), 401
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load')
def load_page():
    if 'client_id' in session:
        return render_template('load.html')
    else:
        return redirect(url_for('index'))

@app.route('/Post_load', methods=['POST'])
def post_load():
    load_data = request.get_json() 
    user_ip = get_ip_address()
    user_agent = request.headers.get('User-Agent')

    if not load_data:
        print("No data received from the form.")
        return jsonify({"error": "No data received"}), 400

    required_fields = [
        'load_name', 'quantity', 'pickup_time', 'pickup_place', 'destination',
        'clearing_agency', 'clearing_agency_contact', 'number_of_trucks', 'truck_type',
        'payment_days', 'payment_method', 'proof_of_delivery_requirements', 'delivery_duration',
        'additional_instructions', 'recommended_price' 
    ]

    missing_fields = [field for field in required_fields if field not in load_data]
    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400

    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=load_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        print(response_data)
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Load details received", "load":load_data}), 200

if __name__ == '__main__':
    app.run(debug=True)
