
import os

import psycopg2
import pytest

from app.services import material_service


def conectar_banco_teste():
    return psycopg2.connect(os.environ["TEST_DATABASE_URL"])


@pytest.fixture
def ambiente_material(monkeypatch):
    monkeypatch.setattr(
        material_service,
        "get_db_connection",
        conectar_banco_teste
    )

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM kits
        WHERE nome LIKE 'TESTE_INTEGRACAO_MATERIAL_%'
    """)

    conn.commit()
    cur.close()
    conn.close()

    yield

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM kits
        WHERE nome LIKE 'TESTE_INTEGRACAO_MATERIAL_%'
    """)

    conn.commit()
    cur.close()
    conn.close()


def test_criar_material_no_banco(ambiente_material):
    dados = {
        "nome": "TESTE_INTEGRACAO_MATERIAL_CRIAR",
        "descricao": "Material criado pelo teste",
        "tipo": "cirurgico"
    }

    material_id = material_service.service_criar_material(
        dados,
        1
    )

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT nome, descricao, tipo, ativo FROM kits WHERE id = %s",
        (material_id,)
    )

    material = cur.fetchone()

    cur.close()
    conn.close()

    assert material is not None
    assert material[0] == dados["nome"]
    assert material[1] == dados["descricao"]
    assert material[2] == dados["tipo"]
    assert material[3] is True


def test_listar_materiais_do_banco(ambiente_material):
    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO kits (nome, descricao, tipo)
        VALUES (%s, %s, %s)
    """, (
        "TESTE_INTEGRACAO_MATERIAL_LISTAR",
        "Material para listagem",
        "cirurgico"
    ))

    conn.commit()
    cur.close()
    conn.close()

    materiais = material_service.service_obter_materiais()

    assert any(
        material["nome"] == "TESTE_INTEGRACAO_MATERIAL_LISTAR"
        for material in materiais
    )


def test_editar_material_no_banco(ambiente_material):
    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO kits (nome, descricao, tipo)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        "TESTE_INTEGRACAO_MATERIAL_EDITAR",
        "Descrição original",
        "cirurgico"
    ))

    material_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    sucesso = material_service.service_editar_material(
        material_id,
        {
            "nome": "TESTE_INTEGRACAO_MATERIAL_EDITADO",
            "descricao": "Descrição atualizada",
            "tipo": "esterilizacao",
            "ativo": False
        }
    )

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT nome, descricao, tipo, ativo FROM kits WHERE id = %s",
        (material_id,)
    )

    material = cur.fetchone()

    cur.close()
    conn.close()

    assert sucesso is True
    assert material[0] == "TESTE_INTEGRACAO_MATERIAL_EDITADO"
    assert material[1] == "Descrição atualizada"
    assert material[2] == "esterilizacao"
    assert material[3] is False


def test_editar_material_inexistente(ambiente_material):
    sucesso = material_service.service_editar_material(
        999999999,
        {
            "nome": "Material inexistente",
            "descricao": "Teste",
            "tipo": "cirurgico",
            "ativo": True
        }
    )

    assert sucesso is False


def test_excluir_material_do_banco(ambiente_material):
    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO kits (nome, descricao, tipo)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        "TESTE_INTEGRACAO_MATERIAL_EXCLUIR",
        "Material para exclusão",
        "cirurgico"
    ))

    material_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    sucesso = material_service.service_excluir_material(material_id)

    conn = conectar_banco_teste()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM kits WHERE id = %s",
        (material_id,)
    )

    material = cur.fetchone()

    cur.close()
    conn.close()

    assert sucesso is True
    assert material is None


def test_excluir_material_inexistente(ambiente_material):
    sucesso = material_service.service_excluir_material(999999999)

    assert sucesso is False
