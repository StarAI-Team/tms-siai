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

documents_data = [
    {
        'title': 'CROSS COUNTRY',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
    {
        'title': 'CARGO CONNECT',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
    {
        'title': 'TENGWA',
        'files': [
            {'name': 'Agreement.pdf', 'url': '/files/agreement.pdf'},
            {'name': 'Invoice.pdf', 'url': '/files/invoice.pdf'},
            {'name': 'P_O_D_scan.pdf', 'url': '/files/p_o_d_scan.pdf'},
        ]
    },
]

@app.route('/documents')
def documents():
    return render_template('docs.html', documents=documents_data)

@app.route('/chat')
def chat():
    # Example chat messages - replace with your data source
    messages = [
        {'text': 'Hello, how can I help you?', 'type': 'incoming'},
        {'text': 'I need information about the loads.', 'type': 'outgoing'},
        {'text': 'Sure! Here are the details.', 'type': 'incoming'},
    ]
    return render_template('chat.html', messages=messages)

@app.route('/analytics')
def analytics():
    # Placeholder for analytics data
    return render_template('analytics.html')

# Example route to fetch real-time data for charts (replace with your logic)
@app.route('/api/analytics-data')
def analytics_data():
    # Replace this with actual logic to gather data for your analytics
    return jsonify({
        'labels': ['January', 'February', 'March', 'April', 'May'],
        'data': [12, 19, 3, 5, 2],
    })


if __name__ == "__main__":
    app.run(debug=True, port='8008')
