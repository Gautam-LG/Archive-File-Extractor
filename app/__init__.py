from flask import Flask
from app.models import db
from .config import SQLALCHEMY_DATABASE_URI, CONCURRENCY
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=CONCURRENCY)

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import bp
    app.register_blueprint(bp)

    return app