from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from config import SERVICENOW_URL, USERNAME, PASSWORD, HEADERS

app = Flask(__name__)
CORS(app)

# Fetch all incidents
@app.route("/incidents", methods=["GET"])
def get_all_incidents():
    response = requests.get(SERVICENOW_URL, auth=(USERNAME, PASSWORD), headers=HEADERS)
    if response.status_code == 200:
        return jsonify({"result": response.json().get("result", [])}), 200
    return jsonify({"error": "Failed to fetch incidents"}), response.status_code

# Fetch a single/multiple incidents
@app.route("/incidents/<sys_ids>", methods=["GET"])
def get_incident(sys_ids):
    sys_id_list = sys_ids.split(",")  
    incidents = []

    for sys_id in sys_id_list:
        response = requests.get(f"{SERVICENOW_URL}/{sys_id.strip()}", auth=(USERNAME, PASSWORD), headers=HEADERS)
        if response.status_code == 200:
            incidents.append(response.json().get("result", {}))

    if incidents:
        return jsonify({"result": incidents}), 200
    return jsonify({"error": "No incidents found"}), 404

# Create an Incident (FIXED FIELD UPDATING)
@app.route("/incidents", methods=["POST"])
def create_incident():
    data = request.json
    required_fields = ["short_description", "caller_id", "priority", "state", "category", "assignment_group", "assigned_to"]

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    payload = {
        "short_description": data["short_description"],
        "caller_id": data["caller_id"],
        "priority": str(data["priority"]),
        "state": data["state"],
        "category": data["category"],
        "assignment_group": data["assignment_group"],
        "assigned_to": data["assigned_to"]
    }

    response = requests.post(SERVICENOW_URL, auth=(USERNAME, PASSWORD), headers=HEADERS, json=payload)
    
    if response.status_code == 201:
        return jsonify({"message": "Incident created successfully", "incident": response.json().get("result")}), 201
    return jsonify({"error": "Failed to create incident", "details": response.text}), response.status_code

# Update an Incident
@app.route("/incidents/<sys_id>", methods=["PUT"])
def update_incident(sys_id):
    data = request.json
    response = requests.put(f"{SERVICENOW_URL}/{sys_id}", auth=(USERNAME, PASSWORD), headers=HEADERS, json=data)
    
    if response.status_code == 200:
        return jsonify({"message": f"Incident {sys_id} updated successfully"}), 200
    return jsonify({"error": "Failed to update incident", "details": response.text}), response.status_code

# Delete an Incident
@app.route("/incidents/<sys_id>", methods=["DELETE"])
def delete_incident(sys_id):
    response = requests.delete(f"{SERVICENOW_URL}/{sys_id}", auth=(USERNAME, PASSWORD), headers=HEADERS)
    
    if response.status_code in [200, 204]:
        return jsonify({"message": "Incident deleted successfully"}), 200
    return jsonify({"error": "Failed to delete incident"}), response.status_code

if __name__ == "__main__":
    app.run(debug=True)
