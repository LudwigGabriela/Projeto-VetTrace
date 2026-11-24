
import os

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from app.services import residuo_service


def conectar_banco_teste():
    """Abre conexão exclusiva com o banco de integração."""
    url = os.environ["TEST_DATABASE_URL"]

    return psycopg2.connect(
        url,
        cursor_factory=RealDictCursor
    )


@pytest.fixture(autouse=True)
def configurar_banco_teste(monkeypatch):
    """
    Direciona os serviços para o banco vettrace_test
    e limpa os registros criados pelos testes.
    """

    monkeypatch.setattr(
        residuo_service,
        "get_db_connection",
        conectar_banco_teste
    )

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM residuos
        WHERE descricao LIKE 'TESTE_INTEGRACAO_%'
    """)

    conn.commit()
    cur.close()
    conn.close()

    yield

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM residuos
        WHERE descricao LIKE 'TESTE_INTEGRACAO_%'
    """)

    conn.commit()
    cur.close()
    conn.close()


def dados_residuo(descricao):
    """Monta os dados utilizados nos testes."""

    return {
        "tipo_grupo": "B",
        "descricao": descricao,
        "quantidade": 12.50,
        "unidade": "kg",
        "data_registro": "2026-11-24 10:00:00",
        "setor_gerador": "Laboratório",
        "setor_destino": "Armazenamento"
    }


def test_criar_residuo_no_banco():
    dados = dados_residuo("TESTE_INTEGRACAO_CRIACAO")

    residuo_id = residuo_service.service_criar_residuo(
        dados,
        None
    )

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM residuos WHERE id = %s",
        (residuo_id,)
    )

    resultado = cur.fetchone()

    cur.close()
    conn.close()

    assert resultado is not None
    assert resultado["descricao"] == dados["descricao"]
    assert float(resultado["quantidade"]) == 12.50


def test_listar_residuos_do_banco():
    dados = dados_residuo("TESTE_INTEGRACAO_LISTAGEM")

    residuo_service.service_criar_residuo(dados, None)

    resultado = residuo_service.service_obter_residuos()

    encontrado = any(
        item["descricao"] == dados["descricao"]
        for item in resultado
    )

    assert encontrado is True


def test_editar_residuo_no_banco():
    dados = dados_residuo("TESTE_INTEGRACAO_EDICAO")

    residuo_id = residuo_service.service_criar_residuo(
        dados,
        None
    )

    novos_dados = dados_residuo(
        "TESTE_INTEGRACAO_EDICAO_ATUALIZADA"
    )
    novos_dados["quantidade"] = 25.00

    resultado = residuo_service.service_editar_residuo(
        residuo_id,
        novos_dados
    )

    assert resultado is True

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM residuos WHERE id = %s",
        (residuo_id,)
    )

    registro = cur.fetchone()

    cur.close()
    conn.close()

    assert registro["descricao"] == novos_dados["descricao"]
    assert float(registro["quantidade"]) == 25.00


def test_excluir_residuo_do_banco():
    dados = dados_residuo("TESTE_INTEGRACAO_EXCLUSAO")

    residuo_id = residuo_service.service_criar_residuo(
        dados,
        None
    )

    resultado = residuo_service.service_excluir_residuo(
        residuo_id
    )

    assert resultado is True

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM residuos WHERE id = %s",
        (residuo_id,)
    )

    registro = cur.fetchone()

    cur.close()
    conn.close()

    assert registro is None



def test_obter_residuos_por_mes():
    dados = dados_residuo("TESTE_INTEGRACAO_MENSAL")

    residuo_service.service_criar_residuo(dados, None)

    resultado = residuo_service.service_obter_residuos_mes(
        11,
        2026
    )

    encontrado = any(
        item["descricao"] == dados["descricao"]
        for item in resultado
    )

    assert encontrado is True


def test_obter_peso_total():
    dados1 = dados_residuo("TESTE_INTEGRACAO_PESO_1")
    dados2 = dados_residuo("TESTE_INTEGRACAO_PESO_2")

    dados1["quantidade"] = 10.00
    dados2["quantidade"] = 15.50

    residuo_service.service_criar_residuo(dados1, None)
    residuo_service.service_criar_residuo(dados2, None)

    resultado = residuo_service.service_obter_peso_total()

    assert float(resultado) == 25.50
