import os
import easyocr
from groq import Groq
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.auth_utils import login_required

ocr_bp = Blueprint('ocr', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load EasyOCR model (English)
reader = easyocr.Reader(['en'])

groq_api_key = os.getenv("GROQ_KEY")
client = Groq(api_key=groq_api_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ocr_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    document_type = request.form.get('document_type', '')
    questions = request.form.getlist('questions')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Extract text using EasyOCR
        text = extract_text(filepath)
        print(questions)

        # Process questions with Groq API (Mistral)
        extracted_info = extract_information(text, questions)

        return jsonify({
            'message': 'File processed successfully',
            'document_type': document_type,
            'extracted_data': extracted_info
        }), 200

    return jsonify({'error': 'Invalid file type'}), 400

def extract_text(image_path):
    try:
        results = reader.readtext(image_path, detail=0)
        return " ".join(results)
    except Exception as e:
        return str(e)

def extract_information(text, questions):
    answers = {}
    for question in questions:
        prompt = f"""
        Pick out only the information from the text that is relevant to the question.
        Text: {text}

        Question: {question}

        Provide answer in the format:  "value"
        """
        try:
            response = client.chat.completions.create(
                model="gemma2-9b-it",  # Adjust if Groq has a specific model name for Mistral
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Keep responses consistent
                max_tokens=200
            )
            answers[question] = response.choices[0].message.content.strip()
        except Exception as e:
            answers[question] = f"Error processing question: {str(e)}"
    
    return answers
