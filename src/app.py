import os
from flask import Flask, flash, request, redirect, url_for, make_response, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

from modules.main import fetch_files_and_convert
from utils.Constants import ALLOWED_EXTENSIONS



app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/images', methods=['POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('files')
        image_files = []
        for file in files:
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                image_files.append(file.read())

        pdf_file = fetch_files_and_convert(image_files)
        if pdf_file:
            response = make_response(pdf_file)
            response.headers.set('Content-Type', 'application/pdf')
            response.headers.set(
                'Content-Disposition', 'attachment', filename='doc.pdf')
            return response

        else: return make_response(-1, 500)

app.run()