from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from main import *
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
class GoogleSheetUpdater:
    def __init__(self, service_account_file, document_id, sheet_index=0):
        self.service_account_file = service_account_file
        self.document_id = document_id
        self.sheet_index = sheet_index
        self.gc = self._authorize_client()
        self.worksheet = self._open_worksheet()

    def _authorize_client(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        return gspread.authorize(credentials)

    def _open_worksheet(self):
        spreadsheet = self.gc.open_by_key(self.document_id)
        return spreadsheet.get_worksheet(self.sheet_index)

    def get_dataframe(self):
        records = self.worksheet.get_all_records()
        return pd.DataFrame(records)

# Usage
SERVICE_ACCOUNT_FILE = './data-extraction-tool-433301-eaef27c2bac9.json'
DOCUMENT_ID = '1h2dNYqfsyHtwv-E7Q2tUvrBRQnzXYjjrLPR_ogPuG0c'

updater = GoogleSheetUpdater(SERVICE_ACCOUNT_FILE, DOCUMENT_ID)

# Route to fetch all transporters data as JSON
@app.route('/fetch_transporters', methods=['GET'])
def fetch_transporters():
    try:
        df = updater.get_dataframe()  # Fetch updated data from Google Sheets
        
        # Convert the DataFrame to a list of dictionaries
        transporters = df.to_dict(orient="records")

        # Return the data as JSON
        return jsonify(transporters)
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 500

# Route to fetch and display all transporters
@app.route('/transporters', methods=['GET'])
def transporters():
    try:
        df = updater.get_dataframe()  # Fetch updated data from Google Sheets
        search_query = request.args.get('search', '')

        # Filter the data if a search query is provided
        if search_query:
            df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]

        # Convert to dictionary for rendering in the template
        transporters = df.to_dict(orient="records")
        
        # Fetch favorites from the session
        favorite_ids = session.get('favorites', [])

        return render_template('transporterslist.html', transporters=transporters, favorites=favorite_ids, search_query=search_query)
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 500

# Route to add/remove favorites
@app.route('/favorite/<int:transporter_id>', methods=['POST'])
def favorite(transporter_id):
    favorites = session.get('favorites', [])
    
    if transporter_id in favorites:
        favorites.remove(transporter_id)
    else:
        favorites.append(transporter_id)
    
    session['favorites'] = favorites
    return redirect(url_for('transporters'))

# Route to view favorites
@app.route('/favorites', methods=['GET'])
def view_favorites():
    try:
        df = updater.get_dataframe()  # Fetch updated data from Google Sheets
        favorite_ids = session.get('favorites', [])
        
        # Filter only the favorites
        favorites = df[df['ID'].isin(favorite_ids)].to_dict(orient="records")

        return render_template('favorites.html', transporters=favorites)
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login page (or homepage)
    return redirect(url_for('login'))

@app.route('/load')
def dashboard():
    if 'client_id' in session:
        return render_template('home.html')  # Render the new home dashboard
    else:
        return redirect(url_for('login'))  # Redirect to login if no session exists
    
@app.route('/view_transporters')
def view_transporters():
    if 'client_id' in session:        
        return render_template('transporterslist.html')
    else:
        return redirect(url_for('login'))


@app.route('/form')
def form():
    if 'client_id' in session:
        return render_template('load.html')
    else:
        return redirect(url_for('login'))


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
