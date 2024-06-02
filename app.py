import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pdf2image import convert_from_path

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'avi', 'mov'}
FILES_JSON = 'files.json'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_files():
    if not os.path.exists(FILES_JSON):
        with open(FILES_JSON, 'w') as f:
            json.dump([], f)  # Initialize with an empty list
    with open(FILES_JSON, 'r') as f:
        return json.load(f)

def save_files(files):
    with open(FILES_JSON, 'w') as f:
        json.dump(files, f, indent=4)

@app.route('/')
def index():
    files = load_files()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        if file.filename.endswith('.pdf'):
            pages = convert_from_path(filepath, 300)
            pdf_base = os.path.splitext(file.filename)[0]
            for i, page in enumerate(pages):
                image_path = os.path.join(UPLOAD_FOLDER, f"{pdf_base}_page_{i + 1}.png")
                page.save(image_path, 'PNG')

        files = load_files()
        files.append({'filename': file.filename, 'duration': 5})  # Default duration of 5 seconds
        save_files(files)

        return redirect(url_for('index'))

@app.route('/update_duration', methods=['POST'])
def update_duration():
    filename = request.form['filename']
    duration = int(request.form['duration'])
    files = load_files()
    for file in files:
        if file['filename'] == filename:
            file['duration'] = duration
            break
    save_files(files)
    return redirect(url_for('index'))

@app.route('/display')
def display():
    files = load_files()
    return render_template('display.html', files=files)

@app.route('/display/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
