from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PENDING_ENTRIES_PATH = os.path.join(BASE_DIR, "pending_entries.json")

@app.route("/")
def home():
    return "Render Webhook is live."

@app.route("/update_pending", methods=["POST"])
def update_pending():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload received."}), 400

        if os.path.exists(PENDING_ENTRIES_PATH):
            with open(PENDING_ENTRIES_PATH, "r") as f:
                entries = json.load(f)
        else:
            entries = []

        entries.append(data)

        with open(PENDING_ENTRIES_PATH, "w") as f:
            json.dump(entries, f, indent=2)

        return jsonify({"status": "Polymer added via webhook"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
