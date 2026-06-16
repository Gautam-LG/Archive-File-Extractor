import pytest
import zipfile

from app import create_app

from app.models import db

@pytest.fixture
def app():
    flask_app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'TESTING': True
    })
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_zip(tmp_path):
    zpath = tmp_path / "sample.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("a.txt", "hello")
        zf.writestr("b.json", "{}")
        zf.writestr("sub/c.json", '{"x":1}')
    return str(zpath)

@pytest.fixture
def nested_zip(tmp_path):
    inner_path = tmp_path / "inner.zip"
    with zipfile.ZipFile(inner_path, "w") as zf:
        zf.writestr("deep.json", '{"deep":true}')
        zf.writestr("deep.txt", "text")

    outer_path = tmp_path / "nested.zip"
    with zipfile.ZipFile(outer_path, "w") as zf:
        zf.writestr("top.json", "{}")
        zf.write(inner_path, "inner.zip")
    return str(outer_path)
