from flask import Flask
from app.models import db
from config import SQLALCHEMY_DATABASE_URI, CONCURRENCY
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=CONCURRENCY)

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app