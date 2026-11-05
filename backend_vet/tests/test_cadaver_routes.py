def test_listar_cadaveres(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.cadaver.service_obter_cadaveres",
        lambda: [{"id": 1}],
    )
    resposta = client.get("/cadaver")
    assert resposta.status_code == 200
    assert resposta.get_json() == [{"id": 1}]


def test_criar_cadaver_sem_token_retorna_401(client):
    resposta = client.post("/cadaver", json={"nome": "Rex"})
    assert resposta.status_code == 401


def test_criar_cadaver_registra_usuario_logado(client, auth_headers, monkeypatch):
    recebido = {}

    def service_falso(dados):
        recebido.update(dados)
        return 7

    monkeypatch.setattr("app.routes.cadaver.service_criar_cadaver", service_falso)

    resposta = client.post("/cadaver", json={"nome": "Rex"}, headers=auth_headers)

    assert resposta.status_code == 201
    assert resposta.get_json()["id"] == 7
    assert recebido["registrado_por"] == 1


def test_editar_cadaver_inexistente_retorna_404(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.routes.cadaver.service_editar_cadaver",
        lambda cadaver_id, dados: False,
    )
    resposta = client.put("/cadaver/5", json={}, headers=auth_headers)
    assert resposta.status_code == 404


def test_excluir_cadaver_com_sucesso(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.routes.cadaver.service_excluir_cadaver",
        lambda cadaver_id: True,
    )
    resposta = client.delete("/cadaver/5", headers=auth_headers)
    assert resposta.status_code == 200
