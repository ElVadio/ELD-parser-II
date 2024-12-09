from flask import Flask, request, jsonify
from ml.document_processor import DocumentProcessor

app = Flask(__name__)
processor = DocumentProcessor()

@app.route('/process', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        result = processor.process_pdf(file)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500