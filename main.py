from random import randint
from flask import (
    Flask,
    render_template, 
    jsonify, 
    request
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    return render_template('login.html')

if __name__ == "__main__":
    app.run()