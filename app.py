from flask import Flask, render_template, request, send_from_directory
import os
from main import run
import uuid

app = Flask(__name__)

####################################################################################################### OTHER FUNCTIONS (NO PATH)

def is_audio_file(filepath):
    # audio_extensions = ['.mp3', '.wav'] #real thing, REMOVE next line
    audio_extensions = ['.mp3', '.wav', '.midi']
    file_ext = os.path.splitext(filepath)[1]
    return file_ext.lower() in audio_extensions

def process_music(filepath, id):
    run(filepath, id)
    

def generate_id ():
    return str(uuid.uuid4())


####################################################################################################### ROOT

@app.route('/')
def index():
    return render_template('index.html')

####################################################################################################### UPLOAD FILE PAGE

@app.route('/process', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    
    if uploaded_file.filename != '' and is_audio_file(uploaded_file.filename):
        folder_id = generate_id()
        folder_path = os.path.join('uploads', folder_id)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, uploaded_file.filename)
        uploaded_file.save(file_path)
        processed_succesfully = process_music(file_path, folder_id)
        results_dir = os.path.join('results', folder_id)
        result_files = [file for file in os.listdir(results_dir) if os.path.isfile(os.path.join(results_dir, file))]
        return render_template('results.html', folder_id=folder_id, files=result_files)
    
    return render_template('index.html')

####################################################################################################### DOWNLOAD FILES

@app.route('/download/<folder_id>/<filename>')
def download_file(folder_id, filename):
    results_dir = os.path.join('results', folder_id)
    if not os.path.exists(results_dir):
        return 'Folder not found!', 404

    return send_from_directory(results_dir, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=False)
