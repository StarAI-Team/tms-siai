from flask import Flask, request, jsonify, render_template, url_for
import json
import requests
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask_cors import CORS




app = Flask(__name__)
CORS(app) 

#upload folder path
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve the file from the file system """
    return f"File can be accessed at: /uploads/{filename}"

@app.route('/')
def home():
    return render_template ('register.html')

@app.route('/transport-package')
def transport_package():
    return render_template ('transport_package.html')

@app.route('/transporter_package_selected')
def transporter_package_selected():
    return render_template ('transporter_payment_package.html')

@app.route('/transporter_pay')
def transporter_pay():
    return render_template ('transporter_paying.html')


@app.route('/welcome-transporter')
def welcome_transporter():
    return render_template ('transport_register.html')

    
@app.route('/get_user_metadata', methods=['GET'])
def get_user_metadata():
    user_id = str(uuid.uuid4())  
    ip_address = request.remote_addr  
    
    metadata = {
        'user_id': user_id,
        'ip_address': ip_address
    }
    return jsonify(metadata)


@app.route('/register_transporter', methods=['POST'])
def register_transporter():
    if request.is_json:
        payload = request.get_json()  # Get the JSON payload
    else:
        return jsonify({"error": "Invalid content type"}), 400
    transporter_data = request.form.to_dict()
     # Debug: Print raw form data to check what is being sent
    print("Raw form data:", request.form)

    # Create transporter_data dictionary directly from the payload
    transporter_data = {
        'user_id': payload.get('user_id'),  # Get user_id from the payload
        'ip_address': payload.get('ip_address', request.remote_addr),  # Fallback to request's IP if not sent
        **{key: payload[key] for key in payload if key not in ['user_id', 'ip_address']}  # Include all other fields
    }

    print("Transporter data before processing:", transporter_data)

    # Get the current section from the form submission
    current_section = transporter_data.get('current_section')
   

    #files that are required for the transporter to register 
    file_fields = [
        'directorship', 'certificate_of_incorporation', 'proof_of_current_address', 'tax_clearance','operators_licence',
        'permits', 'tracking_licence', 'num_of_trucks', 'reg_books', 'certificate_of_fitness',
        'profile_picture',
        
    ]

     # Segregated required fields by sections (from the `requiredFields` in JavaScript)
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

    transporter_data.update(file_data)

     # Password validation
    password = transporter_data.get('password')
    confirm_password = transporter_data.get('confirm_password')  

    # Check if both password fields are present before comparing
    if password and confirm_password and password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Hash the password if it exists
    if password:
        hashed_password = generate_password_hash(password)
        transporter_data['password'] = hashed_password

    # Validate only the fields for the current section
    required_fields_for_section = required_fields_by_section.get(current_section, [])
    
     # Separate validation for regular form fields and file fields
    required_form_fields = [field for field in required_fields_for_section if field not in file_fields]
    required_file_fields = [field for field in required_fields_for_section if field in file_fields]

    # Check for missing regular form fields
    missing_form_fields = [field for field in required_form_fields if field not in transporter_data]
    
    # Check for missing file fields
    missing_file_fields = [field for field in required_file_fields if field not in request.files and field not in transporter_data]

    # Combine all missing fields
    missing_fields = missing_form_fields + missing_file_fields

    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    
    # Final payload to send to processing URL
    processing_payload = {
        **transporter_data  # This spreads all fields from transporter_data
    }

    processing_payload = transporter_data
    print("Final payload being sent to processing URL:", processing_payload)

    
    # Send the data to the processing Flask application
    # endpoint of the kafka server
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
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


@app.route('/client-package')
def client_package():
    return render_template ('client_package.html')


@app.route('/client_package_selected')
def client_package_selected():
    return render_template ('client_payment_package.html')

@app.route('/welcome-client')
def welcome_client():
    return render_template ('client_register.html')



@app.route('/client_register', methods=['POST'])
def client_register():
    client_data = request.form.to_dict()  # Form data

    #files that are required for the client to register 
    file_fields = [
        'directorship', 'certificate_of_incorporation', 'proof_of_current_address', 'tax_clearance',
        'profile_picture',
        
    ]

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

    client_data.update(file_data)

     # Password validation and hashing
    password = client_data.get('password')
    confirm_password = client_data.pop('confirm_password')

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    hashed_password = generate_password_hash(password)
    client_data['password'] = hashed_password
    


    #Ensuring all required fields are present
    required_fields = [
        'first_name', 'last_name', 'phone_number', 'id_number',
        'company_name', 'bank_name', 'account_name', 'account_number', 
        'company_location', 'company_email', 'company_contact', 'bank_name', 'account_name', 'account_number',
        'directorship_text', 'proof_of_current_address_text', 
        'tax_clearance_text', 'certificate_of_incorporation_text', 'user_name', 'password' 
        
    ] + file_fields


    missing_fields = [field for field in required_fields if field not in client_data and field not in request.files]
    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    
    # Generating  a unique user ID
    user_id = str(uuid.uuid4())

    # Adding user_id and event_name to the data
    client_data['user_id'] = user_id
    client_data['event_name'] = 'clientRegistration'
  

    
    # Send the data to the processing Flask application
    # endpoint of the kafka server
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=client_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "client registered successfully"}), 200




if __name__ == '__main__':
    app.run(debug = True, port=8000)



