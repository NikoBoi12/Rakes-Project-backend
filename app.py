import base64
import os

from flask import Flask, request
from flask_cors import CORS
from google.oauth2.credentials import Credentials
app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/login')
def login():
    return "Login Page"


@app.route('/home')
def home():
    return "Home Page"


@app.post('/test')
def upload():
    data = request.get_json()

    pdf_data = base64.b64decode(data.get("file"))

    print(pdf_data)

    with open("syllabus.pdf", "wb") as pdf_file:
        pdf_file.write(pdf_data)

    token_data = data.get("token")



    return "Upload File"


if __name__ == '__main__':
    app.run(debug=True)
