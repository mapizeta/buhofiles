from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Debugging: verificar carpetas
    downloads_path = os.path.join(os.path.dirname(__file__), 'app', 'static', 'downloads')
    print(f"Ruta de descargas: {downloads_path}")
    print(f"¿Existe la carpeta?: {os.path.exists(downloads_path)}")
    if os.path.exists(downloads_path):
        try:
            files = os.listdir(downloads_path)
            print(f"Archivos en la carpeta: {files}")
        except Exception as e:
            print(f"Error al listar archivos: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
