from flask import Flask, render_template, jsonify
app = Flask(__name__)

# Sample data for loads
trip = [
    {
        'id': 1,
        'load': 'Wheat',
        'quantity': '2 Tonnes',
        'route': 'Harare RoadPort 08:00am - Beira',
        'truck_type': '10 Tankers',
        'payment_days': '60 Days Cash',
        'amount': '$1400'
    },
]

@app.route('/agreement')
def index():
    return render_template('agreement.html', trip=trip)

# To retrieve loads via API
@app.route('/api/trip')
def get_trip():
    return jsonify(trip)

if __name__ == '__main__':
    app.run(debug=True, port='8010')