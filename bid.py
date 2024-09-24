from flask import Flask, request, jsonify, render_template, url_for


app = Flask(__name__)

@app.route('/')
def auction():
    return render_template('bid.html')

@app.route('/bid')
def bid():
    return render_template('allbid.html')


if __name__ == '__main__':
    app.run(debug = True, port=8005)