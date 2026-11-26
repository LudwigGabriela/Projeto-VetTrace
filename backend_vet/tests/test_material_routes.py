
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.routes.material import material_bp


@pytest.fixture
def material_client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres"

    JWTManager(app)
    app.register_blueprint(material_bp)

    return app.test_client()


@pytest.fixture
def material_auth_headers(material_client):
    app = material_client.application

    with app.app_context():
        token = create_access_token(identity="1")

    return {"Authorization": f"Bearer {token}"}


def test_listar_materiais_com_sucesso(material_client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.material.service_obter_materiais",
        lambda: [{"id": 1, "nome": "Kit Cirúrgico"}]
    )

    resposta = material_client.get("/material")

    assert resposta.status_code == 200
    assert resposta.get_json()[0]["nome"] == "Kit Cirúrgico"


def test_cadastrar_material_sem_autenticacao(material_client):
    resposta = material_client.post(
        "/material",
        json={
            "nome": "Kit Cirúrgico",
            "descricao": "Kit de teste",
            "tipo": "Cirúrgico"
        }
    )

    assert resposta.status_code == 401


def test_cadastrar_material_com_sucesso(
    material_client, material_auth_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.routes.material.service_criar_material",
        lambda dados, usuario_id: 10
    )

    resposta = material_client.post(
        "/material",
        headers=material_auth_headers,
        json={
            "nome": "Kit Cirúrgico",
            "descricao": "Kit de teste",
            "tipo": "Cirúrgico"
        }
    )

    assert resposta.status_code == 201
    assert resposta.get_json()["id"] == 10


def test_editar_material_sem_autenticacao(material_client):
    resposta = material_client.put(
        "/material/1",
        json={}
    )

    assert resposta.status_code == 401


def test_editar_material_inexistente(
    material_client, material_auth_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.routes.material.service_editar_material",
        lambda material_id, dados: False
    )

    resposta = material_client.put(
        "/material/999",
        headers=material_auth_headers,
        json={}
    )

    assert resposta.status_code == 404


def test_editar_material_com_sucesso(
    material_client, material_auth_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.routes.material.service_editar_material",
        lambda material_id, dados: True
    )

    resposta = material_client.put(
        "/material/1",
        headers=material_auth_headers,
        json={
            "nome": "Kit Atualizado",
            "descricao": "Descrição atualizada",
            "tipo": "Cirúrgico",
            "ativo": True
        }
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["id"] == 1


def test_excluir_material_sem_autenticacao(material_client):
    resposta = material_client.delete("/material/1")

    assert resposta.status_code == 401


def test_excluir_material_inexistente(
    material_client, material_auth_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.routes.material.service_excluir_material",
        lambda material_id: False
    )

    resposta = material_client.delete(
        "/material/999",
        headers=material_auth_headers
    )

    assert resposta.status_code == 404


def test_excluir_material_com_sucesso(
    material_client, material_auth_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.routes.material.service_excluir_material",
        lambda material_id: True
    )

    resposta = material_client.delete(
        "/material/1",
        headers=material_auth_headers
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["id"] == 1
