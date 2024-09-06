from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

# Google Sheets Updater class
class GoogleSheetUpdater:
    def __init__(self, service_account_file, document_id, sheet_index=0):
        self.service_account_file = service_account_file
        self.document_id = document_id
        self.sheet_index = sheet_index
        self.gc = self._authorize_client()
        self.worksheet = self._open_worksheet()

    def _authorize_client(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        return gspread.authorize(credentials)

    def _open_worksheet(self):
        spreadsheet = self.gc.open_by_key(self.document_id)
        return spreadsheet.get_worksheet(self.sheet_index)

    def get_dataframe(self):
        records = self.worksheet.get_all_records()
        return pd.DataFrame(records)

# Usage
SERVICE_ACCOUNT_FILE = './data-extraction-tool-433301-f79d60b07ff8.json'
DOCUMENT_ID = '1h2dNYqfsyHtwv-E7Q2tUvrBRQnzXYjjrLPR_ogPuG0c'

updater = GoogleSheetUpdater(SERVICE_ACCOUNT_FILE, DOCUMENT_ID)

# Route to fetch all transporters data as JSON
@app.route('/fetch_transporters', methods=['GET'])
def fetch_transporters():
    try:
        df = updater.get_dataframe()  # Fetch updated data from Google Sheets
        
        # Convert the DataFrame to a list of dictionaries
        transporters = df.to_dict(orient="records")

        # Return the data as JSON
        return jsonify(transporters)
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 500

# Route to fetch and display all transporters
@app.route('/transporters', methods=['GET'])
def transporters():
    try:
        df = updater.get_dataframe()  # Fetch updated data from Google Sheets
        search_query = request.args.get('search', '')

        # Filter the data if a search query is provided
        if search_query:
            df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]

        # Convert to dictionary for rendering in the template
        transporters = df.to_dict(orient="records")
        
        # Fetch favorites from the session
        favorite_ids = session.get('favorites', [])

        return render_template('transporterslist.html', transporters=transporters, favorites=favorite_ids, search_query=search_query)
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 500

# Route to add/remove favorites
@app.route('/favorite/<int:transporter_id>', methods=['POST'])
def favorite(transporter_id):
    favorites = session.get('favorites', [])
    
    if transporter_id in favorites:
        favorites.remove(transporter_id)
    else:
        favorites.append(transporter_id)
    
    session['favorites'] = favorites
    return redirect(url_for('transporters'))

# Route to view favorites
@app.route('/favorites', methods=['GET'])
def view_favorites():
    try:
        df = updater.get_dataframe()  # Fetch updated data from Google Sheets
        favorite_ids = session.get('favorites', [])
        
        # Filter only the favorites
        favorites = df[df['ID'].isin(favorite_ids)].to_dict(orient="records")

        return render_template('favorites.html', transporters=favorites)
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/logout')
def logout():
    # Clear the session data, effectively logging out the user
    session.clear()
    # Redirect the user to the login page or any other desired page
    return redirect(url_for('login'))

# Assume you have a login route already defined
@app.route('/login')
def login():
    # Your login logic here
    return "Login Page"

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
