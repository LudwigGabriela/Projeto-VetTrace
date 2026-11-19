from database import get_db_connection


def service_criar_material(dados, usuario_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO kits (
            nome,
            descricao,
            tipo
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        dados["nome"],
        dados["descricao"],
        dados["tipo"],
    ))

    material_id = cur.fetchone()["id"]

    conn.commit()

    cur.close()
    conn.close()

    return material_id


def service_obter_materiais():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.id,
            r.nome,
            r.descricao,
            r.tipo,
            r.ativo
        FROM kits r
        ORDER BY r.id DESC
    """)

    materiais = cur.fetchall()

    cur.close()
    conn.close()

    return materiais



def service_editar_material(material_id, dados):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE kits
        SET
            nome = %s,
            descricao = %s,
            tipo = %s,
            ativo = %s
        WHERE id = %s
    """, (
        dados["nome"],
        dados["descricao"],
        dados["tipo"],
        dados["ativo"],
        material_id
    ))

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return False

    conn.commit()

    cur.close()
    conn.close()

    return True


def service_excluir_material(material_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM kits
        WHERE id = %s
    """, (material_id,))

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return False

    conn.commit()

    cur.close()
    conn.close()

    return True