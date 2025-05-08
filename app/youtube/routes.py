from flask import Flask, render_template, request, jsonify, send_from_directory, Blueprint
import yt_dlp
import os

youtube_to_mp3_bp = Blueprint('youtube', __name__, url_prefix='/youtube')

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'static/downloads')

# Asegúrate de que la carpeta 'downloads' exista
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_audio(url):
    # Configuración de opciones para yt-dlp
    options = {
        'format': 'bestaudio/best',  # Selecciona el mejor audio disponible
        'keepvideo': False,          # No conserva el video después de la conversión
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Guarda en la carpeta 'downloads'
        'postprocessors': [
            {   # Conversión a MP3
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }
        ],
        'ffmpeg_location': '/usr/bin/ffmpeg',  # Ubicación de ffmpeg (ajústala según tu sistema)
    }

    # Descargar el archivo de audio
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"{info['title']}.mp3", info['title'] + '.mp3'


@youtube_to_mp3_bp.route('/', methods=['GET'])
def index():
    return render_template('youtube/index.html')  # Mostrar el formulario

@youtube_to_mp3_bp.route('/download', methods=['POST'])
def download():
    url = request.form['url']  # Obtener la URL desde el formulario
    if url:
        try:
            filepath, filename = download_audio(url)  # Descargar el audio
            # Crear URL accesible desde Flask
            filepath_in_static = f'/downloads/{filename}'  
            return jsonify({'success': True, 'filepath': filepath_in_static, 'filename': filename})  # Enviar respuesta JSON
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'No URL provided!'})

@youtube_to_mp3_bp.route('/downloads/<filename>')
def download_file(filename):
    print("DOWNLOAD_FOLDER:",DOWNLOAD_FOLDER)
    print("filename:",filename)
    return send_from_directory(DOWNLOAD_FOLDER, filename)
