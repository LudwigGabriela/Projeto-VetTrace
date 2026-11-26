
import os

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from app.services import cadaver_service


EMAIL_TESTE = "teste_integracao_cadaver@vettrace.local"
IDENTIFICACAO_TESTE = "TESTE_INTEGRACAO_CADAVER_"


def conectar_banco_teste():
    """Abre conexão exclusiva com vettrace_test."""
    return psycopg2.connect(
        os.environ["TEST_DATABASE_URL"],
        cursor_factory=RealDictCursor
    )


@pytest.fixture
def ambiente_cadaver(monkeypatch):
    """Configura o banco e prepara um usuário exclusivo para os testes."""

    monkeypatch.setattr(
        cadaver_service,
        "get_db_connection",
        conectar_banco_teste
    )

    conn = conectar_banco_teste()
    cur = conn.cursor()

    # Remove possíveis registros de execuções anteriores.
    cur.execute("""
        DELETE FROM cadaveres
        WHERE identificacao LIKE %s
    """, (IDENTIFICACAO_TESTE + "%",))

    cur.execute("""
        DELETE FROM usuarios
        WHERE email = %s
    """, (EMAIL_TESTE,))

    # Cria usuário necessário para a chave estrangeira.
    cur.execute("""
        INSERT INTO usuarios (
            nome,
            email,
            senha_hash,
            perfil
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        "Usuário de Teste",
        EMAIL_TESTE,
        "hash_teste_integracao",
        "tecnico"
    ))

    usuario_id = cur.fetchone()["id"]

    conn.commit()
    cur.close()
    conn.close()

    yield usuario_id

    # Limpa os registros criados pelos testes.
    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM cadaveres
        WHERE identificacao LIKE %s
    """, (IDENTIFICACAO_TESTE + "%",))

    cur.execute("""
        DELETE FROM usuarios
        WHERE email = %s
    """, (EMAIL_TESTE,))

    conn.commit()
    cur.close()
    conn.close()


def dados_cadaver(usuario_id, identificacao):
    """Monta os dados utilizados nos testes."""

    return {
        "especie": "Canina",
        "identificacao": identificacao,
        "idade_anos": 5,
        "peso_kg": 12.50,
        "data_entrada": "2026-11-24 10:00:00",
        "status": "congelado",
        "observacoes": "Registro de teste de integração",
        "registrado_por": usuario_id,
        "nome_proprietario": "Proprietário de Teste",
        "causa_obito": "Causa de teste",
        "destino_id": None,
        "data_saida": None
    }


def test_criar_cadaver_no_banco(ambiente_cadaver):
    dados = dados_cadaver(
        ambiente_cadaver,
        IDENTIFICACAO_TESTE + "CRIACAO"
    )

    cadaver_id = cadaver_service.service_criar_cadaver(dados)

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM cadaveres WHERE id = %s",
        (cadaver_id,)
    )

    resultado = cur.fetchone()

    cur.close()
    conn.close()

    assert resultado is not None
    assert resultado["especie"] == "Canina"
    assert resultado["identificacao"] == dados["identificacao"]
    assert float(resultado["peso_kg"]) == 12.50


def test_listar_cadaveres_do_banco(ambiente_cadaver):
    dados = dados_cadaver(
        ambiente_cadaver,
        IDENTIFICACAO_TESTE + "LISTAGEM"
    )

    cadaver_service.service_criar_cadaver(dados)

    resultado = cadaver_service.service_obter_cadaveres()

    encontrado = any(
        item["identificacao"] == dados["identificacao"]
        for item in resultado
    )

    assert encontrado is True


def test_editar_cadaver_no_banco(ambiente_cadaver):
    dados = dados_cadaver(
        ambiente_cadaver,
        IDENTIFICACAO_TESTE + "EDICAO"
    )

    cadaver_id = cadaver_service.service_criar_cadaver(dados)

    novos_dados = dados_cadaver(
        ambiente_cadaver,
        IDENTIFICACAO_TESTE + "EDICAO_ATUALIZADA"
    )
    novos_dados["peso_kg"] = 18.75
    novos_dados["status"] = "aguardando_retirada"

    resultado = cadaver_service.service_editar_cadaver(
        cadaver_id,
        novos_dados
    )

    assert resultado is True

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM cadaveres WHERE id = %s",
        (cadaver_id,)
    )

    registro = cur.fetchone()

    cur.close()
    conn.close()

    assert registro["identificacao"] == novos_dados["identificacao"]
    assert float(registro["peso_kg"]) == 18.75
    assert registro["status"] == "aguardando_retirada"


def test_excluir_cadaver_do_banco(ambiente_cadaver):
    dados = dados_cadaver(
        ambiente_cadaver,
        IDENTIFICACAO_TESTE + "EXCLUSAO"
    )

    cadaver_id = cadaver_service.service_criar_cadaver(dados)

    resultado = cadaver_service.service_excluir_cadaver(cadaver_id)

    assert resultado is True

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM cadaveres WHERE id = %s",
        (cadaver_id,)
    )

    registro = cur.fetchone()

    cur.close()
    conn.close()

    assert registro is None
