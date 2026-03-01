import base64
import os

from flask import Flask, request, jsonify, make_response
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)