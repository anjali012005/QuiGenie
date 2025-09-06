from flask import Flask, request, render_template, send_file

# 24 min

from dotenv import load_dotenv
load_dotenv() 
import os
import pdfplumber
import docx
import csv
from werkzeug.utils import secure_filename
import google.generativeai as genai
from fpdf import FPDF
import re
from transformers import pipeline

# initialize text generation pipeline
generator = pipeline("text2text-generation", model="t5-base")

# Set API Key
# os.environ["GOOGLE_API_KEY"] = "your api here"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-pro")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx'}

# custom functions
def allowed_file(filename):
    # anjali.pdf
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def clean_text(text):
    if not text:
        return ""
    # Replace multiple newlines with space
    text = re.sub(r'\n+', ' ', text)
    # Replace multiple spaces with single space
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

# def extract_text_from_file(file_path):
    # anjali.docx
    ext = file_path.rsplit(".", 1)[1].lower()

    if ext == "pdf":
        with pdfplumber.open(file_path) as pdf:
           text = ''.join([page.extract_text() for page in pdf.pages])
        return text


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


def Question_mcqs_generator(input_text, num_questions):
    prompt = f"""
    You are an AI assistant helping the user generate multiple-choice questions (MCQs) based on the following text:
    '{input_text}'
    Please generate {num_questions} MCQs from the text. Each question should have:
    - A clear question
    - Four answer options (labeled A, B, C, D)
    - The correct answer clearly indicate
    Format:
    ## MCQ
    Question: [question]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    Correct Answer: [correct option] 
    
    """

    result = generator(prompt, max_length=512, do_sample=True)
    return result[0]['generated_text']


    # response = model.generate_content(prompt)
    # return response

# routes (end points)
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/generate", methods=['POST'])
def generate_mcqs():
    # if 'file' not in request.files:
    #     return "No file has chosen!"

    # file = request.files['file']
    # # num_questions = request.form['num_questions']
    
    # # anjali.pdf
    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #     file.save(file_path)

    #     # pdf, txt, docx
    #     text = extract_text_from_file(file_path)
        
    #     if text:
    #         num_questions = request.form['num_questions']
            
    #         mcqs = Question_mcqs_generator(text, num_questions)

    #         print("\n\n\n", mcqs)

    #     return render_template('index.html')


        # //////////////////////////////////////

    if 'file' not in request.files:
        return "No file has been chosen!"

    file = request.files['file']
    num_questions = request.form['num_questions']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        text = extract_text_from_file(file_path)
        mcqs = generate_mcqs_from_text(text, num_questions)
        print(mcqs)

        return render_template('index.html', mcqs=mcqs)


# python main
if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    

    if not os.path.exists(app.config['RESULTS_FOLDER']):
        os.makedirs(app.config['RESULTS_FOLDER'])
    
    app.run(debug=True)