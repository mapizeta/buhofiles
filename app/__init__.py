from flask import Flask
from .compress.routes import compress_bp, img_to_pdf_bp
from .home.routes import home_bp
from .youtube.routes import youtube_to_mp3_bp

def create_app():
    
    app = Flask(__name__, static_folder='static')

    app.register_blueprint(compress_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(img_to_pdf_bp)
    app.register_blueprint(youtube_to_mp3_bp)

    return app
