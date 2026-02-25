# Rakes Project – CornHacks UNL 2026

A basic web development starter for CornHacks UNL 2026.

## Tech Stack

- **Backend:** Python + Flask
- **Frontend:** HTML, CSS, JavaScript (served as static files)

## Getting Started

### Prerequisites

- [Python 3.8+](https://www.python.org/)

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run in development mode (with auto-reload)

```bash
FLASK_ENV=development python server.py
```

### Run in production mode

```bash
python server.py
```

Open your browser and go to [http://localhost:3000](http://localhost:3000).

## Project Structure

```
├── server.py        # Flask server & API routes
├── public/
│   ├── index.html   # Main HTML page
│   ├── style.css    # Styles
│   └── script.js    # Frontend JavaScript
├── requirements.txt
└── .gitignore
```

## Adding Features

- **New API routes:** Add them in `server.py` under the existing `/api/hello` example.
- **Frontend pages:** Edit files in `public/` or add new HTML/CSS/JS files there.
- **Environment variables:** Create a `.env` file (already git-ignored) and read them with `os.environ.get('YOUR_VAR')` in `server.py`.
