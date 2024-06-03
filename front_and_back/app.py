from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'supersecretkey'  # Необходимо для использования flash сообщений
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Хранение истории загрузок
uploaded_files = []

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            uploaded_files.append(file.filename)
            return render_template('index.html', filename=file.filename, uploaded_files=uploaded_files)
    return render_template('index.html', filename=None, uploaded_files=uploaded_files)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global uploaded_files
    for filename in uploaded_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    uploaded_files = []
    flash("Upload history and files cleared!")
    return redirect(url_for('upload_file'))

if __name__ == "__main__":
    app.run(debug=True)
