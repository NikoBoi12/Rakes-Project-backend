from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='public')

PORT = int(os.environ.get('PORT', 3000))


# Example API route
@app.route('/api/hello')
def hello():
    return jsonify(message='Hello from the server!')


# Serve the frontend (catch-all for client-side routing)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    print(f'Server running at http://localhost:{PORT}')
    app.run(host='0.0.0.0', port=PORT, debug=os.environ.get('FLASK_ENV') == 'development')
