import os
from flask import Blueprint, render_template, request, send_from_directory, redirect, url_for
from .utils import compress_files

compress_bp = Blueprint('compress', __name__, url_prefix='/compress')
UPLOAD_FOLDER = 'app/static/uploads'

# Ruta para mostrar el formulario de carga de archivos
@compress_bp.route('/', methods=['GET'])
def index():
    return render_template('compress/index.html')

# Ruta para manejar la subida y compresión de archivos
@compress_bp.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "No files part", 400
    files = request.files.getlist('files')
    # Obtener el nivel de compresión del formulario
    compression_level = request.form.get('compression_level', 'ZIP_DEFLATED')

    # Guardar los archivos en un directorio temporal
    file_paths = []
    for file in files:
        if file.filename != '':
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            file_paths.append(filepath)

    # Comprimir los archivos
    #compressed_file_path = compress_files(file_paths)
        # Comprimir los archivos con el nivel de compresión seleccionado
    compressed_file_path = compress_files(file_paths, compression_level)
    
    print(f"Archivo comprimido guardado en: {compressed_file_path}")  # Imprimir la ruta del archivo

    # Retornar el enlace para descargar el archivo comprimido
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
