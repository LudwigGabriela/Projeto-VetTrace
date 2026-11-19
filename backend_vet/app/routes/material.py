
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.material_service import (
    service_criar_material,
    service_obter_materiais,
    service_editar_material,
    service_excluir_material
)

material_bp = Blueprint("material", __name__)


@material_bp.route("/material", methods=["POST"])
@jwt_required()
def criar_material():

    dados = request.json or {}

    usuario_id = get_jwt_identity()

    print("Usuário autenticado:", usuario_id)
    print("Dados recebidos:", dados)

    material_id = service_criar_material(
        dados,
        int(usuario_id)
    )

    return jsonify({
        "message": "Material cadastrado com sucesso",
        "id": material_id
    }), 201


@material_bp.route("/material", methods=["GET"])
def obter_materiais():

    materiais = service_obter_materiais()

    return jsonify(materiais), 200


@material_bp.route("/material/<int:material_id>", methods=["PUT"])
@jwt_required()
def editar_material(material_id):

    dados = request.json or {}

    print("Usuário autenticado:", get_jwt_identity())
    print("ID do material:", material_id)
    print("Dados recebidos:", dados)

    sucesso = service_editar_material(
        material_id,
        dados
    )

    if not sucesso:
        return jsonify({
            "erro": "Material não encontrado"
        }), 404

    return jsonify({
        "message": "Material atualizado com sucesso",
        "id": material_id
    }), 200


@material_bp.route("/material/<int:material_id>", methods=["DELETE"])
@jwt_required()
def excluir_material(material_id):

    print("Usuário autenticado:", get_jwt_identity())
    print("ID do material:", material_id)

    sucesso = service_excluir_material(material_id)

    if not sucesso:
        return jsonify({
            "erro": "Material não encontrado"
        }), 404

    return jsonify({
        "message": "Material excluído com sucesso",
        "id": material_id
    }), 200
