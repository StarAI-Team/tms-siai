from flask import Flask, render_template

app = Flask(__name__)

@app.route('/bid')
def bid():
    # Example data 
    loads = [
        {
            'load_name': 'Pelcravía',
            'stars': '★★★★★',
            'price': '1200',
            'route': 'Wheat Harare - Beira',
            'status': 'Premium Member',
            'perfect_match': True
        },
        {
            'load_name': 'Ngwena',
            'stars': '★★★★☆',
            'price': '1100',
            'route': 'Harare - Lusaka',
            'status': 'Standard Member',
            'perfect_match': False
        },
        {
            'load_name': 'Nestle',
            'stars': '★★★★★',
            'price': '1250',
            'route': 'Harare - Gaborone',
            'status': 'Premium Member',
            'perfect_match': False
        },
    ]
    
    return render_template('allbid.html', loads=loads)


@app.route('/place_bid')
def auction():
    return render_template('bid.html')


@app.route('/place_bid/<string:load_name>')
def place_bid(load_name):

    load_data = {
        'Pelcravía': {'route': 'Wheat Harare - Beira', 'quantity': '2 Tonnes', 'rate': '1200', 'perfect_match':True},
        'Ngwena': {'route': 'Harare - Lusaka', 'quantity': '3 Tonnes', 'rate': '1100', 'perfect_match':False},
        'Nestle': {'route': 'Harare - Gaborone', 'quantity': '1.5 Tonnes', 'rate': '1250', 'perfect_match':False}
    }

    # Fetch the load details dynamically
    load_details = load_data.get(load_name)

    if load_details:
        return render_template('bid.html', load_name=load_name, route=load_details['route'], quantity=load_details['quantity'], rate=load_details['rate'], perfect_match=load_details['perfect_match'])
    else:
        return "Load not found", 404


if __name__ == "__main__":
    app.run(debug=True, port='8005')
