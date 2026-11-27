
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from app.routes.auth import auth_bp


class CursorFalso:
    def __init__(self, resultados):
        self.resultados = resultados

    def execute(self, query, parametros=None):
        pass

    def fetchone(self):
        if self.resultados:
            return self.resultados.pop(0)
        return None

    def close(self):
        pass


class ConexaoFalsa:
    def __init__(self, resultados):
        self.cursor_falso = CursorFalso(resultados)
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self.cursor_falso

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


@pytest.fixture
def auth_client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres"

    JWTManager(app)
    app.register_blueprint(auth_bp)

    return app.test_client()


def test_cadastro_com_campos_obrigatorios_ausentes(auth_client):
    resposta = auth_client.post(
        "/api/auth/cadastro",
        json={}
    )

    assert resposta.status_code == 400


def test_cadastro_com_senhas_diferentes(auth_client):
    resposta = auth_client.post(
        "/api/auth/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "teste@vettrace.com",
            "cargo": "Administrador",
            "senha": "senha123",
            "confirmar_senha": "senha456"
        }
    )

    assert resposta.status_code == 400


def test_cadastro_com_email_ja_existente(auth_client, monkeypatch):
    conexao = ConexaoFalsa([
        (1,)
    ])

    monkeypatch.setattr(
        "app.routes.auth.get_db_connection",
        lambda: conexao
    )

    resposta = auth_client.post(
        "/api/auth/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "existente@vettrace.com",
            "cargo": "Administrador",
            "senha": "senha123",
            "confirmar_senha": "senha123"
        }
    )

    assert resposta.status_code == 400
    assert conexao.committed is False


def test_login_com_campos_ausentes(auth_client):
    resposta = auth_client.post(
        "/api/auth/login",
        json={}
    )

    assert resposta.status_code == 400


def test_login_com_usuario_inexistente(auth_client, monkeypatch):
    conexao = ConexaoFalsa([
        None
    ])

    monkeypatch.setattr(
        "app.routes.auth.get_db_connection",
        lambda: conexao
    )

    resposta = auth_client.post(
        "/api/auth/login",
        json={
            "email": "inexistente@vettrace.com",
            "senha": "senha123"
        }
    )

    assert resposta.status_code == 401


def test_cadastro_com_sucesso(auth_client, monkeypatch):
    conexao = ConexaoFalsa([
        None,
        (10, "Usuario Teste", "novo@vettrace.com", "admin")
    ])

    monkeypatch.setattr(
        "app.routes.auth.get_db_connection",
        lambda: conexao
    )

    resposta = auth_client.post(
        "/api/auth/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "novo@vettrace.com",
            "cargo": "Administrador",
            "senha": "senha123",
            "confirmar_senha": "senha123"
        }
    )

    assert resposta.status_code == 201
    assert resposta.get_json()["usuario"]["id"] == 10
    assert resposta.get_json()["usuario"]["perfil"] == "admin"
    assert conexao.committed is True


def test_login_com_sucesso(auth_client, monkeypatch):
    senha_hash = generate_password_hash("senha123")

    conexao = ConexaoFalsa([
        (
            1,
            "Usuario Teste",
            "teste@vettrace.com",
            senha_hash,
            "admin",
            "11999999999",
            None,
            True
        )
    ])

    monkeypatch.setattr(
        "app.routes.auth.get_db_connection",
        lambda: conexao
    )

    resposta = auth_client.post(
        "/api/auth/login",
        json={
            "email": "teste@vettrace.com",
            "senha": "senha123"
        }
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["usuario"]["id"] == 1
    assert dados["usuario"]["perfil"] == "admin"
    assert dados["token"]


def test_login_com_senha_incorreta(auth_client, monkeypatch):
    senha_hash = generate_password_hash("senha_correta")

    conexao = ConexaoFalsa([
        (
            1,
            "Usuario Teste",
            "teste@vettrace.com",
            senha_hash,
            "admin",
            "11999999999",
            None,
            True
        )
    ])

    monkeypatch.setattr(
        "app.routes.auth.get_db_connection",
        lambda: conexao
    )

    resposta = auth_client.post(
        "/api/auth/login",
        json={
            "email": "teste@vettrace.com",
            "senha": "senha_errada"
        }
    )

    assert resposta.status_code == 401


def test_login_com_usuario_inativo(auth_client, monkeypatch):
    senha_hash = generate_password_hash("senha123")

    conexao = ConexaoFalsa([
        (
            1,
            "Usuario Teste",
            "teste@vettrace.com",
            senha_hash,
            "admin",
            "11999999999",
            None,
            False
        )
    ])

    monkeypatch.setattr(
        "app.routes.auth.get_db_connection",
        lambda: conexao
    )

    resposta = auth_client.post(
        "/api/auth/login",
        json={
            "email": "teste@vettrace.com",
            "senha": "senha123"
        }
    )

    assert resposta.status_code == 401
