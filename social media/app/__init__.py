from flask import Flask

app = Flask(__name__)

UPLOAD_FOLDER = r'C:\Users\trade\Documents\python2\social media\app\static\img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'ico', 'ppm', 'pgm', 'pbm'}


from app import routes