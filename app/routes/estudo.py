from flask import Blueprint, request, jsonify
from flask import current_app

# Defina e exponha o blueprint com o nome esperado
estudo_bp = Blueprint(
    'estudo',             # identificador interno do Blueprint
    __name__,             # módulo em que ele está definido
    url_prefix='/estudo'  # caminho base para as rotas de estudo
)

@estudo_bp.route('/', methods=['GET'])
def list_estudos():
    # lógica para retornar todos os planos de estudo, por exemplo
    return jsonify([...])

@estudo_bp.route('/<int:id>', methods=['GET'])
def get_estudo(id):
    # lógica para retornar um estudo específico
    return jsonify({...})
