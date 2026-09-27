# Live Paintings by Harshita

A multi-page website for a live wedding and event painting studio. Visitors can explore the studio, estimate painting prices, submit booking details, and ask the studio assistant questions.

## Features

- Studio pages for the process, gallery, reviews, FAQs, and artist information.
- Price estimator and booking form.
- Orders page with customer OTP login and admin login.
- Chat assistant that retrieves studio information and can use Gemini to generate answers.

## Tech Stack

- **

- **Frontend:** A multi-page website built with HTML, Tailwind CSS via CDN, and plain JavaScript. 
It uses Font Awesome icons and Google Fonts. There’s no React or other frontend framework in the current setup.
 See index.html and chatbot.js.

- **Backend:**  Python with FastAPI, served locally by Uvicorn on port 8001.
 The API handles chat, bookings, customer OTP verification, and admin login. See rag_server.py.

- **AI assistant:** A retrieval-augmented generation (RAG) flow. The app chunks its studio information, 
stores it in ChromaDB, retrieves up to four relevant chunks per question, 
then uses Gemini to generate an answer when GEMINI_API_KEY is configured. See vectorbase.py and answering.py.

- **Retrieval:** ChromaDB with a local 256-dimensional hashed-token embedding function. The assistant retrieves up to four knowledge-base chunks per question.

- **Answer generation:** Google Gemini when `GEMINI_API_KEY` is configured; otherwise, the backend uses a local text-matching fallback.

- **Data:** Booking records are stored in `data/bookings.json`; assistant content is in `data/live_painting_data.txt`; ChromaDB persists its index in `chroma_db/`.

## Project Structure

```text
.
├── index.html
├── about.html
├── estimator.html
├── faq.html
├── gallery.html
├── orders.html
├── process.html
├── reviews.html
├── chatbot.js
├── rag_server.py
├── requirements.txt
├── rag_engine/
├── data/
└── chroma_db/
```

## Requirements

- Python 3.10 or newer
- A Gemini API key is optional. Without one, the chat endpoint uses its local fallback.

## Run Locally (Windows PowerShell)

From the project folder, create and activate a virtual environment, then install the Python dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a local environment file from the example:

```powershell
Copy-Item .env.example .env
```

To enable Gemini answers, add your key to `.env`:

```env
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash
```

Start the API from the project folder:

```powershell
python -m uvicorn rag_server:app --host 127.0.0.1 --port 8001
```

Then open `index.html` using a local development server, such as the VS Code Live Server extension. The API health check is available at `http://127.0.0.1:8001/health`.

## Demo Authentication and Data

- Customer OTP uses the demo code `123456`; it is not a real SMS or email delivery service.
- Customer and admin sessions are held in memory and are cleared when the API process restarts.
- Set `ADMIN_PASSWORD` in `.env` to choose an admin password. The current backend also has a development fallback, which must be changed before deployment.
- Booking records can contain customer names, phone numbers, and email addresses. Do not publish real customer data in a public repository; remove or anonymize `data/bookings.json` before pushing.
- `.env` contains local configuration and secrets. Keep it private; `.gitignore` excludes it.

This project is intended for local development and demonstration. Authentication and data storage should be upgraded before handling real customers in production.