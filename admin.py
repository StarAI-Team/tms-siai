from flask import Flask, request, jsonify, render_template, url_for


app = Flask(__name__)

@app.route('/')
def client_submissions():
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

    return render_template('admin_submission.html', submission=submission)


if __name__ == '__main__':
    app.run(debug = True, port=8009)