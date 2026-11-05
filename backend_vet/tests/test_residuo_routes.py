def test_listar_residuos_sem_filtro(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.residuo.service_obter_residuos",
        lambda: [{"id": 1}, {"id": 2}],
    )
    resposta = client.get("/residuo")
    assert resposta.status_code == 200
    assert len(resposta.get_json()) == 2


def test_listar_residuos_por_mes(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.residuo.service_obter_residuos_mes",
        lambda mes, ano: [{"mes": mes, "ano": ano}],
    )
    resposta = client.get("/residuo?mes=5&ano=2025")
    assert resposta.status_code == 200
    assert resposta.get_json() == [{"mes": 5, "ano": 2025}]


def test_peso_total(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.residuo.service_obter_peso_total", lambda: 42.5
    )
    resposta = client.get("/residuo/peso-total")
    assert resposta.status_code == 200
    assert resposta.get_json()["peso_total"] == 42.5


def test_criar_residuo_sem_token_retorna_401(client):
    resposta = client.post("/residuo", json={"peso": 10})
    assert resposta.status_code == 401


def test_criar_residuo_com_token(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.routes.residuo.service_criar_residuo",
        lambda dados, usuario_id: 99,
    )
    resposta = client.post("/residuo", json={"peso": 10}, headers=auth_headers)
    assert resposta.status_code == 201
    assert resposta.get_json()["id"] == 99


def test_editar_residuo_inexistente_retorna_404(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.routes.residuo.service_editar_residuo",
        lambda residuo_id, dados: False,
    )
    resposta = client.put("/residuo/123", json={"peso": 5}, headers=auth_headers)
    assert resposta.status_code == 404


def test_excluir_residuo_com_sucesso(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.routes.residuo.service_excluir_residuo",
        lambda residuo_id: True,
    )
    resposta = client.delete("/residuo/1", headers=auth_headers)
    assert resposta.status_code == 200
