from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from back.models import db, Character, Condition
from back.utils import validate_required_fields

condition = Blueprint("condition", __name__)

@condition.route('/condition/<int:character_id>', methods=['GET'])
@jwt_required()
def get_conditions(character_id):
    user_id = get_jwt_identity()
    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    conditions = Condition.query.filter_by(character_id=character.id).all()
    return jsonify({
        'message': 'Condiciones obtenidas correctamente',
        'conditions': [c.to_dict() for c in conditions]
    }), 200

@condition.route('/condition', methods=['POST'])
@jwt_required()
def create_condition():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'character_id', 'name', 'description')
    if not valid:
        return jsonify({'error': error}), 400

    character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    condition = Condition(
        character_id=character.id,
        name=data['name'],
        description=data['description'],
        temporary=data.get('temporary', True)
    )
    db.session.add(condition)
    db.session.commit()

    return jsonify({
        'message': 'Condición creada correctamente',
        'condition_id': condition.id
    }), 201

@condition.route('/condition/<int:condition_id>', methods=['DELETE'])
@jwt_required()
def delete_condition(condition_id):
    user_id = get_jwt_identity()
    condition = Condition.query.get(condition_id)
    if not condition:
        return jsonify({'error': 'Condición no encontrada'}), 404

    character = Character.query.filter_by(id=condition.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(condition)
    db.session.commit()

    return jsonify({
        'message': 'Condición eliminada correctamente',
        'condition_id': condition_id
    }), 200
