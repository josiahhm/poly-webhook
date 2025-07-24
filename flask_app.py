from flask import Flask, request, jsonify
import os
import json
from openai import OpenAI

# Set up Flask app
app = Flask(__name__)

# OpenAI client setup
client = OpenAI(api_key="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")  # Replace with your actual API key

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PENDING_ENTRIES_PATH = os.path.join(BASE_DIR, "pending_entries.json")
LOG_PATH = os.path.join(BASE_DIR, "webhook_log.txt")

# Prompt template
PROMPT_TEMPLATE = """You are a polymer database assistant. For the polymer "{polymer_name}", return all of the following fields with real, sourced data:

Common Name
IUPAC Name
Modulus (GPa) + Source
Tensile Strength (MPa) + Source
Density (g/cm³) + Source
Dielectric Constant + Source
Biodegradable? + Source
Thermal Conductivity (W/m·K) + Source
Refractive Index + Source
Surface Energy (mJ/m²) + Source
Water Contact Angle (°) + Source
Gas Permeability (Barrer) + Source
Glass Transition Temp (°C) + Source
Melting Temperature (°C) + Source
Thermal Decomposition Temp (°C) + Source
Safety Data
Hildebrand Solubility Parameter (MPa^0.5) + Source
Hansen Solubility Parameters + Source
Solubility + Source

Return your answer in JSON format.
"""

@app.route("/")
def home():
    return "PolyTherm Flask App is running."

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "Webhook active"}), 200

@app.route("/debug_headers", methods=["POST"])
def debug_headers():
    print(f"🔎 Headers: {dict(request.headers)}")
    print(f"📦 Body: {request.get_json()}")
    return jsonify({"status": "received"})

@app.route("/add_polymer")
def add_polymer():
    polymer_name = request.args.get("name")
    if not polymer_name:
        return jsonify({"error": "Missing polymer name in URL query string."}), 400

    try:
        prompt = PROMPT_TEMPLATE.format(polymer_name=polymer_name)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content

        try:
            polymer_data = json.loads(content)
        except json.JSONDecodeError:
            return jsonify({"error": "OpenAI response not valid JSON", "raw": content}), 500

        if os.path.exists(PENDING_ENTRIES_PATH):
            with open(PENDING_ENTRIES_PATH, "r") as f:
                entries = json.load(f)
        else:
            entries = []

        entries.append(polymer_data)

        with open(PENDING_ENTRIES_PATH, "w") as f:
            json.dump(entries, f, indent=2)

        return jsonify({"status": "Polymer added", "name": polymer_name}), 200

    except Exception as e:
        print(f"[ERROR /add_polymer] {str(e)}")
        return jsonify({"error": str(e)}), 500

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

        # Log entry
        with open(LOG_PATH, "a") as log_file:
            log_file.write(f"Webhook received: {data.get('name', 'Unknown')}\n")

        return jsonify({"status": "Polymer added via webhook"}), 200

    except Exception as e:
        print(f"[ERROR /update_pending] {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/pending_entries", methods=["GET"])
def get_pending_entries():
    try:
        if os.path.exists(PENDING_ENTRIES_PATH):
            with open(PENDING_ENTRIES_PATH, "r") as f:
                entries = json.load(f)
            return jsonify(entries)
        else:
            return jsonify([])
    except Exception as e:
        print(f"[ERROR /pending_entries] {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/debug_entries", methods=["GET"])
def debug_entries():
    try:
        if os.path.exists(PENDING_ENTRIES_PATH):
            with open(PENDING_ENTRIES_PATH, "r") as f:
                data = json.load(f)
            return jsonify(data), 200
        else:
            return jsonify([]), 200
    except Exception as e:
        print(f"[ERROR /debug_entries] {str(e)}")
        return jsonify({"error": str(e)}), 500

# Expose app for gunicorn
if __name__ == "__main__":
    app.run()
