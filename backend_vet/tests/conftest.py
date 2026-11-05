import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.routes.residuo import residuo_bp
from app.routes.cadaver import cadaver_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres"
    JWTManager(app)
    app.register_blueprint(residuo_bp)
    app.register_blueprint(cadaver_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {token}"}
