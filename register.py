from flask import Flask, request, jsonify, render_template
""" from kafka import KafkaProducer """
import json
import requests
import os


app = Flask(__name__)
#producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))


@app.route('/')
def home():
    return render_template ('transport_register.html')
    

@app.route('/transport_register', methods=['POST'])
def post_load():
    """ getting JSON data from request body"""
    transporter_data = request.form

    #fields that are required for the transporter to register 
    required_fields = [
        'first_name', 'last_name', 'date_of_birth', 'phone_number', 'id_number',
        'company_name', 'bank_name', 'account_name', 'account_number', 
        'location', 'company_contact', 'directorship', 'proof_of_current_address',
        'tax_clearance', 'certificate_of_incorporation', 'permits', 'operators_licence',
        'tracking_licence', 'number_of_trucks', 'num_of_trucks', 'reg_books', 'certificate_of_fitness',
        'truck_list_excel', 'profile_picture', 'password', 'confirm_password', 
    ]

    #Ensuring all required fields are present
    missing_fields = [field for field in required_fields if field not in transporter_data]
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

    # return the load data as a response
    return jsonify({"message": "register details received", "transporter":transporter_data}), 200

if __name__ == '__main__':
    app.run(debug = True)
