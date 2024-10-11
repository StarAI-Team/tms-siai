from flask import Flask, render_template, jsonify, request
import psycopg2
import json
import os
import requests
import uuid


app = Flask(__name__)

# Route for the main SPA page

@app.route('/get_user_metadata', methods=['GET'])
def get_user_metadata():

    ip_address = request.remote_addr  
    
    metadata = {
        'ip_address': ip_address
    }
    return jsonify(metadata)

@app.route('/')
def home():
    # Placeholder data to simulate data from the backend
    manage_users = [
        {'name': 'STAR', 'type': 'Transporter', 'red_flag': True},
        {'name': 'JJ', 'type': 'Shipper', 'red_flag': True},
        {'name': 'ABC', 'type': 'Transporter', 'red_flag': True}
    ]
    
    loads = [
        {'load_id': 101, 'route': 'A to B', 'rate': 1200, 'status': 'Completed', 'transporter': 'Transporter A', 'shipper': 'Shipper X'},
        {'load_id': 102, 'route': 'B to C', 'rate': 1500, 'status': 'In Progress', 'transporter': 'Transporter B', 'shipper': 'Shipper Y'}
    ]

    load_history = [
        {'load_id': 101, 'route': 'A to B', 'rate': 1200, 'transporter': 'Transporter A', 'shipper': 'Shipper X'},
        {'load_id': 102, 'route': 'B to C', 'rate': 1500, 'transporter': 'Transporter B', 'shipper': 'Shipper Y'}
    ]

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

    conn = create_connection()
    with conn.cursor() as cur:
        query = """
                    SELECT 
                            t.company_name,
                            t.company_location AS address,
                            tf.number_of_trucks,
                            json_agg(file) AS files
                        FROM 
                            transporter t
                        JOIN 
                            transporter_fleet tf ON t.user_id = tf.user_id
                        JOIN (
                            SELECT 
                                user_id,
                                json_build_object('file', certificate_of_incorporation) AS file
                            FROM 
                                transporter_documentation
                            UNION ALL
                            SELECT 
                                user_id,
                                json_build_object('file', operators_licence) AS file
                            FROM 
                                transporter_documentation
                            UNION ALL
                            SELECT 
                                user_id,
                                json_build_object('file', permits) AS file
                            FROM 
                                transporter_documentation
                            UNION ALL
                            SELECT 
                                user_id,
                                json_build_object('file', tax_clearance) AS file
                            FROM 
                                transporter_documentation
                        ) AS td ON t.user_id = td.user_id
                        GROUP BY 
                            t.company_name, t.company_location, tf.number_of_trucks;
                """

        # Execute the insert with all values
        cur.execute(query)

        # Fetch all results
        results = cur.fetchall()
        print(results)
    # Format the results into a list of dictionaries
    data = []
    for row in results:
        company_info = {
            'company_name': row[0],
            'address': row[1],
            'number_of_trucks': row[2],
            'files': [file['file'] for file in row[3]]
        }
        data.append(company_info)

    # Print the results before modification
    print("Before modification:", data[0])

    # Replace 'minio' with 'localhost' in the dictionary
    for record in data:
        # Replace the values in the record dictionary
        for key in record:
            if isinstance(record[key], str):
                record[key] = record[key].replace('minio', 'localhost')
        
        # Update the 'files' list specifically in the dictionary
        record['files'] = [url.replace('minio', 'localhost') for url in record['files']]

    # Print the results after modification
    print("After modification:", data[0])

    # Store the modified data in submission
    submission = data

    print(f">>>> {submission}")
    # Clean up
    cur.close()
    conn.close()


    user_details = {
        'name': 'John Doe',
        'load_history': '10 completed loads',
        'ranking': 5
    }
    
    # Passing placeholder data to Jinja templates
    return render_template('admin.html', 
        manage_users=manage_users,  
        users=manage_users,         
        load_history=load_history,  
        loads=loads,
        submission=submission,  
        user_details=user_details)

# API Route to handle user actions
@app.route('/suspend/<username>', methods=['POST'])
def suspend_user(username):
    # Logic to suspend user
    return jsonify({'message': f'User {username} suspended successfully!'})

@app.route('/deregister/<username>', methods=['POST'])
def deregister_user(username):
    # Logic to deregister user
    return jsonify({'message': f'User {username} deregistered successfully!'})

@app.route('/activate/<username>', methods=['POST'])
def activate_user(username):
    # Logic to activate user
    return jsonify({'message': f'User {username} activated successfully!'})

@app.route('/submit')
def submissions():
    submission = {
        "company_name": "Star International Trucks",
        "address": "97 WILLOWVALE HARARE",
        "number_of_trucks": 20,
        "files": [
            "images.png",
            "Tax Clearance.pdf",
            "Directorship.pdf",
            "Proof of Residence.pdf",
            "Vehicle Registration.pdf",
            "GIT.pdf",
            "Tracking.pdf"
        ]
    }

    return render_template('submit.html', submission=submission)

@app.route('/user_submission', methods=['POST'])
def user_submission():
    # Check if request is JSON
    if request.is_json:
        payload = request.get_json()
    else:
        return jsonify({"error": "Invalid content type"}), 400

    # Debug: Print incoming JSON payload
    print("Incoming JSON Payload:", payload)

    # Extract data from the payload
    request_data = {
        **{key: payload[key] for key in payload if key not in ['form_data']},
        **{key: payload['form_data'][key] for key in payload['form_data']}
    }

    print("Processed Request Data:", request_data)

    # Send the data to the processing Flask application
    PROCESSING_FLASK_URL = 'http://localhost:6000/process_user'
    try:
        # Debug: Print request_data before sending
        print("Sending the following data to processing URL:", request_data)

        response = requests.post(
            PROCESSING_FLASK_URL,
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )

        # Debug: Print response status and data
        response_data = response.json()
        print("Response status code:", response.status_code)
        print("Response data:", response_data)

        return jsonify(response_data), response.status_code
    except requests.exceptions.RequestException as e:
        print("Error occurred while sending to processing URL:", e)
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Data submitted successfully"}), 200



if __name__ == '__main__':
    app.run(debug=True, port=8009)
