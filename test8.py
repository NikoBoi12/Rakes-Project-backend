import base64
import os
import requests

from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from datetime import datetime

app = Flask(__name__)


# -------------------------
# OLLAMA HELPER FUNCTION
# -------------------------
def query_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return None

    return response.json().get("response", "")


# -------------------------
# BASIC ROUTES
# -------------------------
@app.route('/login')
def login():
    return "Login Page"


@app.route('/home')
def home():
    return "Home Page"


# -------------------------
# PDF UPLOAD ROUTE
# -------------------------
@app.post('/test')
def upload():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        file_base64 = data.get("file")
        if not file_base64:
            return jsonify({"error": "No file provided"}), 400

        pdf_data = base64.b64decode(file_base64)

        file_path = os.path.join(os.getcwd(), "syllabus.pdf")
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(pdf_data)

        token_data = data.get("token")
        if token_data:
            credentials = Credentials(**token_data)
            print("Token received.")

        return jsonify({"message": "File uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# AI EVENT GENERATION ROUTE
# -------------------------
@app.route("/generate-event", methods=["POST"])
def generate_event():
    data = request.json
    user_text = data.get("text")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    prompt = f"""
    Convert the following text into a Google Calendar event JSON object.

    The format MUST be:

    {{
      "summary": "",
      "location": "",
      "description": "",
      "start": {{
        "dateTime": "",
        "timeZone": "America/Chicago"
      }},
      "end": {{
        "dateTime": "",
        "timeZone": "America/Chicago"
      }},
      "reminders": {{
        "useDefault": false,
        "overrides": [
          {{"method": "email", "minutes": 1440}},
          {{"method": "popup", "minutes": 10}}
        ]
      }}
    }}

    Only return valid JSON. No explanations.

    Text:
    {user_text}
    """

    ai_response = query_ollama(prompt)

    if not ai_response:
        return jsonify({"error": "Failed to get response from Ollama"}), 500

    return ai_response


if __name__ == "__main__":
    app.run(debug=True)
