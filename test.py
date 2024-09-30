from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)
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


@app.route('/')
def index():
    return render_template('loadpool.html')

@app.route('/api/loads')
def get_loads():
    return jsonify(loads_data)

@app.route('/requests')
def requests():
    return render_template('requests.html')



@app.route('/trucks')
def trucks():
    return render_template('trucks.html')



if __name__ == "__main__":
    app.run(debug=True, port='8008')
