from flask import Flask, request, render_template
from dotenv import load_dotenv
import os
import pdfplumber
import docx
import re
from werkzeug.utils import secure_filename
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-pro")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx'}

# Utility functions
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

# Generate MCQs using Google Gemini
def Question_mcqs_generator(input_text, num_questions):
    prompt = f"""
Generate {num_questions} multiple-choice questions from the following text:

{input_text}

Format each question like this:

Q: ...
Options:
A) ...
B) ...
C) ...
D) ...
Answer: ...
    """

    response = model.generate_content(prompt)
    return response.content


def save_mcqs_to_file(mcqs, filename):
    results_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    with open(results_path, 'w') as f:
        f.write(mcqs)
    return results_path

def create_pdf(mcqs, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for mcq in mcqs.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)  # Add a line break

    pdf_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    pdf.output(pdf_path)
    return pdf_path

# Routes
@app.route("/")
def index():
    return render_template('index.html')

# @app.route("/generate", methods=['POST'])
# def generate_mcqs():
#     if 'file' not in request.files:
#         return "No file has been chosen!"

#     file = request.files['file']
#     num_questions = request.form.get('num_questions', 5)

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)

#         text = extract_text_from_file(file_path)


#         if text:
#           num_questions = int(request.form['num_questions'])
#           mcqs = Question_mcqs_generator(text, num_questions)
#           # print(mcqs)  # MCQs printed in console

#           # Save the generated MCQs to a file
#           txt_filename = f"generated_mcqs{filename.rsplit('.', 1)[0]}.txt"
#           pdf_filename = f"generated_mcqs{filename.rsplit('.', 1)[0]}.pdf"
#           save_mcqs_to_file(mcqs, txt_filename)
#           create_pdf(mcqs, pdf_filename)

#           # Display and allow downloading
#           return render_template('results.html', mcqs=mcqs, txt_filename=txt_filename, pdf_filename=pdf_filename)
#     return "Invalid file format"



@app.route("/generate", methods=['POST'])
def generate_mcqs():
    if 'file' not in request.files:
        return "No file has been chosen!"

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        text = extract_text_from_file(file_path)

        if not text.strip():
            return "Could not extract text from the file. Please upload a valid PDF/TXT/DOCX."

        num_questions = int(request.form.get('num_questions', 5))
        mcqs = Question_mcqs_generator(text, num_questions)

        # Save to file
        txt_filename = f"generated_mcqs_{filename.rsplit('.',1)[0]}.txt"
        pdf_filename = f"generated_mcqs_{filename.rsplit('.',1)[0]}.pdf"
        save_mcqs_to_file(mcqs, txt_filename)
        create_pdf(mcqs, pdf_filename)

        return render_template('results.html', mcqs=mcqs, txt_filename=txt_filename, pdf_filename=pdf_filename)

    return "Invalid file format. Allowed: pdf, txt, docx"




@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

# Main
if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    app.run(debug=True)