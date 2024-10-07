from flask import Flask, request, jsonify, render_template, url_for, redirect, session
import json
import requests
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import base64
from flask_cors import CORS
import logging





app = Flask(__name__)
CORS(app) 
logging.basicConfig(level=logging.DEBUG)
app.secret_key = os.urandom(24)  

users = {
    "user1": "password1",
    "user2": "password2"
}

""" 
@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload route called")  # Debugging statement to indicate the upload route is accessed

    if 'file' not in request.files:
        print("No file part in the request")  # Debugging statement for missing file
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        print("No selected file")  # Debugging statement for no file selected
        return "No selected file", 400

    print(f"File received: {file.filename}")  # Debugging statement for the file received

    # Prepare to send the file to the second Flask app (MinIO handler)
    files = {'file': (file.filename, file.stream, file.mimetype)}
    print(f"Preparing to send file to MinIO: {files}")  # Debugging statement before sending

    try:
        response = requests.post('http://localhost:6000/upload-file', files=files)
        print(f"Response from MinIO: Status Code - {response.status_code}, Response Text - {response.text}")  # Debugging response from MinIO

        if response.status_code == 200:
            print("File uploaded successfully")  # Debugging statement for successful upload
            return f"File uploaded successfully. File stored at: {response.text}"
        else:
            print(f"Failed to upload file. Error: {response.text}")  # Debugging statement for failed upload
            return f"Failed to upload file. Error: {response.text}", response.status_code
    except Exception as e:
        print(f"Exception occurred while uploading file: {str(e)}")  # Debugging statement for exception handling
        return "Internal server error", 500 """

@app.route('/get_user_metadata', methods=['GET'])
def get_user_metadata():
    user_id = str(uuid.uuid4())  
    ip_address = request.remote_addr  
    
    metadata = {
        'user_id': user_id,
        'ip_address': ip_address
    }
    return jsonify(metadata)

@app.route('/')
def index():
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
    print("Initial transporter data received :", transporter_data)
    print("Files in request:", request.files)

    
    # Process form data and files
    inputs = request.form  # Contains form data only
    for key, value in inputs.items():
        transporter_data[key] = value 


    # Files that are required for the transporter to register
    file_fields = [
        'directorship', 'certificate_of_incorporation', 'proof_of_current_address', 'tax_clearance', 'operators_licence',
        'permits', 'tracking_licence', 'num_of_trucks', 'reg_books', 'certificate_of_fitness',
        'profile_picture'
    ]

    # Segregated required fields by section
    required_fields_by_section = {
        'section1': ['first_name', 'last_name', 'phone_number', 'id_number', 'company_name', 'company_location', 'company_email'],
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
@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload route called")

    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    try:
        response = requests.post('http://localhost:6000/upload-file', files={'file': (file.filename, file.stream, file.mimetype)})
        return f"File uploaded successfully. File stored at: {response.text}" if response.status_code == 200 else f"Failed to upload file. Error: {response.text}", response.status_code
    except Exception as e:
        return f"Exception occurred while uploading file: {str(e)}", 500



#BID SECTION

@app.route('/bid')
def bid():
    # Example data 
    loads = [
        {
            'load_name': 'Pelcravía',
            'stars': '★★★★★',
            'price': '1200',
            'route': 'Wheat Harare - Beira',
            'status': 'Premium Member',
            'perfect_match': True
        },
        {
            'load_name': 'Ngwena',
            'stars': '★★★★☆',
            'price': '1100',
            'route': 'Harare - Lusaka',
            'status': 'Standard Member',
            'perfect_match': False
        },
        {
            'load_name': 'Nestle',
            'stars': '★★★★★',
            'price': '1250',
            'route': 'Harare - Gaborone',
            'status': 'Premium Member',
            'perfect_match': False
        },
    ]
    
    return render_template('allbid.html', loads=loads)


@app.route('/place_bid')
def auction():
    return render_template('bid.html')


@app.route('/place_bid/<string:load_name>')
def place_bid(load_name):

    load_data = {
        'Pelcravía': {'route': 'Wheat Harare - Beira', 'quantity': '2 Tonnes', 'rate': '1200', 'perfect_match':True},
        'Ngwena': {'route': 'Harare - Lusaka', 'quantity': '3 Tonnes', 'rate': '1100', 'perfect_match':False},
        'Nestle': {'route': 'Harare - Gaborone', 'quantity': '1.5 Tonnes', 'rate': '1250', 'perfect_match':False}
    }

    # Fetch the load details dynamically
    load_details = load_data.get(load_name)

    if load_details:
        return render_template('bid.html', load_name=load_name, route=load_details['route'], quantity=load_details['quantity'], rate=load_details['rate'], perfect_match=load_details['perfect_match'])
    else:
        return "Load not found", 404



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
    if request.is_json:
        payload = request.get_json()  
    else:
        return jsonify({"error": "Invalid content type"}), 400
    
    # Debug: Print incoming JSON payload
    print("Incoming JSON Payload:", payload)
    shipper_data = {
        **{key: payload[key] for key in payload if key not in ['form_data']} ,
        **{key: payload['form_data'][key] for key in payload['form_data']}
    } 
    print("CLIENT DATA", shipper_data)

    

    #files that are required for the shipper to register 
    file_fields = [
        'directorship', 'certificate_of_incorporation', 'proof_of_current_address', 'tax_clearance',
        'profile_picture',
        
    ]

    # Segregated required fields by section
    required_fields_by_section = {
        'section1':['first_name', 'last_name', 'phone_number', 'id_number','id_number', 'company_name', 'company_location', 'company_email'],
        'section2': ['company_contact', 'bank_name', 'account_name', 'account_number', 'directorship_text','directorship', 'proof_of_current_address_text', 'proof_of_current_address' ],
        'section3': ['tax_clearance_text', 'tax_clearance', 'tax_expiry', 'certificate_of_incorporation_text', 'certificate_of_incorporation'],
        'section4': ['user_name', 'profile_picture', 'password', 'confirm_password']
    }

    # Handling file uploads
    file_data = {}
    for file_field in file_fields:
        if file_field in request.files:
            file = request.files[file_field]
            if file:
                 # creating a secure filename and storing it in the uploads folder
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path) # Save the file to the disk

                #generating URI to access this file 
                file_uri = url_for('uploaded_file', filename=unique_filename, _external=True)
                file_data[file_field] = file_uri

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
    


    #Ensuring all required fields are present
    required_fields = [
        'first_name', 'last_name', 'phone_number', 'id_number',
        'company_name', 'bank_name', 'account_name', 'account_number', 
        'company_location', 'company_email', 'company_contact', 'bank_name', 'account_name', 'account_number',
        'directorship_text', 'proof_of_current_address_text', 
        'tax_clearance_text', 'certificate_of_incorporation_text', 'user_name', 'password' 
        
    ] + file_fields


    # Validate required fields
    missing_fields = [field for field in required_fields_by_section.get(current_section, []) if field not in shipper_data]

    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    
    
# Print transporter data before sending to the next service
    print("Final transporter data being sent:", shipper_data)
  

    
    # Send the data to the processing Flask application
    # endpoint of the kafka server
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        # Print the transporter_data before sending
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
    
    return jsonify({"message": "shipper registered successfully"}), 200



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
    # Sample data for  trucks
    booked_trucks = [
        {
            'id': 1,
            'truck_reg': 'AEF 1234',
            'truck_type': 'Tanker',
            'trailer1_reg': 'AEF 1234',
            'trailer2_reg': 'AEF 1234',
            'driver_name': 'J.MOYO',
            'id_number': '522-CDR',
            'passport_number': '522-CDR',
            'license_number': '522-CDR',
            'phone_number': '01258956'
        },
        {
            'id': 2,
            'truck_reg': 'AEF 5678',
            'truck_type': 'Bulk',
            'trailer1_reg': 'AEF 5678',
            'trailer2_reg': 'AEF 5678',
            'driver_name': 'Abisha Beta',
            'id_number': '523-DEF',
            'passport_number': '523-DEF',
            'license_number': '523-DEF',
            'phone_number': '01258957'
        }
    ]
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
loads_data = [
    {
        'load_id': 1,
        'route': 'Harare-Gweru',
        'date': '2024-09-30',
        'coordinates': [29.8325, -18.9245],  
        'rate': 100,
        'load_type': 'Goods'
    },
    {
        'load_id': 2,
        'route': 'Kadoma-Gweru',
        'date': '2024-09-30',
        'coordinates': [29.9000, -18.3700],  
        'rate': 200,
        'load_type': 'Machinery'
    }
]


@app.route('/load-pool')
def loadpool():
    return render_template('loadpool.html')

@app.route('/api/loads')
def get_loads():
    return jsonify(loads_data)

documents_data = [
    {
        'title': 'CROSS COUNTRY',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
    {
        'title': 'CARGO CONNECT',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
    {
        'title': 'TENGWA',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
]

@app.route('/documents')
def documents():
    return render_template('docs.html', documents=documents_data)

@app.route('/chat')
def chat():
    
    messages = [
        {'text': 'Hello, how can I help you?', 'type': 'incoming'},
        {'text': 'I need information about the loads.', 'type': 'outgoing'},
        {'text': 'Sure! Here are the details.', 'type': 'incoming'},
    ]
    return render_template('chat.html', messages=messages)

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
    # Mock data for demonstration
    loads = [
        {'load_id': '1', 'origin': 'City A', 'destination': 'City B', 'transport_date': '2024-09-01', 'status': 'Delivered'},
        {'load_id': '2', 'origin': 'City C', 'destination': 'City D', 'transport_date': '2024-09-15', 'status': 'In Transit'},
        # Add more loads as needed...
    ]
    return render_template('history.html', loads=loads)
    

@app.route('/transporter_dashboard')
def transporter_dashboard():
    return render_template('transporterdashboard.html')


#LOAD SECTION 

@app.route('/sign-in')
def sign_in():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')  # Use request.json since you're sending JSON
    password = request.json.get('password')
    role = request.json.get('role')

    if username in users and users[username] == password:
        session['client_id'] = username  # Use the username as the client ID
        session['session_id'] = str(uuid.uuid4())  # Generate a session ID
        return jsonify({"message": "Login successful"}), 200  # Return success message in JSON
    else:
        return jsonify({"message": "Login failed. Please check your credentials and try again."}), 401  # Return JSON error
    
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



@app.route('/view-transporters')
def view_transporters():
    return render_template('transporterslist.html')



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


documents_data = [
    {
        'title': 'CROSS COUNTRY',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
    {
        'title': 'CARGO CONNECT',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
    {
        'title': 'TENGWA',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
]

@app.route('/shipper_documents')
def shipper_documents():
    return render_template('shipperdocs.html', documents=documents_data)


@app.route('/shipper_chat')
def shipper_chat():
    
    messages = [
        {'text': 'Hello, how can I help you?', 'type': 'incoming'},
        {'text': 'I need information about the loads.', 'type': 'outgoing'},
        {'text': 'Sure! Here are the details.', 'type': 'incoming'},
    ]
    return render_template('shipperchat.html', messages=messages)




if __name__ == '__main__':
    app.run(debug = True, port=8000)



