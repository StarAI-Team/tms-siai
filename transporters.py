from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock data to represent loads in different statuses
loads = {
    "waiting": [
        {"id": 1, "goods": "Wheat", "quantity": "2 tonnes", "pickup_place_and_time": "RoadPort Beira 8am","destination": "Harare", "rate": 500},
        {"id": 2, "goods": "Chrome", "quantity": "5 tonnes", "pickup_place_and_time": "RoadPort Byo 10am","destination": "Beira", "rate": 1000},
    ],
    "ongoing": {
        "transporter_1": [
            {"id": 3, "goods": "cotton", "quantity": "8 tonnes", "pickup_place_and_time": "Gweru RoadPort 5am","destination": "Kadoma", "rate": 750}
        ],
        "transporter_2": [
            {"id": 4, "goods": "maize", "quantity": "2 tonnes", "pickup_place_and_time": "RoadPort 3am", "destination": "Hwange", "rate": 300}
        ]
    },
    "completed": {
        "transporter_1": [
            {"id": 5, "goods": "coal", "quantity": "200 tonnes", "pickup_place_and_time": "RoadPort Hwange 6am","destination": "Karoi", "rate": 1500}
        ]
    }
}

@app.route("/transporterapp")
def transporter_app():
    transporter_id = request.args.get("id")
    
    if not transporter_id:
        return jsonify({"error": "Transporter ID is required"}), 400

    # Fetch waiting, ongoing, and completed loads for the transporter
    waiting_requests = loads["waiting"]
    ongoing_requests = loads["ongoing"].get(f"transporter_{transporter_id}", [])
    completed_requests = loads["completed"].get(f"transporter_{transporter_id}", [])

    if not ongoing_requests and not completed_requests:
        return jsonify({"error": f"Transporter ID {transporter_id} does not exist"}), 404
    
     # Fetch waiting requests (shown for all transporters)
    waiting_requests = loads["waiting"]
    
    # Return data as JSON for testing purposes
    return jsonify({
        "transporter_id": transporter_id,
        "waiting_requests": waiting_requests,
        "ongoing_requests": ongoing_requests,
        "completed_requests": completed_requests
    })

@app.route("/accept_load/<int:load_id>")
def accept_load(load_id):
    transporter_id = "1"
    for load in loads["waiting"]:
        if load["id"] == load_id:
            loads["waiting"].remove(load)
            loads["ongoing"].setdefault(f"transporter_{transporter_id}", []).append(load)
            return jsonify({"message": f"Load {load_id} accepted by transporter {transporter_id}"})
    return jsonify({"error": f"Load {load_id} not found"}), 404

@app.route("/complete_load/<int:load_id>")
def complete_load(load_id):
    transporter_id = "1"
    for load in loads["ongoing"].get(f"transporter_{transporter_id}", []):
        if load["id"] == load_id:
            loads["ongoing"][f"transporter_{transporter_id}"].remove(load)
            loads["completed"].setdefault(f"transporter_{transporter_id}", []).append(load)
            return jsonify({"message": f"Load {load_id} marked as completed"})
    return jsonify({"error": f"Load {load_id} not found in ongoing"}), 404

if __name__ == "__main__":
    app.run(debug=True)
