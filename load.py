from flask import Flask, request, jsonify, render_template,redirect, url_for, session
""" from kafka import KafkaProducer """
import json
import requests
import os
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random 24-byte string

users = {
    "user1": "password1",
    "user2": "password2"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and users[username] == password:
        session['client_id'] = username  # Use the username as the client ID
        session['session_id'] = str(uuid.uuid4())  # Generate a session ID
        return '', 200  # Successful login, empty response body
    else:
        return 'Login failed. Please check your credentials and try again.', 401

@app.route('/load')
def load_page():
    if 'client_id' in session:
        return render_template('load.html')
    else:
        return redirect(url_for('index'))

@app.route('/Post_load', methods=['POST'])
def post_load():
    load_data = request.get_json() 
    print(load_data)
    #print("Form data received:", load_data)  # Debugging line

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