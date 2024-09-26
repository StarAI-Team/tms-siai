from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Route for the main SPA page
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

    submission = {
        'company_name': 'Transport Co.',
        'address': '123 Main St.',
        'number_of_trucks': 10,
        'files': ['regbook.pdf', 'cert_fitness.pdf']
    }
    
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


if __name__ == '__main__':
    app.run(debug=True, port=8009)
