from flask import Flask, request, jsonify, render_template
""" from kafka import KafkaProducer """
import json
import requests


app = Flask(__name__)
#producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))


@app.route('/')
def home():
    return render_template ('load.html')
    

@app.route('/Post_load', methods=['POST'])
def post_load():
    """ getting JSON data from request body"""
    load_data = request.form

    #fields that are required for the form to post load
    required_fields = [
        'load_name', 'quantity', 'pickup_time', 'pickup_place', 'destination',
        'clearing_agency', 'clearing_agency_contact', 'number_of_trucks', 'truck_type',
        'payment_days', 'payment_method', 'proof_of_delivery_requirements', 'delivery_duration',
        'additional_instructions', 'recommended_price' 
    ]

    #Ensuring all required fields are present
    missing_fields = [field for field in required_fields if field not in load_data]
    if missing_fields:
        return jsonify({"error": "Missing fields", "fields": missing_fields}), 400
    
    # Send the data to the processing Flask application
    # endpoint of the kafka server
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        response = requests.post(
            PROCESSING_FLASK_URL,
            json=load_data,
            headers={'Content-Type': 'application/json'}
        )
        response_data = response.json()
        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    # return the load data as a response
    return jsonify({"message": "Load details received", "load":load_data}), 200

if __name__ == '__main__':
    app.run(debug = True)
