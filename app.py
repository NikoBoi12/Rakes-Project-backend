import base64
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
import requests
import fitz  # PyMuPDF

app = Flask(__name__)


@app.route('/login')
def login():
    return "Login Page"


@app.route('/home')
def home():
    return "Home Page"


def convert_pdf_to_images(base64_pdf_string):
    """Converts the incoming base64 PDF into an array of base64 PNG images for Ollama."""
    pdf_data = base64.b64decode(base64_pdf_string)

    # Open PDF directly from memory
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    base64_images = []

    for page in doc:
        # Render each page to an image
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        base64_string = base64.b64encode(img_bytes).decode('utf-8')
        base64_images.append(base64_string)

    return base64_images


@app.route('/create-invite', methods=['POST'])
def create_invite():
    data = request.json
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401

    if "file" not in data:
        return jsonify({"error": "No file provided in JSON payload"}), 400

    base64_images = convert_pdf_to_images(data.get("file"))

    print("Running")

    ai_response_string = generate_event(base64_images)
    print("AI Response:", ai_response_string)

    # 3. Parse the AI response into a Python list

    print(ai_response_string)

    try:
        events_array = json.loads(ai_response_string)
        if isinstance(events_array, dict):
            events_array = [events_array]
    except json.JSONDecodeError:
        return jsonify({"error": "AI did not return valid JSON", "ai_raw_output": ai_response_string}), 500

    print(events_array)

    # 4. Loop through the array and hit the Google API for each event
    google_calendar_endpoint = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }

    results = []
    for event_data in events_array:
        try:
            response = requests.post(google_calendar_endpoint, headers=headers, json=event_data)
            response_data = response.json()

            if response.status_code == 200:
                results.append({"status": "success", "link": response_data.get('htmlLink')})
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

    # Notice the "images" array added to the payload here
    payload = {
        "model": "qwen2.5vl:7b",
        "prompt": prompt,
        "images": base64_images,
        "stream": False,
        "format": "json"
    }

    response = requests.post(url, json=payload)
    return response.json().get("response", "[]")


if __name__ == '__main__':
    app.run(debug=True)