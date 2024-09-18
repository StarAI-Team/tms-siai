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
    return render_template ('transport_register.html')
    

@app.route('/register_transporter', methods=['POST'])
def register_transporter():
    transporter_data = request.form.to_dict()  # Form data

    #files that are required for the transporter to register 
    file_fields = [
        'directorship', 'certificate_of_incorporation', 'proof_of_current_address', 'tax_clearance','operators_licence',
        'permits', 'tracking_licence', 'num_of_trucks', 'reg_books', 'certificate_of_fitness',
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

    transporter_data.update(file_data)

     # Password validation and hashing
    password = transporter_data.get('password')
    confirm_password = transporter_data.pop('confirm_password')

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    hashed_password = generate_password_hash(password)
    transporter_data['password'] = hashed_password
    


    #Ensuring all required fields are present
    required_fields = [
        'first_name', 'last_name', 'date_of_birth', 'phone_number', 'id_number',
        'company_name', 'bank_name', 'account_name', 'account_number', 
        'company_location', 'company_email', 'company_contact', 'bank_name', 'account_name', 'account_number',
        'directorship_text', 'proof_of_current_address_text', 
        'tax_clearance_text', 'certificate_of_incorporation_text',
        'operators_licence_text', 'operators_expiry', 'permits_text', 'permit_expiry',
        'tracking_licence_text', 'number_of_trucks', 'num_of_trucks_text',
        'reg_books', 'reg_books_text', 'certificate_of_fitness_text',
        'user_name', 'password' 
        
    ] + file_fields


    missing_fields = [field for field in required_fields if field not in transporter_data and field not in request.files]
    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    
    # Generating  a unique user ID
    user_id = str(uuid.uuid4())

    # Adding user_id and event_name to the data
    transporter_data['user_id'] = user_id
    transporter_data['event_name'] = 'transporterRegistration'
  

    
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
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Transporter registered successfully"}), 200




if __name__ == '__main__':
    app.run(debug = True, port=8000)



