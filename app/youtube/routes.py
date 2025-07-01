from flask import Flask, render_template, request, jsonify, send_from_directory, Blueprint
import yt_dlp
import os
import zipfile
import glob
from datetime import datetime

youtube_to_mp3_bp = Blueprint('youtube', __name__, url_prefix='/youtube')

# Usar la ruta absoluta correcta para la carpeta de descargas
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'downloads')

# Asegúrate de que la carpeta 'downloads' exista
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
    print(f"Carpeta de descargas creada: {DOWNLOAD_FOLDER}")
else:
    print(f"Carpeta de descargas existente: {DOWNLOAD_FOLDER}")

def clean_filename(filename):
    """Limpia el nombre del archivo para evitar problemas con caracteres especiales"""
    import re
    import unicodedata
    
    # Normalizar caracteres Unicode
    filename = unicodedata.normalize('NFD', filename)
    
    # Reemplazar solo caracteres realmente problemáticos para URLs y sistemas de archivos
    # Mantener letras, números, espacios, guiones, puntos y algunos caracteres especiales
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
    
    # Reemplazar espacios múltiples con uno solo
    filename = re.sub(r'\s+', ' ', filename)
    
    # Eliminar espacios al inicio y final
    filename = filename.strip()
    
    # Si el nombre está vacío después de la limpieza, usar un nombre por defecto
    if not filename:
        filename = "Unknown"
    
    return filename

def download_audio(url):
    # Verificar que ffmpeg esté disponible
    import subprocess
    try:
        subprocess.run(['/usr/bin/ffmpeg', '-version'], capture_output=True, check=True)
        print("ffmpeg está disponible")
    except Exception as e:
        print(f"Error con ffmpeg: {e}")
        # Si ffmpeg no está disponible, usar configuración sin postprocesador
        options = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
            'keepvideo': False,
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'extract_flat': False,
        }
    else:
        # Configuración completa con ffmpeg
        options = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',  # Formato de audio específico
            'keepvideo': False,          # No conserva el video después de la conversión
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Guarda en la carpeta 'downloads'
            'postprocessors': [
                {   # Conversión a MP3
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }
            ],
            'ffmpeg_location': '/usr/bin/ffmpeg',  # Ubicación de ffmpeg
            'extract_flat': False,  # Para playlists, descargar todos los videos
            'prefer_ffmpeg': True,  # Preferir ffmpeg sobre otros extractores
            'no_warnings': False,  # Mostrar warnings para debugging
            'verbose': True,  # Mostrar información detallada
            'extractaudio': True,  # Forzar extracción de audio
            'audioformat': 'mp3',  # Formato de audio preferido
        }

    # Descargar el archivo de audio
    with yt_dlp.YoutubeDL(options) as ydl:
        print(f"Configuración yt-dlp: {options}")
        
        # Primero extraer información sin descargar
        info = ydl.extract_info(url, download=False)
        print(f"Info extraída: {info.get('title', 'Unknown') if 'title' in info else 'Playlist'}")
        
        # Listar formatos disponibles para debugging
        if 'formats' in info:
            print("Formatos disponibles:")
            for fmt in info['formats']:
                if 'audio' in fmt.get('format_note', '').lower() or 'audio' in fmt.get('format', '').lower():
                    print(f"  - {fmt.get('format_id', 'N/A')}: {fmt.get('format_note', 'N/A')} ({fmt.get('ext', 'N/A')})")
        
        # Ahora descargar
        info = ydl.extract_info(url, download=True)
        
        # Buscar todos los archivos de audio en la carpeta de descargas
        audio_extensions = ['*.mp3', '*.m4a', '*.webm', '*.ogg', '*.wav']
        all_audio_files = []
        for ext in audio_extensions:
            all_audio_files.extend(glob.glob(f'{DOWNLOAD_FOLDER}/{ext}'))
        
        print(f"Archivos de audio encontrados después de descarga: {all_audio_files}")
        
        # Verificar si es una playlist
        if 'entries' in info and len(info['entries']) > 1:
            # Es una playlist, obtener todos los archivos descargados
            downloaded_files = []
            for entry in info['entries']:
                if entry:
                    title = entry.get('title', 'Unknown')
                    # Buscar el archivo de audio correspondiente (más flexible)
                    for audio_file in all_audio_files:
                        if title.lower() in os.path.basename(audio_file).lower():
                            downloaded_files.append(audio_file)
                            break
            
            # Si no encontramos archivos por título, usar todos los archivos de audio recientes
            if not downloaded_files and all_audio_files:
                downloaded_files = all_audio_files
            
            # Crear archivo ZIP con todos los archivos de audio
            if downloaded_files:
                # Obtener información de la playlist para el nombre del archivo
                playlist_title = info.get('title', 'Unknown Playlist')
                channel_name = info.get('uploader', 'Unknown Channel')
                
                # Limpiar el nombre de la playlist para usarlo en el nombre del archivo
                clean_playlist_name = clean_filename(playlist_title)
                clean_channel_name = clean_filename(channel_name)
                
                # Crear nombre del ZIP con información de la playlist
                if clean_playlist_name != 'Unknown Playlist':
                    zip_filename = f"{clean_playlist_name} - {clean_channel_name}.zip"
                else:
                    zip_filename = f"{clean_channel_name} - Playlist.zip"
                
                # Si el nombre es muy largo, truncarlo
                if len(zip_filename) > 100:
                    zip_filename = zip_filename[:97] + ".zip"
                
                zip_path = os.path.join(DOWNLOAD_FOLDER, zip_filename)
                print(f"Creando ZIP: {zip_filename}")
                print(f"Ruta del ZIP: {zip_path}")
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in downloaded_files:
                        zipf.write(file_path, os.path.basename(file_path))
                
                # Verificar que el ZIP se creó correctamente
                if os.path.exists(zip_path):
                    print(f"ZIP creado exitosamente: {zip_path}")
                    print(f"Tamaño del ZIP: {os.path.getsize(zip_path)} bytes")
                else:
                    print(f"ERROR: El ZIP no se creó en: {zip_path}")
                
                # Limpiar archivos de audio individuales
                for file_path in downloaded_files:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                
                return zip_path, zip_filename, len(downloaded_files)
        else:
            # Es un video individual
            if all_audio_files:
                # Tomar el archivo de audio más reciente
                latest_audio = max(all_audio_files, key=os.path.getctime)
                original_filename = os.path.basename(latest_audio)
                
                # Limpiar el nombre del archivo
                clean_name = clean_filename(original_filename)
                if clean_name != original_filename:
                    # Renombrar el archivo con nombre limpio
                    new_path = os.path.join(DOWNLOAD_FOLDER, clean_name)
                    try:
                        os.rename(latest_audio, new_path)
                        latest_audio = new_path
                        print(f"Archivo renombrado: {original_filename} -> {clean_name}")
                    except Exception as e:
                        print(f"Error al renombrar archivo: {e}")
                
                return latest_audio, os.path.basename(latest_audio), 1
    
    return None, None, 0

@youtube_to_mp3_bp.route('/', methods=['GET'])
def index():
    return render_template('youtube/index.html')

@youtube_to_mp3_bp.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    if url:
        try:
            print(f"Descargando URL: {url}")
            filepath, filename, count = download_audio(url)
            print(f"Resultado: filepath={filepath}, filename={filename}, count={count}")
            
            if filepath and filename:
                filepath_in_static = f'/downloads/{filename}'
                
                # Crear mensaje más informativo
                if count > 1:
                    # Es una playlist
                    playlist_title = info.get('title', 'Unknown Playlist') if 'info' in locals() else 'Unknown Playlist'
                    message = f"Se descargaron {count} canciones de '{playlist_title}'"
                else:
                    # Es un video individual
                    video_title = info.get('title', 'Unknown Video') if 'info' in locals() else 'Unknown Video'
                    message = f"Se descargó '{video_title}' exitosamente"
                
                print(f"Ruta de descarga generada: {filepath_in_static}")
                return jsonify({
                    'success': True, 
                    'filepath': filepath_in_static, 
                    'filename': filename,
                    'count': count,
                    'message': message
                })
            else:
                # Verificar si hay archivos de audio en la carpeta
                audio_extensions = ['*.mp3', '*.m4a', '*.webm', '*.ogg', '*.wav']
                all_audio_files = []
                for ext in audio_extensions:
                    all_audio_files.extend(glob.glob(f'{DOWNLOAD_FOLDER}/{ext}'))
                print(f"Archivos de audio encontrados: {all_audio_files}")
                return jsonify({'success': False, 'error': f'No se pudo descargar ningún archivo. Archivos de audio en carpeta: {len(all_audio_files)}'})
        except Exception as e:
            print(f"Error durante la descarga: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'No URL provided!'})

# La ruta /downloads/<filename> ahora está en app/__init__.py
