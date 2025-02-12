from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

key = Fernet.generate_key()
cipher_suite = Fernet(key)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        text = request.form.get('text')
        file = request.files.get('file')
        algorithm = request.form.get('algorithm', 'fernet')

        result = None
        filename = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            with open(filepath, 'rb') as f:
                data = f.read()

            if action == 'encrypt':
                result = cipher_suite.encrypt(data)
            elif action == 'decrypt':
                result = cipher_suite.decrypt(data)

            with open(filepath, 'wb') as f:
                f.write(result)

            filename = f"{action}_{filename}"
            result = filename

        elif text:
            if action == 'encrypt':
                result = cipher_suite.encrypt(text.encode()).decode()
            elif action == 'decrypt':
                result = cipher_suite.decrypt(text.encode()).decode()

        return render_template('index.html', result=result, action=action.capitalize(), filename=filename)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)