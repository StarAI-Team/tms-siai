from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
import uuid

app = Flask(__name__)

# Configuring the MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/SiAi_database"
mongo = PyMongo(app)

# Example collections for storing requests in MongoDB
waiting_collection = mongo.db.waiting
ongoing_collection = mongo.db.ongoing
completed_collection = mongo.db.completed

@app.route("/transporterapp")
def transporter_app():
    transporter_id = request.args.get("id")
    
    if not transporter_id:
        return jsonify({"error": "Transporter ID is required"}), 400

    # Fetch waiting, ongoing, and completed loads for the transporter
    waiting_requests = list(waiting_collection.find())
    ongoing_requests = list(ongoing_collection.find({"transporter_id": transporter_id}))
    completed_requests = list(completed_collection.find({"transporter_id": transporter_id}))

    if not ongoing_requests and not completed_requests:
        return jsonify({"error": f"Transporter ID {transporter_id} does not exist"}), 404
    
    return jsonify({
        "transporter_id": transporter_id,
        "waiting_requests": dumps(waiting_requests),
        "ongoing_requests": dumps(ongoing_requests),
        "completed_requests": dumps(completed_requests)
    })

# Endpoint to add a new request
@app.route("/add_request", methods=["POST"])
def add_request():
    data = request.json
    request_id = str(uuid.uuid4())  # Generate a random unique ID
    
    new_request = {
        "id": request_id,
        "goods": data.get("goods"),
        "quantity": data.get("quantity"),
        "pickup_place_and_time": data.get("pickup_place_and_time"),
        "destination": data.get("destination"),
        "rate": data.get("rate")
    }
    
    waiting_collection.insert_one(new_request)  # Insert into the 'waiting' collection
    
    return jsonify({"message": f"Request {request_id} added successfully"}), 201

# Accept load function that transfers from waiting to ongoing
@app.route("/accept_load/<string:load_id>")
def accept_load(load_id):
    transporter_id = "1"  # Replace with actual logic to get the transporter ID
    load = waiting_collection.find_one({"id": load_id})

    if load:
        waiting_collection.delete_one({"id": load_id})
        load["transporter_id"] = transporter_id
        ongoing_collection.insert_one(load)
        return jsonify({"message": f"Load {load_id} accepted by transporter {transporter_id}"})
    
    return jsonify({"error": f"Load {load_id} not found"}), 404

# Complete load function
@app.route("/complete_load/<string:load_id>")
def complete_load(load_id):
    transporter_id = "1"  # Replace with actual logic to get the transporter ID
    load = ongoing_collection.find_one({"id": load_id, "transporter_id": transporter_id})

    if load:
        ongoing_collection.delete_one({"id": load_id})
        completed_collection.insert_one(load)
        return jsonify({"message": f"Load {load_id} marked as completed"})
    
    return jsonify({"error": f"Load {load_id} not found in ongoing"}), 404

if __name__ == "__main__":
    app.run(debug=True)
