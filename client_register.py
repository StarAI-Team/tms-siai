from flask import Flask, request, jsonify, render_template
import json
import requests
import os
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

@app.route('/')
def home():
    return render_template ('client_register.html')
    

@app.route('/client_register', methods=['POST'])
def register_transporter():
    transporter_data = request.form.to_dict()  # Form data

    #fields that are required for the transporter to register 
    file_fields = [
         'directorship', 'proof_of_current_address', 'tax_clearance', 'certificate_of_incorporation', 'id_number',
        'profile_picture'
        
    ]

    # Handling file uploads
    file_data = {}
    for file_field in file_fields:
        if file_field in request.files:
            file = request.files[file_field]
            if file:
                file_path = os.path.join('uploads', file.filename)  # Placeholder for where uploads are going to be saved
                file.save(file_path)
                file_data[file_field] = file_path

    transporter_data.update(file_data)

     # Password validation and hashing
    password = transporter_data.get('password')
    confirm_password = transporter_data.get('confirm_password')

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    hashed_password = generate_password_hash(password)
    transporter_data['password'] = hashed_password
    transporter_data.pop('confirm_password')


    #Ensuring all required fields are present
    required_fields = [
        'first_name', 'last_name', 'date_of_birth', 'phone_number', 'id_number',
        'company_name', 'bank_name', 'account_name', 'account_number', 
        'location', 'company_email', 'company_contact', 'bank_name', 'account_name', 'account_number',
        'directorship_text', 'proof_of_current_address_text',
        'tax_clearance_text', 'certificate_of_incorporation_text',
        'user_name', 'password', 'confirm_password', 
       

    ] + file_fields


    missing_fields = [field for field in required_fields if field not in transporter_data and field not in request.files]
    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    

    
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

if __name__ == '__main__':
    app.run(debug = True, port=5001)



