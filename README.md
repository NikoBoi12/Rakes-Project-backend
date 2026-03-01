# Syllabus to Calendar - Backend

The Python Flask backend for the Syllabus to Calendar application. This service handles PDF decoding, interfaces with Google's Gemini AI to intelligently extract schedule data based on user-defined filters, and posts the formatted events to the user's Google Calendar.

## Features
* **PDF Processing:** Securely decodes base64 string payloads into temporary PDF files.
* **Gemini AI Integration:** Utilizes the `gemini-2.5-flash` model via REST API with strict JSON schema enforcement to ensure highly accurate data extraction.
* **Dynamic Filtering:** Dynamically injects user-selected filters (like ignoring exams or office hours) into the AI prompt.
* **Google Calendar Automation:** Authenticates using the user's frontend Bearer token to automatically populate their primary calendar with formatted events and recurrence rules.

## Tech Stack
* Python 3.x
* Flask & Flask-CORS
* Google Generative AI (Gemini REST API)
* Google Calendar API

## Setup & Installation

1. **Clone the repository**

2. **Create and activate a virtual environment:**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   \`\`\`

3. **Install the required packages:**
   \`\`\`bash
   pip install flask flask-cors requests pymupdf
   \`\`\`
