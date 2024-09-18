from flask import Flask, request, jsonify, render_template, url_for
import json
import requests
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask_cors import CORS




app = Flask(__name__)
CORS(app) 



@app.route('/')
def home():
    return render_template ('register.html')
    


if __name__ == '__main__':
    app.run(debug = True, port=8090)
