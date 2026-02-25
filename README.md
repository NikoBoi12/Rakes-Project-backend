# Rakes Project – CornHacks UNL 2026

A basic web development starter for CornHacks UNL 2026.

## Tech Stack

- **Backend:** Node.js + Express
- **Frontend:** HTML, CSS, JavaScript (served as static files)

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later recommended)

### Install dependencies

```bash
npm install
```

### Run in development mode (with live reload)

```bash
npm run dev
```

### Run in production mode

```bash
npm start
```

Open your browser and go to [http://localhost:3000](http://localhost:3000).

## Project Structure

```
├── server.js        # Express server & API routes
├── public/
│   ├── index.html   # Main HTML page
│   ├── style.css    # Styles
│   └── script.js    # Frontend JavaScript
├── package.json
└── .gitignore
```

## Adding Features

- **New API routes:** Add them in `server.js` under the existing `/api/hello` example.
- **Frontend pages:** Edit files in `public/` or add new HTML/CSS/JS files there.
- **Environment variables:** Create a `.env` file (already git-ignored) and use `process.env.YOUR_VAR` in `server.js`.
