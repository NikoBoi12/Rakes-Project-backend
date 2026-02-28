import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

def query_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    return response.json().get("response", "")


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

    return ai_response  # return raw JSON text from model


if __name__ == "__main__":
    app.run(debug=True)
