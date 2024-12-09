from flask import Flask
from .compress.routes import compress_bp

def create_app():
    
    app = Flask(__name__, static_folder='static')
    print(f"Static folder: {app.static_folder}")
    # Registrar el Blueprint de compresión
    app.register_blueprint(compress_bp)

    return app
