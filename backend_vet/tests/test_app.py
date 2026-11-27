
from app import create_app


def test_criar_aplicacao_com_sucesso():
    app = create_app()

    assert app is not None
    assert app.config["TESTING"] is False


def test_rota_inicial():
    app = create_app()
    client = app.test_client()

    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.get_json() == {
        "mensagem": "API do VetTrace rodando com sucesso!"
    }


def test_rota_teste():
    app = create_app()
    client = app.test_client()

    resposta = client.get("/teste")

    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "ok"


def test_blueprints_registrados():
    app = create_app()

    blueprints_esperados = {
        "auth",
        "residuo",
        "cadaver",
        "material"
    }

    assert blueprints_esperados.issubset(
        set(app.blueprints.keys())
    )
