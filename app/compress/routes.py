import os
from flask import Blueprint, render_template, request, send_from_directory, redirect, url_for
from .utils import compress_files, convert_images_to_pdf

compress_bp     = Blueprint('compress', __name__, url_prefix='/compress')
img_to_pdf_bp      = Blueprint('img_to_pdf', __name__, url_prefix='/img_to_pdf')
UPLOAD_FOLDER   = 'app/static/uploads'

# Render Index compresor
@compress_bp.route('/', methods=['GET'])
def index():
    return render_template('compress/compress.html')
    
#Render Index img to pdf
@img_to_pdf_bp.route('/', methods=['GET'])
def index():
    return render_template('compress/img_pdf.html')

@img_to_pdf_bp.route('/upload', methods=['POST'])
def img_pdf():
    input_folder = upload_files(request)
    print("input_folder",input_folder)
    output_file = "app/static/uploads/output.pdf"
    convert_images_to_pdf(input_folder, "app/static/uploads/output.pdf")
    return redirect(url_for('compress.download_file', filename=output_file))

@compress_bp.route('/upload', methods=['POST'])
def compress_zip():
    file_paths = upload_files(request)
    compression_level = request.form.get('compression_level', 'ZIP_DEFLATED')
    compressed_file_path = compress_files(file_paths, compression_level)
    return redirect(url_for('compress.download_file', filename=os.path.basename(compressed_file_path)))

# Ruta para descargar el archivo comprimido
@compress_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Verificar si el archivo existe antes de intentar enviarlo
    print(f"Ruta absoluta del directorio de uploads: {os.path.abspath(UPLOAD_FOLDER)}")
    upload_folder_abs = os.path.abspath(UPLOAD_FOLDER)
    file_path = os.path.join(upload_folder_abs, filename)

    if os.path.exists(file_path):
        print(f"Archivo encontrado: {file_path}")
        return send_from_directory(upload_folder_abs, filename, as_attachment=True)
    else:
        print(f"Archivo no encontrado: {file_path}")
        return "File not found", 404

def upload_files(request):
    if 'files' not in request.files:
        return "No files part", 400
    files = request.files.getlist('files')

    # Guardar los archivos en un directorio temporal
    file_paths = []
    for file in files:
        if file.filename != '':
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            file_paths.append(filepath)

    return file_paths
