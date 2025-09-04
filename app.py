from flask import Flask, request, render_template, send_file

# 24 min

import os
import pdfplumber
import docx
import csv
from werkzeug.utils import secure_filename
import google.generativeai as genai
from fpdf import FPDF

app = Flask(__name__)

# routes (end points)
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/generate", methods=['POST'])
def generate():
    return render_template('results.html')


# python main
if __name__ == "__main__":
    app.run(debug=True)