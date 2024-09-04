from flask import Flask, render_template, redirect, url_for, request, session,flash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password
    
class transporters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caller_name = db.Column(db.String(100))
    call_time = db.Column(db.String(100))
    summary = db.Column(db.Text)
    rate_accepted = db.Column(db.Boolean, default=False)  # New field
    notes = db.Column(db.String(255))  # New field

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')

    # Initialize the database
    db.init_app(app)

    # Home route
    @app.route('/')
    def home():
        return render_template('home.html')

    # Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
        
            user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            transporter = transporters.query.all()
            return render_template('logs.html', transporter=transporters )
        else:
            flash('Invalid username or password')

    return render_template('home.html')

    # Register route
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            # Handle registration logic here (e.g., form validation, saving to database)
            return redirect(url_for('home'))
        return render_template('register.html')

    # Additional routes can go here

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
