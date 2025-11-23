from flask import Flask, request, render_template, send_file
from dotenv import load_dotenv
import os
import pdfplumber
import docx
import re
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import google.generativeai as genai

# Load .env
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise Exception("❌ GOOGLE_API_KEY not found in .env")

genai.configure(api_key=API_KEY)

print("\n🔍 AVAILABLE GEMINI MODELS:")
print("=" * 55)
for m in genai.list_models():
    print(" -", m.name)
print("=" * 55)

# Best text generation model
MODEL_NAME = "models/gemini-2.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

# Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx'}


# ---------- FILE UTIL ----------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def extract_text_from_file(file_path):
    ext = file_path.rsplit(".", 1)[1].lower()
    text = ""

    if ext == "pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    elif ext == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    elif ext == "docx":
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])

    return clean_text(text)


# ---------- GEMINI MCQ GENERATOR ----------
def Question_mcqs_generator(input_text, num_questions):
    prompt = f"""
Generate {num_questions} MCQs from the following content.

Format exactly like this:

## MCQ
Q: Question text here
A] Option A
B] Option B
C] Option C
D] Option D
Correct Answer: A

Content:
{input_text}
"""

    res = model.generate_content(prompt)
    return res.text


# ---------- SAVE TXT ----------
def save_mcqs_to_file(mcqs, filename):
    path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(mcqs)
    return path


# ---------- PDF (UNICODE SUPPORTED) ----------
def create_pdf(mcqs, filename):
    pdf_path = os.path.join(app.config['RESULTS_FOLDER'], filename)

    styles = getSampleStyleSheet()
    style = styles["Normal"]

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)

    paragraphs = []
    for line in mcqs.split("\n"):
        paragraphs.append(Paragraph(line.replace("  ", "&nbsp;&nbsp;"), style))

    doc.build(paragraphs)
    return pdf_path


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_mcqs():
    if "file" not in request.files:
        return "No file uploaded!"

    file = request.files["file"]
    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        extracted_text = extract_text_from_file(file_path)

        if not extracted_text.strip():
            return "Failed to extract text."

        num_questions = int(request.form.get("num_questions", 5))

        mcqs = Question_mcqs_generator(extracted_text, num_questions)

        txt_filename = f"mcqs_{filename.rsplit('.',1)[0]}.txt"
        pdf_filename = f"mcqs_{filename.rsplit('.',1)[0]}.pdf"

        save_mcqs_to_file(mcqs, txt_filename)
        create_pdf(mcqs, pdf_filename)

        return render_template(
            "results.html",
            mcqs=mcqs,
            txt_filename=txt_filename,
            pdf_filename=pdf_filename
        )

    return "Invalid file format! Allowed: pdf, txt, docx"


@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(app.config["RESULTS_FOLDER"], filename)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)

    print("\n🚀 Flask server running at http://127.0.0.1:5000\n")
    app.run(debug=True)
