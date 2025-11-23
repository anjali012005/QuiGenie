# QuiGenie

QuiGenie is a web application that automatically generates multiple-choice questions (MCQs) from PDF, TXT, or DOCX files using AI. Users can upload documents, specify the number of questions, and download the generated MCQs as TXT or PDF files.

<img width="1917" height="976" alt="image" src="https://github.com/user-attachments/assets/36e6b297-0543-4f9f-8b7e-23ed1b0c5714" />

---

## Features

- Upload PDF, TXT, or DOCX files.
- Extract text from uploaded files.
- Generate multiple-choice questions using Google Gemini AI.
- Download generated MCQs as:
  - Text file (TXT)
  - PDF file
- Clean and simple UI to view MCQs before downloading.

---

## Demo

- Local: `http://127.0.0.1:5000`  
- Deployed:  https://quigenie-2.onrender.com/

---

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **AI Integration:** Google Gemini API
- **PDF Generation:** ReportLab
- **Text Extraction:** pdfplumber, python-docx

---

## Setup Instructions (Local)

1. **Clone the repository:**

```bash
git clone https://github.com/anjali012005/QuiGenie.git
cd QuiGenie
```

Create a virtual environment:

```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate
```


Install dependencies:
```bash
pip install -r requirements.txt
```
Add your Google API key:

Create a .env file in the project root:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

Run the app:
```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

Deployment (Render.com)

Connect your GitHub repo to Render.

Add environment variable GOOGLE_API_KEY in Render’s dashboard.

Set the start command:
```bash
gunicorn app:app
```

Ensure your requirements.txt includes all dependencies:
```bash
Flask
python-dotenv
pdfplumber
python-docx
reportlab
gunicorn
google-generativeai
```

File Structure
```bash
quigenie/
│
├── app.py               # Main Flask application
├── templates/
│   ├── index.html       # Upload form
│   └── results.html     # Generated MCQs display
├── static/
│   └── results.css      # CSS for results page
├── uploads/             # Temporary uploaded files
├── results/             # Generated MCQ files
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not in repo)
```
Usage

Go to the homepage.

Upload your document (PDF, TXT, DOCX).

Enter the number of questions to generate.

Click Generate.

View the MCQs and download them as TXT or PDF.

Acknowledgements

Google Gemini API for AI-powered question generation.
pdfplumber and python-docx for text extraction.
ReportLab for PDF creation.

## 💛 Author<br/>

**Anjali Daharwal**  <br/>
CS Student | Web Developer
