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

    
    # Database connection parameters
    # Initialize PostgreSQL connection
def create_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host='localhost',
        port='5433'
    )
    return conn

@app.route('/')
def home():
    conn = create_connection()
    with conn.cursor() as cur:
        # Query to fetch transporter data
        transporter_query = """
            SELECT 
                t.user_id,
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
            WHERE 
                t.registration_status = 'pending'  
            GROUP BY 
                t.user_id, t.company_name, t.company_location, tf.number_of_trucks;
        """

        # Execute the transporter query
        cur.execute(transporter_query)

        # Fetch all results
        results = cur.fetchall()
        print("RESULT FROM POSTGRE", results)

        # Format the results into a list of dictionaries
        data = []
        for row in results:
            company_info = {
                'user_id': row[0],
                'company_name': row[1],
                'address': row[2],
                'number_of_trucks': row[3],
                'files': [file['file'] for file in row[4]]
            }
            data.append(company_info)

        # Replace 'minio' with 'localhost' in the dictionary
        for record in data:
            # Replace the values in the record dictionary
            for key in record:
                if isinstance(record[key], str):
                    record[key] = record[key].replace('minio', 'localhost')

            # Update the 'files' list specifically in the dictionary
            record['files'] = [url.replace('minio', 'localhost') for url in record['files']]

        # Query to fetch shipper data
        shipper_query = """
            SELECT 
                s.user_id,
                s.company_name,
                s.company_location AS address,
                json_agg(file) AS files
            FROM 
                shipper s
            LEFT JOIN (
                SELECT 
                    user_id,
                    json_build_object('file', certificate_of_incorporation) AS file
                FROM 
                    shipper_documentation
                UNION ALL
                SELECT 
                    user_id,
                    json_build_object('file', tax_clearance) AS file
                FROM 
                    shipper_documentation
            ) AS td ON s.user_id = td.user_id  -- Fixed this line
             WHERE 
                s.registration_status = 'pending'  -- Only fetch shippers with pending status
            GROUP BY 
                s.user_id, s.company_name, s.company_location;
        """

        # Execute the shipper query
        cur.execute(shipper_query)

        # Fetch all results for shippers
        shipper_results = cur.fetchall()
        print("RESULT FROM POSTGRE (Shippers)", shipper_results)

        # Format the results into a list of dictionaries
        shipper_data = []
        for row in shipper_results:
            company_info = {
                'user_id': row[0],
                'company_name': row[1],
                'address': row[2],
                'files': [file['file'] for file in row[3] if file is not None] if row[3] else []
 
            }
            shipper_data.append(company_info)

        # Replace 'minio' with 'localhost' in the dictionary for shippers
        for record in shipper_data:
            for key in record:
                if isinstance(record[key], str):
                    record[key] = record[key].replace('minio', 'localhost')

            record['files'] = [url.replace('minio', 'localhost') for url in record['files']]

    # Combine both transporter and shipper data for submission
    submissions = {
        'transporters': data,
        'shippers': shipper_data
    }

    print(f">>>> Submissions: {submissions}")

    # Clean up
    conn.close()

    user_details = {
        'name': 'John Doe',
        'load_history': '10 completed loads',
        'ranking': 5
    }

    # Passing placeholder data to Jinja templates
    return render_template('admin.html', user_details=user_details, submissions=submissions)


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
    # Retrieve the data from the query parameters
    user_id = request.args.get('user_id')
    company_name = request.args.get('company_name')
    address = request.args.get('address')
    number_of_trucks = request.args.get('number_of_trucks')
    files = request.args.getlist('files')

    # Prepare the submission object
    submissions = {
        'user_id': user_id,
        'company_name': company_name,
        'address': address,
        'number_of_trucks': number_of_trucks,
        'files': files
    }

    # Render the 'submit.html' page with the submission details
    return render_template('submit.html', submissions=submissions)


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
