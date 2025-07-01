from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__, url_prefix='/')

@home_bp.route('/', methods=['GET'])
def index():
    cards = [
    {"title": "Files to Zip", "icon": "bi-file-zip", "url": "/compress/"},
    {"title": "Youtube to mp3", "icon": "bi-filetype-mp3", "url": "/youtube"},
    {"title": "Imgs to Pdf", "icon": "bi-image", "url": "/img_to_pdf/"},
    {"title": "Cbr to Pdf", "icon": "bi-file-pdf", "url": "/cbr_to_pdf/"},
    {"title": "MP3 to Wav", "icon": "bi-music-note", "url": "/mp3_to_wav/"},
    ]

    return render_template('home/index.html', cards=cards)