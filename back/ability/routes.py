from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from back.models import db, Character, Ability
from back.utils import validate_required_fields

ability = Blueprint("ability", __name__)

@ability.route('/ability/<int:character_id>', methods=['GET'])
@jwt_required()
def get_abilities(character_id):
    response = {}
    user_id = get_jwt_identity()

    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    abilities = Ability.query.filter_by(character_id=character.id).all()
    response['message'] = 'Habilidades obtenidas correctamente'
    response['abilities'] = [a.to_dict() for a in abilities]
    return jsonify(response), 200


@ability.route('/ability', methods=['POST'])
@jwt_required()
def create_ability():
    response = {}
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'character_id', 'name', 'description', 'uses_per_session')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    ability = Ability(
        character_id=character.id,
        name=data['name'],
        description=data['description'],
        image_url=data.get('image_url'),
        uses_per_session=data['uses_per_session'],
        used=data.get('used', False)
    )
    db.session.add(ability)
    db.session.commit()
    response['message'] = 'Habilidad creada correctamente'
    response['ability_id'] = ability.id
    return jsonify(response), 201


@ability.route('/ability/<int:ability_id>', methods=['PUT'])
@jwt_required()
def update_ability(ability_id):
    response = {}
    user_id = get_jwt_identity()
    ability = Ability.query.get(ability_id)
    if not ability:
        return jsonify({'error': 'Habilidad no encontrada'}), 404

    character = Character.query.filter_by(id=ability.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json() or {}
    for field in ['name', 'description', 'image_url', 'uses_per_session', 'used']:
        if field in data:
            setattr(ability, field, data[field])

    db.session.commit()
    response['message'] = 'Habilidad actualizada correctamente'
    response['ability_id'] = ability.id
    return jsonify(response), 200


@ability.route('/ability/<int:ability_id>', methods=['DELETE'])
@jwt_required()
def delete_ability(ability_id):
    response = {}
    user_id = get_jwt_identity()
    ability = Ability.query.get(ability_id)
    if not ability:
        return jsonify({'error': 'Habilidad no encontrada'}), 404

    character = Character.query.filter_by(id=ability.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(ability)
    db.session.commit()
    response['message'] = 'Habilidad eliminada correctamente'
    response['ability_id'] = ability_id
    return jsonify(response), 200


@ability.route('/ability/reset/<int:character_id>', methods=['POST'])
@jwt_required()
def reset_abilities(character_id):
    response = {}
    user_id = get_jwt_identity()

    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    abilities = Ability.query.filter_by(character_id=character.id).all()
    for ability in abilities:
        ability.used = False

    db.session.commit()
    response['message'] = 'Habilidades reiniciadas correctamente'
    response['character_id'] = character_id
    return jsonify(response), 200
