from flask import Flask, render_template, request, redirect, url_for, flash
import os
from PIL import Image
import torch
from torchvision import transforms
from classes import classes  # Импорт классов

app = Flask(__name__, static_folder='static')
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Загрузка кастомной модели
MODEL_PATH = os.path.join(os.path.dirname(__file__), "custom_model_traced_087.pt")
traced_model = torch.jit.load(MODEL_PATH).to(DEVICE)

def preprocess_image(image_path):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(image_path)
    image = preprocess(image)
    image = image.unsqueeze(0)  # Добавляем batch dimension
    return image

def predict_image(image_path):
    image = preprocess_image(image_path).to(DEVICE)
    traced_model.eval()
    with torch.no_grad():
        output = traced_model(image)
        _, predicted = torch.max(output, 1)
    predicted_class = classes[predicted.item()]  # Получение класса по индексу
    return predicted_class

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
            predicted_class = predict_image(filename)
            uploaded_files.append((file.filename, predicted_class))
            return render_template('index.html', filename=file.filename, predicted_class=predicted_class, uploaded_files=uploaded_files)
    return render_template('index.html', filename=None, uploaded_files=uploaded_files)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global uploaded_files
    for filename, _ in uploaded_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    uploaded_files = []
    flash("Upload history and files cleared!")
    return redirect(url_for('upload_file'))

if __name__ == "__main__":
    app.run(debug=True)
