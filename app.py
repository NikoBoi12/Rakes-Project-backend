import base64
import json
from datetime import datetime
import requests
import fitz
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
}, supports_credentials=True)

@app.route('/login')
def login():
    return "Login Page"

@app.route('/home')
def home():
    return "Home Page"

@app.post('/test')
def upload():
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: No token found or invalid format"}), 401

    access_token = auth_header.split(" ")[1]

    data = request.get_json()
    if not data or "file" not in data:
        return jsonify({"error": "No file data provided"}), 400

    try:
        pdf_data = base64.b64decode(data.get("file"))
        
        with open("syllabus.pdf", "wb") as pdf_file:
            pdf_file.write(pdf_data)

        print(f"File received and verified with token: {access_token[:10]}...")
        return jsonify({"message": "File uploaded successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def convert_pdf_to_images(base64_pdf_string):
    """Converts the incoming base64 PDF into an array of base64 PNG images for Ollama."""
    pdf_data = base64.b64decode(base64_pdf_string)

    doc = fitz.open(stream=pdf_data, filetype="pdf")
    base64_images = []

    for page in doc[:1]:
        pix = page.get_pixmap(dpi=72, alpha=False)
        img_bytes = pix.tobytes("png")
        base64_string = base64.b64encode(img_bytes).decode('utf-8')
        base64_images.append(base64_string)

    return base64_images


@app.route('/create-invite', methods=['POST'])
def create_invite():
    data = request.json
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: No token found or invalid format"}), 401

    if not data or "file" not in data:
        return jsonify({"error": "No file provided in JSON payload"}), 400

    print("Converting PDF to images...")
    try:
        base64_images = convert_pdf_to_images(data.get("file"))
    except Exception as e:
        return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500

    print("Sending to Ollama (This should take ~15-30 seconds)...")
    ai_response_string = generate_event(base64_images)
    print("AI Response:", ai_response_string)

    try:
        events_array = json.loads(ai_response_string)
        if isinstance(events_array, dict):
            events_array = [events_array]
    except json.JSONDecodeError:
        return jsonify({"error": "AI did not return valid JSON", "ai_raw_output": ai_response_string}), 500

    print("Parsed Events:", events_array)

    google_calendar_endpoint = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }

    results = []
    for event_data in events_array:
        try:
            response = requests.post(google_calendar_endpoint, headers=headers, json=event_data)
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"raw_error": response.text}

            if response.status_code == 200:
                results.append({"status": "success", "link": response_data.get('htmlLink', 'No link provided')})
            else:
                results.append({"status": "failed", "error": response_data})
        except Exception as e:
            results.append({"status": "failed", "error": str(e)})

    return jsonify({"processed_events": results}), 200


def generate_event(base64_images):
    current_context = datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""
You are a strict data extraction system. Look at the provided images of a course syllabus. Extract all scheduled events, classes, or deadlines. Output ONLY a valid JSON array of event objects.

Current Context: The current date is {current_context}. The default location is Lincoln, Nebraska, United States (America/Chicago timezone).

STRICT RULES:
1. Output NOTHING except a raw, valid JSON array `[...]`. Do not use markdown blocks (```json). Do not add conversational text.
2. If there are no events, output an empty array: `[]`.
3. Escape any double quotes or special characters within the text fields.
4. `start.dateTime` and `end.dateTime` MUST be strictly formatted in ISO 8601 with the Central Time offset (e.g., "YYYY-MM-DDTHH:MM:SS-06:00").
5. If the text mentions a day/month but no year, infer the next upcoming occurrence based on the Current Context.
6. If no end time is specified, make the end `dateTime` exactly 1 hour after the start `dateTime`.

The output MUST perfectly match this schema for every object in the array:
[
  {{
    "summary": "Event Title",
    "location": "Event Location or empty string",
    "description": "Any additional details, rules, or instructions from the text.",
    "start": {{
      "dateTime": "YYYY-MM-DDTHH:MM:SS-06:00",
      "timeZone": "America/Chicago"
    }},
    "end": {{
      "dateTime": "YYYY-MM-DDTHH:MM:SS-06:00",
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
]
"""
    return query_ollama(prompt, base64_images)


def query_ollama(prompt, base64_images):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen2.5vl:7b",
        "prompt": prompt,
        "images": base64_images,
        "stream": False,
        "format": "json",
    }

    response = requests.post(url, json=payload)
    return response.json().get("response", "[]")


if __name__ == '__main__':
    app.run(debug=True, port=5000)