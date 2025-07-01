from flask import Flask, send_from_directory
from .compress.routes import compress_bp, img_to_pdf_bp
from .home.routes import home_bp
from .youtube.routes import youtube_to_mp3_bp
import os

def create_app():
    
    app = Flask(__name__, static_folder='static')

    app.register_blueprint(compress_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(img_to_pdf_bp)
    app.register_blueprint(youtube_to_mp3_bp)

    # Ruta para servir archivos de descarga
    @app.route('/downloads/<filename>')
    def download_file(filename):
        import urllib.parse
        # Decodificar el nombre del archivo de la URL
        decoded_filename = urllib.parse.unquote(filename)
        downloads_folder = os.path.join(app.root_path, 'static', 'downloads')
        
        # Verificar si la carpeta existe
        if not os.path.exists(downloads_folder):
            print(f"ERROR: La carpeta de descargas no existe: {downloads_folder}")
            return "Carpeta de descargas no encontrada", 404
        
        # Verificar si el archivo existe
        file_path = os.path.join(downloads_folder, decoded_filename)
        if not os.path.exists(file_path):
            print(f"ERROR: El archivo no existe: {file_path}")
            # Listar archivos en la carpeta para debugging
            try:
                files_in_folder = os.listdir(downloads_folder)
                print(f"Archivos en la carpeta: {files_in_folder}")
            except Exception as e:
                print(f"Error al listar archivos: {e}")
            return "Archivo no encontrado", 404
        
        print(f"Archivo solicitado: {filename}")
        print(f"Archivo decodificado: {decoded_filename}")
        print(f"Carpeta de descargas: {downloads_folder}")
        print(f"Archivo encontrado: {file_path}")
        return send_from_directory(downloads_folder, decoded_filename)

    return app
