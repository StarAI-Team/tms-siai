from flask import Flask, request, jsonify, render_template, url_for, redirect, session, flash
import json
import requests
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import base64
from flask_cors import CORS
import logging
import psycopg2




app = Flask(__name__)
app.secret_key = '025896314785368236'
CORS(app) 
logging.basicConfig(level=logging.DEBUG)

app.secret_key = os.urandom(24) 

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit the max size to 16MB

# Database connection parameters
# Initialize PostgreSQL connection
def create_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host='localhost',
        port='5432'
    )
    return conn

users = {
    "user1": "password1",
    "user2": "password2"
}

@app.route('/get_user_metadata', methods=['GET'])
def get_user_metadata():
    if 'user_id' not in session:
        user_id = str(uuid.uuid4()) 
        session['user_id'] = user_id
    else:
        user_id = session['user_id'] 

    ip_address = request.remote_addr  
    
    metadata = {
        'user_id': user_id,
        'ip_address': ip_address
    }
    return jsonify(metadata)



@app.route('/')
def index():
    return render_template('landingpage.html')

@app.route('/register')
def register():
    return render_template('register.html')



#TRANSPORT SECTION

@app.route('/transporter-package')
def transporter_package():
    return render_template ('transport_package.html')

@app.route('/transporter_package_selected')
def transporter_package_selected():
    return render_template ('transporter_payment_package.html')


@app.route('/welcome-transporter')
def welcome_transporter():
    return render_template ('transport_register.html')


@app.route('/register_transporter', methods=['POST'])
def register_transporter():
    if request.method == 'POST':
        transporter_data = {}
        file_data = {}

        user_id = session.get('user_id')
    print("Initial transporter data received :", transporter_data)
    print("Files in request:", request.files)
    if not user_id:
        return jsonify({"error": "User session expired or user_id missing"}), 400

    transporter_data['user_id'] = user_id

    
    # Process form data and files
    inputs = request.form  # Contains form data only
    for key, value in inputs.items():
        transporter_data[key] = value 


    # Files that are required for the transporter to register
    file_fields = [
        'id_number', 'directorship', 'certificate_of_incorporation', 'proof_of_current_address', 'tax_clearance', 'operators_licence',
        'permits', 'tracking_licence', 'num_of_trucks', 'reg_books', 'certificate_of_fitness',
        'profile_picture'
    ]

    # Segregated required fields by section
    required_fields_by_section = {
        'section1': ['first_name', 'last_name', 'phone_number', 'id_number','id_number_text', 'company_name', 'company_location', 'company_email'],
        'section2': ['company_contact', 'bank_name', 'account_name', 'account_number', 'directorship_text', 'directorship', 'proof_of_current_address_text', 'proof_of_current_address'],
        'section3': ['tax_clearance_text', 'tax_clearance', 'tax_expiry', 'certificate_of_incorporation_text', 'certificate_of_incorporation', 'operators_licence_text', 'operators_licence', 'operators_expiry', 'permits_text', 'permits', 'permit_expiry', 'tracking_licence_text', 'tracking_licence'],
        'section4': ['number_of_trucks', 'num_of_trucks_text', 'num_of_trucks', 'reg_books_text', 'reg_books', 'certificate_of_fitness_text', 'certificate_of_fitness'],
        'section5': ['user_name', 'profile_picture', 'password', 'confirm_password']
    }

    # Handling file uploads
    file_data = {}
    for file_field in file_fields:
        file = request.files.get(file_field)
        logging.debug(f"Received file for field '{file_field}': {file.filename if file else 'No file'}")
        if file and file.filename:
                try:
                    # Directly uploading the file to the MinIO service
                    files = {'file': (file.filename, file.stream, file.mimetype)}
                    logging.debug(f"Uploading file: {file.filename}, MIME type: {file.mimetype}")

                    response = requests.post('http://localhost:6000/upload-file', files=files)
                    logging.debug(f"Response from MinIO upload for '{file_field}': {response.status_code}, {response.text}")

                    if response.status_code == 200:
                        file_data[file_field] = response.text 
                        logging.debug(f"Successfully uploaded {file_field}: {file_data[file_field]}")
                    else:
                        return jsonify({"error": f"Failed to upload {file_field}: {response.text}"}), response.status_code
                except Exception as e:
                    return jsonify({"error": f"Error uploading {file_field}: {str(e)}"}), 500

    # Merging form data with file data if files exist
    transporter_data.update(file_data)

    # Password validation for Section 5 
    current_section = transporter_data.get('current_section')
    if current_section == 'section5':
        password = transporter_data.get('form_data', {}).get('password')
        confirm_password = transporter_data.get('form_data', {}).get('confirm_password')

        # Check if passwords are provided and match
        if password and confirm_password:
            if password != confirm_password:
                return jsonify({"error": "Passwords do not match"}), 400
            else:
                # Hash the password before storing it
                transporter_data['form_data']['password'] = generate_password_hash(password)



     # Validate required fields
    missing_fields = [field for field in required_fields_by_section.get(current_section, []) if field not in transporter_data]

    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    
    # Print transporter data before sending to the next service
    print("Final transporter data being sent:", transporter_data)


    # Send the data to the processing Flask application or service
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        # Print the transporter_data before sending
        print("Sending the following data to processing URL:", transporter_data)
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=transporter_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        print("Response status code:", response.status_code)
        print("Response data:", response_data)
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        print("Error occurred while sending to processing URL:", e)
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Data submitted successfully"}), 200




#BID SECTION

@app.route('/bid')
def bid():
    conn = create_connection()
    with conn.cursor() as cur:
        query = """
            SELECT 
                load_name, 
                stars, 
                price, 
                route, 
                status, 
                perfect_match, 
                private 
            FROM 
                loads;  
        """
        cur.execute(query)
        results = cur.fetchall()

    # Format the results into a list of dictionaries
    loads = []
    for row in results:
        load_info = {
            'load_name': row[0],
            'stars': row[1],
            'price': row[2],
            'route': row[3],
            'status': row[4],
            'perfect_match': row[5],
            'private': row[6]
        }
        loads.append(load_info)

    return render_template('allbid.html', loads=loads)


@app.route('/place_bid')
def auction():
    return render_template('bid.html')


@app.route('/place_bid/<string:load_name>')
def place_bid(load_name):
    conn = create_connection()
    with conn.cursor() as cur:
        query = """
            SELECT 
                route, 
                quantity, 
                rate, 
                perfect_match, 
                private 
            FROM 
                loads 
            WHERE 
                load_name = %s;
        """
        cur.execute(query, (load_name,))
        load_details = cur.fetchone()

    if load_details:
        return render_template('bid.html', load_name=load_name, 
                               route=load_details[0], 
                               quantity=load_details[1], 
                               rate=load_details[2], 
                               perfect_match=load_details[3], 
                               private=load_details[4])
    else:
        return "Load not found", 404

# Endpoint to handle bid success
@app.route('/place_bid_done', methods=['POST'])
def place_bid_done():
    if request.is_json:
        payload = request.get_json()  
    else:
        return jsonify({"error": "Invalid content type"}), 400
    
    # Debug: Print incoming JSON payload
    print("Incoming JSON Payload:", payload)
    bid_data = { 
        **{key: payload[key] for key in payload if key not in ['form_data']} ,
        **{key: payload['form_data'][key] for key in payload['form_data']}
    } 
    print("REQUEST DATA", bid_data)  

    # Send the data to the processing Flask application or service
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        # Print the transporter_data before sending
        print("Sending the following data to processing URL:", bid_data)
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=bid_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        print("Response status code:", response.status_code)
        print("Response data:", response_data)
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        print("Error occurred while sending to processing URL:", e)
        return jsonify({"error": str(e)}), 500
    


#SHIPPER SECTION
@app.route('/shipper-package')
def shipper_package():
    return render_template ('shipper_package.html')


@app.route('/shipper_package_selected')
def shipper_package_selected():
    return render_template ('shipper_payment_package.html')

@app.route('/welcome-shipper')
def welcome_shipper():
    return render_template ('shipper_register.html')



@app.route('/shipper_register', methods=['POST'])
def shipper_register():
    if request.method == 'POST':
        shipper_data = {}
        file_data = {}

        user_id = session.get('user_id')
    print("Initial shipper data received :", shipper_data)
    print("Files in request:", request.files)
  
    if not user_id:
        return jsonify({"error": "User session expired or user_id missing"}), 400

    shipper_data['user_id'] = user_id
    print(shipper_data)
    

    
    # Process form data and files
    inputs = request.form  # Contains form data only
    for key, value in inputs.items():
        shipper_data[key] = value 

    

    #files that are required for the shipper to register 
    file_fields = [
        'id_number','directorship', 'certificate_of_incorporation', 'proof_of_current_address', 'tax_clearance',
        'profile_picture',
        
    ]

    # Segregated required fields by section
    required_fields_by_section = {
        'section1':['first_name', 'last_name', 'phone_number', 'id_number','id_number_text', 'company_name', 'company_location', 'company_email'],
        'section2': ['company_contact', 'bank_name', 'account_name', 'account_number', 'directorship_text','directorship', 'proof_of_current_address_text', 'proof_of_current_address' ],
        'section3': ['tax_clearance_text', 'tax_clearance', 'tax_expiry', 'certificate_of_incorporation_text', 'certificate_of_incorporation'],
        'section4': ['user_name', 'profile_picture', 'password', 'confirm_password']
    }

    # Handling file uploads
    file_data = {}
    for file_field in file_fields:
        file = request.files.get(file_field)
        logging.debug(f"Received file for field '{file_field}': {file.filename if file else 'No file'}")
        if file and file.filename:
                try:
                    # Directly uploading the file to the MinIO service
                    files = {'file': (file.filename, file.stream, file.mimetype)}
                    logging.debug(f"Uploading file: {file.filename}, MIME type: {file.mimetype}")

                    response = requests.post('http://localhost:6000/upload-file', files=files)
                    logging.debug(f"Response from MinIO upload for '{file_field}': {response.status_code}, {response.text}")

                    if response.status_code == 200:
                        file_data[file_field] = response.text 
                        logging.debug(f"Successfully uploaded {file_field}: {file_data[file_field]}")
                    else:
                        return jsonify({"error": f"Failed to upload {file_field}: {response.text}"}), response.status_code
                except Exception as e:
                    return jsonify({"error": f"Error uploading {file_field}: {str(e)}"}), 500

    shipper_data.update(file_data)

    # Password validation for Section 4
    current_section = shipper_data.get('current_section')
    if current_section == 'section4':
        password = shipper_data.get('form_data', {}).get('password')
        confirm_password = shipper_data.get('form_data', {}).get('confirm_password')

        # Check if passwords are provided and match
        if password and confirm_password:
            if password != confirm_password:
                return jsonify({"error": "Passwords do not match"}), 400
            else:
                # Hash the password before storing it
                shipper_data['form_data']['password'] = generate_password_hash(password)
    


    # Validate required fields
    missing_fields = [field for field in required_fields_by_section.get(current_section, []) if field not in shipper_data]

    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    
    
# Print shi[[er]] data before sending to the next service
    print("Final shipper data being sent:", shipper_data)
  

    
    # Send the data to the processing Flask application
    # endpoint of the kafka server
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        # Print the shipper before sending
        print("Sending the following data to processing URL:", shipper_data)
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=shipper_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    

#REQUESTS SECTION
@app.route('/transporter_requests')
def transporter_requests():
    return render_template('requests.html')


@app.route('/post_requests', methods=['POST'])
def post_requests(): 
    if request.is_json:
        payload = request.get_json()  
    else:
        return jsonify({"error": "Invalid content type"}), 400
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "User session expired or user_id missing"}), 400
    request_data = {}
    request_data['user_id'] = user_id
    # Debug: Print incoming JSON payload
    print("Incoming JSON Payload:", payload)
    request_data = { 
        **{key: payload[key] for key in payload if key not in ['form_data']} ,
        **{key: payload['form_data'][key] for key in payload['form_data']}
    } 
    print("REQUEST DATA", request_data)  



    # Send the data to the processing Flask application or service
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        # Print the transporter_data before sending
        print("Sending the following data to processing URL:", request_data)
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        print("Response status code:", response.status_code)
        print("Response data:", response_data)
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        print("Error occurred while sending to processing URL:", e)
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Data submitted successfully"}), 200

#TRUCK SECTION

@app.route('/trucks')
def trucks():
    conn = create_connection()
    with conn.cursor() as cur:
        query = """
            SELECT 
                id, 
                truck_reg, 
                truck_type, 
                trailer1_reg, 
                trailer2_reg, 
                driver_name, 
                id_number, 
                passport_number, 
                license_number, 
                phone_number 
            FROM 
                booked_trucks;  -- Change this to your actual table name
        """
        cur.execute(query)
        results = cur.fetchall()

    # Format the results into a list of dictionaries
    booked_trucks = []
    for row in results:
        truck_info = {
            'id': row[0],
            'truck_reg': row[1],
            'truck_type': row[2],
            'trailer1_reg': row[3],
            'trailer2_reg': row[4],
            'driver_name': row[5],
            'id_number': row[6],
            'passport_number': row[7],
            'license_number': row[8],
            'phone_number': row[9]
        }
        booked_trucks.append(truck_info)

    return render_template('trucks.html', trucks=booked_trucks)


@app.route('/trucks-book', methods=['POST'])
def book_trucks():
    data = request.json
    selected_trucks = data.get('selected_trucks', [])
    # Logic for booking trucks 
    print(f"Booking trucks with IDs: {selected_trucks}")
    return jsonify({"message": "Trucks booked successfully!"})

@app.route('/trucks-delete', methods=['POST'])
def delete_trucks():
    data = request.json
    selected_trucks = data.get('selected_trucks', [])
    # Logic for deleting trucks (e.g., remove from database)
    global trucks
    trucks = [truck for truck in trucks if str(truck['id']) not in selected_trucks]
    print(f"Deleted trucks with IDs: {selected_trucks}")
    return jsonify({"message": "Trucks deleted successfully!"})

@app.route('/add_truck', methods=['POST'])
def add_truck():
    truck_data = request.json
    new_truck = {
        "id": len(trucks) + 1,  
        "truck_reg": truck_data['truck_reg'],
        "truck_type": truck_data['truck_type'],
        "trailer1_reg": truck_data['trailer1_reg'],
        "trailer2_reg": truck_data['trailer2_reg'],
        "driver_name": truck_data['driver_name'],
        "id_number": truck_data['id_number'],
        "passport_number": truck_data['passport_number'],
        "license_number": truck_data['license_number'],
        "phone_number": truck_data['phone_number']
    }
    trucks.append(new_truck)
    return jsonify({"message": "Truck added successfully!"})

@app.route('/truck_action', methods=['POST'])
def truck_action():
    if request.is_json:
        payload = request.get_json()
        print("Received payload:", payload)
    else:
        return jsonify({"error": "Invalid content type"}), 400
    
    # Extract and normalize event details
    event_name = payload.get("event_name", "").strip().lower()  # CHANGED: Normalize the event_name to lowercase
    print("Received event name:", event_name) 
    selected_trucks = payload.get("selected_trucks", [])

    truck_data = {
        "event_name": payload.get("event_name"),
        "user_id": payload.get("user_id"),
        "ip_address": payload.get("ip_address"),
        "timestamp": payload.get("timestamp"),
        "user_agent": payload.get("user_agent"),
        "selected_trucks": selected_trucks
    }

    # Process based on normalized event_name
    if event_name == 'add_truck':  
        # Logic to add trucks
        print(f"Adding trucks: {selected_trucks}")
        message = "Truck(s) added successfully!"
    elif event_name == 'book_truck':  
        # Logic to book trucks
        print(f"Booking trucks: {selected_trucks}")
        message = "Truck(s) booked successfully!"
    elif event_name == 'delete_truck': 
        # Logic to delete trucks
        print(f"Deleting trucks: {selected_trucks}")
        message = "Truck(s) deleted successfully!"
    else:
        return jsonify({"error": "Unknown event type"}), 400  

    # Debug: Print the truck data before sending to the external service
    print("TRUCK_DATA", truck_data)

    # Send the truck data to the processing Flask service
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        print(f"Sending truck data to {PROCESSING_FLASK_URL}: {truck_data}")
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=truck_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        print("Response status code:", response.status_code)
        print("Response data:", response_data)
        return jsonify({"message": message, "processing_response": response_data}), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while sending data to {PROCESSING_FLASK_URL}: {e}")
        return jsonify({"error": str(e)}), 500
    

#load_pool
def fetch_loads_data():
    loads_data = []
    conn = create_connection()
    with conn.cursor() as cur:
        query = """
            SELECT load_id, route, transport_date, rate, load_type FROM loads;  -- Change this to your actual loads table name
        """
        cur.execute(query)
        results = cur.fetchall()

    # Format the results into a list of dictionaries
    for row in results:
        load_info = {
            'load_id': row[0],
            'route': row[1],
            'date': row[2],
            'rate': row[3],
            'load_type': row[4]
        }
        loads_data.append(load_info)
    
    return loads_data

@app.route('/load-pool')
def loadpool():
    loads_data = fetch_loads_data() 
    return render_template('loadpool.html', loads=loads_data)

@app.route('/api/loads')
def get_loads():
    loads_data = fetch_loads_data()  
    return jsonify(loads_data)

@app.route('/documents')
def view_documents():
    # Query to retrieve documents from the database
    documents_data = []
    conn = create_connection()
    with conn.cursor() as cur:
        query = """
            SELECT title, file_name, file_url FROM documents;  -- Change this to your actual documents table name
        """
        cur.execute(query)
        results = cur.fetchall()

    # Format the results into the expected structure
    for row in results:
        title = row[0]
        documents_data.append({
            'title': title,
            'files': [
                {'name': row[1], 'url': row[2]}  # Assuming the file_name and file_url are in columns 1 and 2
            ]
        })
    
    return render_template('docs.html', documents=documents_data)

@app.route('/chat')
def chat():
    messages = [
        {'text': 'Hello, how can I help you?', 'type': 'incoming'},
        {'text': 'I need information about the loads.', 'type': 'outgoing'},
        {'text': 'Sure! Here are the details.', 'type': 'incoming'},
    ]
    
    contacts = ['J&J', 'TENGWA', 'CROSS COUNTRY', 'CARGO CONNECT', 'FLEET SYNC']

    return render_template('chat.html', messages=messages, contacts=contacts)


@app.route('/analytics')
def analytics():
    # Placeholder for analytics data
    return render_template('analytics.html')


@app.route('/api/analytics-data')
def analytics_data():
    
    return jsonify({
        'labels': ['January', 'February', 'March', 'April', 'May'],
        'data': [12, 19, 3, 5, 2],
    })

@app.route('/history')
def view_history():
    # Query to retrieve load history from the database
    loads = []
    conn = create_connection()
    with conn.cursor() as cur:
        query = """
            SELECT load_id, origin, destination, transport_date, status FROM load_history;  -- Change this to your actual load history table name
        """
        cur.execute(query)
        results = cur.fetchall()

    # Format the results into a list of dictionaries
    for row in results:
        load_info = {
            'load_id': row[0],
            'origin': row[1],
            'destination': row[2],
            'transport_date': row[3],
            'status': row[4]
        }
        loads.append(load_info)

    return render_template('history.html', loads=loads)

@app.route('/transporter_dashboard')
def transporter_dashboard():
     if 'client_id' in session:
        return render_template('transporterdashboard.html')
     else:
        return redirect(url_for('index'))


#LOAD SECTION 

@app.route('/sign-in')
def sign_in():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')  # Use request.json since you're sending JSON
    password = request.json.get('password')
    role = request.json.get('role')

    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Check in shipper_profile table
        cursor.execute("SELECT user_id, password FROM shipper_profile WHERE user_id = %s", (username,))
        shipper = cursor.fetchone()

        # Check in transporter_profile table
        cursor.execute("SELECT user_id, password FROM transporter_profile WHERE user_id = %s", (username,))
        transporter = cursor.fetchone()

        # Validate credentials
        if shipper and shipper[1] == password and role == "shipper":
            session['client_id'] = username  
            session['session_id'] = str(uuid.uuid4())  
            return jsonify({"message": "Login successful"}), 200  
        elif transporter and transporter[1] == password and role == "transporter":
            session['client_id'] = username   
            return jsonify({"message": "Login successful"}), 200  
        else:
            return jsonify({"message": "Login failed. Please check your credentials and try again."}), 401  
    finally:
        cursor.close()
        conn.close()
    
@app.route('/shipper-dashboard')
def shipper_dashboard():
    if 'client_id' in session:
        return render_template('shipperdashboard.html')
    else:
        return redirect(url_for('index'))

@app.route('/load')
def post_load_page():
    return render_template('load.html')

@app.route('/post_load', methods=['POST'])
def post_load():
    load_data = request.get_json() 
    print(load_data)
   
    event_name = load_data.get("event_name", "")
    current_step = 1
    if "step_2" in event_name:
        current_step = 2

    required_fields_per_step = {
        1: ['load_name', 'quantity', 'pickup_time', 'pickup_place', 'destination', 'clearing_agency', 'clearing_agency_contact'],  
        2: ['number_of_trucks', 'truck_type',
        'payment_days', 'payment_method', 'proof_of_delivery_requirements', 'delivery_duration','additional_instructions', 'recommended_price' ],
    }

     # Get the required fields for the current step
    required_fields = required_fields_per_step.get(current_step, [])

    if not load_data:
        print("No data received from the form.")
        return jsonify({"error": "No data received"}), 400
    
    
    # Process transporter data (if any)
    transporter_data = {k: v for k, v in load_data.items() if k.startswith('transporter_')}
    if transporter_data:
        print(f"Transporter(s) selected: {transporter_data}")

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



@app.route('/shipper-history')
def view_shipper_history():
    
    loads = [
        {'load_id': '1', 'origin': 'City A', 'destination': 'City B', 'transport_date': '2024-09-01', 'status': 'Delivered'},
        {'load_id': '2', 'origin': 'City C', 'destination': 'City D', 'transport_date': '2024-09-15', 'status': 'In Transit'},
        # Add more loads as needed...
    ]
    return render_template('shipperhistory.html', loads=loads)
    
@app.route('/shipper_analytics')
def shipper_analytics():
    # Placeholder for analytics data
    return render_template('shipperanalytics.html')



@app.route('/shipper_documents')
def shipper_documents():
     # Query to retrieve documents from the database
    documents_data = []
    conn = create_connection()
    with conn.cursor() as cur:
        query = """
            SELECT title, file_name, file_url FROM documents;  -- Change this to your actual documents table name
        """
        cur.execute(query)
        results = cur.fetchall()

    # Format the results into the expected structure
    for row in results:
        title = row[0]
        documents_data.append({
            'title': title,
            'files': [
                {'name': row[1], 'url': row[2]}  # Assuming the file_name and file_url are in columns 1 and 2
            ]
        })
    return render_template('shipperdocs.html', documents=documents_data)


@app.route('/shipper_chat')
def shipper_chat():
    
    messages = [
        {'text': 'Hello, how can I help you?', 'type': 'incoming'},
        {'text': 'I need information about the loads.', 'type': 'outgoing'},
        {'text': 'Sure! Here are the details.', 'type': 'incoming'},
    ]
    
    contacts = ['J&J', 'TENGWA', 'CROSS COUNTRY', 'CARGO CONNECT', 'FLEET SYNC']

    return render_template('shipperchat.html', messages=messages, contacts=contacts)



# Mock database of transporters for demonstration
transporters = [
    {"id": 1, "name": "Cargo Sync", "is_favourite": False, "fleet_size": 10, "rating": 4, "ranking": "premium", "git": "1800", "routes": "Harare-Bulawayo""Mbare-Kwekwe", "reviews": ["Could be better"]},
    {"id": 2, "name": "FleetJoy", "is_favourite": True, "fleet_size": 5, "rating": 3, "ranking": "standard", "git": "2000", "routes": "Harare-Mutare", "reviews": ["Great service!"]},
    
]

@app.route('/view-transporters')
def view_transporters():
    return render_template('alltransporters.html', transporters=transporters)

@app.route('/get_transporter_details/<int:transporter_id>')
def get_transporter_details(transporter_id):
    transporter = next((t for t in transporters if t['id'] == transporter_id), None)
    if transporter:
        return jsonify(transporter)
    return jsonify({'error': 'Transporter not found'}), 404

@app.route('/toggle_favourite', methods=['POST'])
def toggle_favourite():
    data = request.json
    transporter_id = int(data.get('transporter_id'))  # Ensure transporter_id is an integer
    is_favourite = data.get('is_favourite')

    # Find transporter by ID and update their is_favourite status
    for transporter in transporters:
        if transporter['id'] == transporter_id:
            transporter['is_favourite'] = is_favourite
            break

    return jsonify({'success': True, 'transporter_id': transporter_id, 'new_favourite_status': is_favourite})

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.json
    transporter_id = int(data.get('transporter_id'))
    review_data = data.get('reviews_text')
    rating = data.get('rating')
    print("Received data:", data)

    # Find transporter and add the review
    transporter_found = False
    for transporter in transporters:
        if transporter['id'] == int(transporter_id):
            # Append the review and rating to the transporter's data
            transporter['reviews'].append({
                'review': review_data,
                'rating': rating,
                'timestamp': data.get('timestamp', None)  # Optional: timestamp
            })
            transporter_found = True
            break  # Exit the loop once the transporter is found

    if not transporter_found:
        return jsonify({"error": "Transporter not found"}), 404

    # Proceed with sending data to the service on port 6000
    print("Sending data to port 6000:", {"review": review_data, "rating": rating})

    # Send the data to the processing Flask application or service
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        response = requests.post(
            PROCESSING_FLASK_URL,
            json={
                "review": review_data,
                "rating": rating,
                "transporter_id": transporter_id,
                "timestamp": data.get('timestamp', None)
            },
            headers={'Content-Type': 'application/json'}
        )

        # Log the response status and data
        print(f"Response status code from port 6000: {response.status_code}")
        response_data = response.json()
        print("Response data from port 6000:", response_data)
        
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        print("Error occurred while sending data to processing URL:", e)
        return jsonify({"error": str(e)}), 500





#SECTION TO ACCEPT OFFERS 

offers = [
    {'id': 1, 'name': 'Star International', 'details': 'Most experienced with Beira-Harare Route.', 'price': '$1400', 'perfect_match': True},
    {'id': 2, 'name': 'Ngwena', 'details': 'Premium Member', 'price': '$1400', 'perfect_match': False},
    {'id': 3, 'name': 'Tengwa', 'details': 'Free customs clearing, shorter transit time.', 'price': '$1250', 'perfect_match': False},
]

# Route to display offers
@app.route('/view_offers')
def view_offers():
    return render_template('alloffers.html', offers=offers)

# Provide all offer data as JSON
@app.route('/api/offers')
def api_offers():
    return jsonify(offers)

# Provide a single offer based on ID
@app.route('/api/offers/<int:offer_id>')
def api_offer(offer_id):
    offer = next((offer for offer in offers if offer['id'] == offer_id), None)
    if offer:
        return jsonify(offer)
    else:
        return jsonify({'error': 'Offer not found'}), 404

# Endpoint to handle offer acceptance
@app.route('/accept_offer', methods=['POST'])
def accept_offer():
    if request.is_json:
        payload = request.get_json()  
    else:
        return jsonify({"error": "Invalid content type"}), 400
    
    # Debug: Print incoming JSON payload
    print("Incoming JSON Payload:", payload)
    offer_data = { 
        **{key: payload[key] for key in payload if key not in ['form_data']} ,
        **{key: payload['form_data'][key] for key in payload['form_data']}
    } 
    print("REQUEST DATA", offer_data)  

    # Send the data to the processing Flask application or service
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        # Print the transporter_data before sending
        print("Sending the following data to processing URL:", offer_data)
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=offer_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        print("Response status code:", response.status_code)
        print("Response data:", response_data)
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        print("Error occurred while sending to processing URL:", e)
        return jsonify({"error": str(e)}), 500
    
#AGREEMENT SECTION
# Sample data for loads
trip = [
    {
        'id': 1,
        'load': 'Wheat',
        'quantity': '2 Tonnes',
        'route': 'Harare RoadPort 08:00am - Beira',
        'truck_type': '10 Tankers',
        'payment_days': '60 Days Cash',
        'amount': '$1400'
    },
]

@app.route('/agreement')
def agreement():
    return render_template('agreement.html', trip=trip)

# To retrieve loads via API
@app.route('/api/trip')
def get_trip():
    return jsonify(trip)


@app.route('/private_load')
def private_load():
    return  render_template('privateload.html')

# Sample user database
users_db = {
    "john.doe@example.com": {
        "name": "Lee Doe",
        "password": generate_password_hash("password123"),
        "email": "john.doe@example.com",
        "phone": "+123456789",
        "address": "123 Main Street, City, Country",
        "profile_picture": "user-profile.jpg",
        "email_notifications": "enabled",
        "sms_notifications": "enabled",
        "profile_visibility": "public",
        "share_data": "no",
    }
}

def get_user_by_email(email):
    return users_db.get(email)

# Set up the upload folder (not used for MinIO, but keeping it for other potential uses)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve the user account page
@app.route('/account')
def user_account():
    email = session.get('email', 'john.doe@example.com')
    user = users_db.get(email)
    return render_template('account.html', user=user)

# Route to update profile information
@app.route('/update-profile', methods=['POST'])
def update_profile():
    email = session.get('email', 'john.doe@example.com')
    user = users_db.get(email)
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        profile_picture = request.files.get('profile_picture')  # Use .get to avoid KeyError

        # Save profile picture to MinIO 
        if profile_picture and profile_picture.filename:
            try:
                files = {'file': (profile_picture.filename, profile_picture.stream, profile_picture.mimetype)}
                response = requests.post('http://localhost:6000/upload-file', files=files)
                
                if response.status_code == 200:
                    user['profile_picture'] = response.text  # Get the file URI from MinIO response
                else:
                    flash(f"Failed to upload profile picture: {response.text}", "error")
                    return redirect(url_for('user_account'))
            except Exception as e:
                flash(f"Error uploading profile picture: {str(e)}", "error")
                return redirect(url_for('user_account'))

        # Update other details
        user['name'] = name
        user['phone'] = phone
        user['address'] = address
        flash("Profile updated successfully!", "success")
    
    return redirect(url_for('user_account'))

# Route to change password
@app.route('/update-password', methods=['POST'])
def update_password():
    email = session.get('email', 'john.doe@example.com')
    user = users_db.get(email)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')  # Use .get() to avoid KeyError
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for('user_account'))

        # Check current password
        if not check_password_hash(user['password'], current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for('user_account'))
        
        # Check if new password matches confirm password
        if new_password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for('user_account'))
        
        # Update password
        user['password'] = generate_password_hash(new_password)
        flash("Password updated successfully!", "success")
    
    return redirect(url_for('user_account'))


@app.route('/privacy_settings', methods=['POST'])
def privacy_settings():
    email = request.form.get('email')  # Get the email from the form (use session in real app)
    profile_visibility = request.form.get('profile_visibility')
    share_data = request.form.get('share_data', 'yes')  # Default to 'yes'

    # Get the user by email
    user = get_user_by_email(email)

    if user:
        # Update the user's privacy settings
        user['profile_visibility'] = profile_visibility
        user['share_data'] = share_data
        flash('Privacy settings updated successfully!')
    else:
        flash('User not found.')

    return redirect(url_for('user_account'))


@app.route('/notification_settings', methods=['POST'])
def notification_settings():
    email = request.form.get('email')  # placeholder for user session in real app)
    email_notifications = request.form.get('email_notifications', 'enabled')  
    sms_notifications = request.form.get('sms_notifications', 'enabled') 

    # Get the user by email
    user = get_user_by_email(email)

    if user:
        # Update the user's notification settings
        user['email_notifications'] = email_notifications
        user['sms_notifications'] = sms_notifications
        flash('Notification settings updated successfully!')
    else:
        flash('User not found.')

    return redirect(url_for('user_account'))


# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('sign-in'))
        

if __name__ == '__main__':
    app.run(debug = True, port=8001)



