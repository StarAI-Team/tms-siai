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

@app.route('/transporter-package')
def transporter_package():
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
        payload = request.get_json()  
    else:
        return jsonify({"error": "Invalid content type"}), 400
    
    # Debug: Print incoming JSON payload
    print("Incoming JSON Payload:", payload)
    transporter_data = {
        **{key: payload[key] for key in payload if key not in ['form_data']} ,
        **{key: payload['form_data'][key] for key in payload['form_data']}
    } 
    print("TRANSPORTER DATA", transporter_data)


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
        if file_field in request.files:
            file = request.files[file_field]
            if file:
                # Create a secure filename and store it in the uploads folder
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)  # Save the file to the disk

                # Generate URI to access this file
                file_uri = url_for('uploaded_file', filename=unique_filename, _external=True)
                file_data[file_field] = file_uri

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


if __name__ == '__main__':
    app.run(debug = True, port=8000)



