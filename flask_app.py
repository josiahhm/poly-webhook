from flask import Flask, request, jsonify
import json
import os
from openai import OpenAI, OpenAIError

app = Flask(__name__)

# Initialize OpenAI client (will fail safely if env var not set)
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
client = OpenAI(api_key=api_key)

PENDING_FILE = "pending_entries.json"

@app.route('/')
def index():
    return "PolyTherm Flask App is running."

@app.route('/update_pending', methods=['POST'])
def update_pending():
    try:
        # Parse JSON from request
        data = request.get_json(force=True)
        if not data or "name" not in data:
            return jsonify({"error": "Missing 'name' field in request JSON"}), 400

        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Polymer name cannot be empty"}), 400

        # Read existing file or initialize
        if os.path.exists(PENDING_FILE):
            with open(PENDING_FILE, "r") as f:
                try:
                    entries = json.load(f)
                except json.JSONDecodeError:
                    entries = []
        else:
            entries = []

        # Append new entry
        entries.append({"name": name, "status": "pending"})

        # Write updated file
        with open(PENDING_FILE, "w") as f:
            json.dump(entries, f, indent=2)

        return jsonify({"status": "success", "message": f"Polymer '{name}' added to pending entries."})

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
