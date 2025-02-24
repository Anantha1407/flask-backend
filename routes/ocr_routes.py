import os
import easyocr
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from utils.auth_utils import login_required

ocr_bp = Blueprint('ocr', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load EasyOCR model (English)
reader = easyocr.Reader(['en'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ocr_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process with EasyOCR
        text = extract_text(filepath)

        os.remove(filepath)

        return jsonify({'message': 'File processed successfully', 'extracted_text': text}), 200

    return jsonify({'error': 'Invalid file type'}), 400

def extract_text(image_path):
    try:
        img = Image.open(image_path)  # Convert to RGB for compatibility
        result = reader.readtext(img, detail=0)
        print(result)
          # Extract text using EasyOCR
        return result
    except UnidentifiedImageError:
        return "Invalid image format"
    except Exception as e:
        return str(e)
