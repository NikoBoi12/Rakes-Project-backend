import base64
import json
import os
from datetime import datetime
import requests
import fitz
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- SETUP ---
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCMXhCyvSEbdqgnClkDDKIaKWq9MJfpvCA")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

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


def call_gemini(prompt: str, pdf_bytes: bytes) -> list:
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "application/pdf",
                            "data": base64.b64encode(pdf_bytes).decode("utf-8")
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["summary", "start", "end"],
                    "properties": {
                        "summary":     {"type": "STRING"},
                        "location":    {"type": "STRING"},
                        "description": {"type": "STRING"},
                        "recurrence":  {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "start": {
                            "type": "OBJECT",
                            "required": ["dateTime"],
                            "properties": {"dateTime": {"type": "STRING"}}
                        },
                        "end": {
                            "type": "OBJECT",
                            "required": ["dateTime"],
                            "properties": {"dateTime": {"type": "STRING"}}
                        },
                        "reminders": {
                            "type": "OBJECT",
                            "properties": {
                                "useDefault": {"type": "BOOLEAN"},
                                "overrides": {
                                    "type": "ARRAY",
                                    "items": {
                                        "type": "OBJECT",
                                        "properties": {
                                            "method":  {"type": "STRING"},
                                            "minutes": {"type": "INTEGER"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    res = requests.post(GEMINI_URL, json=payload)

    if res.status_code != 200:
        raise Exception(f"Gemini REST error {res.status_code}: {res.text}")

    raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(raw_text)


@app.route('/create-invite', methods=['POST'])
def create_invite():
    data = request.json
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: No token found or invalid format"}), 401

    if not data or "file" not in data:
        return jsonify({"error": "No file provided in JSON payload"}), 400

    try:
        pdf_bytes = base64.b64decode(data["file"])
        current_context = datetime.now().strftime("%A, %B %d, %Y")

        prompt = f"""
        Extract all scheduled events, classes, and deadlines from this syllabus.
        Current Context: {current_context}.
        Location: Lincoln, Nebraska.

        Rules:
        - Default time: 09:00:00 - 10:00:00 if none provided.
        - DateTime format: 'YYYY-MM-DDTHH:MM:SS' (no timezone offset).
        - If no end time is specified, make the end dateTime exactly 1 hour after the start dateTime.
        - Output strictly valid JSON.
        - Include reminders for every event: one email reminder 1440 minutes (24 hours) before, and one popup 10 minutes before.

        Recurring Event Rules:
        - If an event is Office Hours, add a recurrence rule: "RRULE:FREQ=WEEKLY;BYDAY=TU,TH;UNTIL=<last_date>T000000Z"
          and only output ONE office hours event (not one per week).
        - If an event is a weekly class (same topic does not repeat, but the CLASS MEETING TIME does),
          do NOT make the individual class topics recurring — only office hours and standing weekly meetings.
        - Use the last date found in the syllabus as the UNTIL date in all recurrence rules.
        - For recurring events, set the start date to the FIRST occurrence found in the syllabus.
        - Add a "recurrence" field as an array, e.g: ["RRULE:FREQ=WEEKLY;BYDAY=TU,TH;UNTIL=20261211T000000Z"]
        """

        events_array = call_gemini(prompt, pdf_bytes)

        if not events_array:
            return jsonify({"error": "AI returned no events"}), 500

    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse AI response", "details": str(e)}), 500
    except Exception as e:
        print(f"Gemini Error: {e}")
        return jsonify({"error": "AI processing failed", "details": str(e)}), 500

    # --- Google Calendar Integration ---
    gc_endpoint = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {"Authorization": auth_header, "Content-Type": "application/json"}
    final_results = []

    for event in events_array:
        event["start"]["timeZone"] = "America/Chicago"
        event["end"]["timeZone"] = "America/Chicago"

        try:
            res = requests.post(gc_endpoint, headers=headers, json=event)
            try:
                response_data = res.json()
            except ValueError:
                response_data = {"raw_error": res.text}

            if res.status_code in (200, 201):
                final_results.append({
                    "summary": event.get("summary"),
                    "status": "success",
                    "link": response_data.get("htmlLink", "No link provided")
                })
            else:
                final_results.append({
                    "summary": event.get("summary"),
                    "status": "failed",
                    "code": res.status_code,
                    "error": response_data
                })
        except Exception as e:
            final_results.append({
                "summary": event.get("summary"),
                "status": "error",
                "details": str(e)
            })

    return jsonify({"processed_events": final_results}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)