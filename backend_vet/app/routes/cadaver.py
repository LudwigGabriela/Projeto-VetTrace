from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.cadaver_service import (
    service_criar_cadaver,
    service_obter_cadaveres,
    service_editar_cadaver,
    service_excluir_cadaver
)

cadaver_bp = Blueprint("cadaver", __name__)


@cadaver_bp.route("/cadaver", methods=["POST"])
@jwt_required()
def criar_cadaver():

    dados = request.json or {}

    identidade = get_jwt_identity()

    usuario_id = get_jwt_identity()  # Obtém o ID do usuário autenticado

    dados["registrado_por"] = int(usuario_id)

    cadaver_id = service_criar_cadaver(dados)

    return jsonify({
        "message": "Cadáver cadastrado com sucesso",
        "id": cadaver_id
    }), 201


@cadaver_bp.route("/cadaver", methods=["GET"])
def obter_cadaveres():

    cadaveres = service_obter_cadaveres()

    return jsonify(cadaveres), 200


@cadaver_bp.route("/cadaver/<int:cadaver_id>", methods=["PUT"])
@jwt_required()
def editar_cadaver(cadaver_id):

    dados = request.json or {}

    print("Usuário autenticado:", get_jwt_identity())
    print("ID do cadáver:", cadaver_id)
    print("Dados recebidos:", dados)

    sucesso = service_editar_cadaver(
        cadaver_id,
        dados
    )

    if not sucesso:
        return jsonify({
            "erro": "Cadáver não encontrado"
        }), 404

    return jsonify({
        "message": "Cadáver atualizado com sucesso",
        "id": cadaver_id
    }), 200


@cadaver_bp.route("/cadaver/<int:cadaver_id>", methods=["DELETE"])
@jwt_required()
def excluir_cadaver(cadaver_id):

    print("Usuário autenticado:", get_jwt_identity())
    print("ID do cadáver:", cadaver_id)

    sucesso = service_excluir_cadaver(cadaver_id)

    if not sucesso:
        return jsonify({
            "erro": "Cadáver não encontrado"
        }), 404

    return jsonify({
        "message": "Cadáver excluído com sucesso",
        "id": cadaver_id
    }), 200