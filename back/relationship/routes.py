from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from back.models import db, Character, CharacterRelationship
from back.utils import validate_required_fields

relationship = Blueprint("relationship", __name__)

@relationship.route('/relationship/<int:character_id>', methods=['GET'])
@jwt_required()
def get_relationships(character_id):
    user_id = get_jwt_identity()
    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    relationships = CharacterRelationship.query.filter_by(source_id=character.id).all()
    return jsonify({
        'message': 'Relaciones obtenidas correctamente',
        'relationships': [r.to_dict() for r in relationships]
    }), 200

@relationship.route('/relationship', methods=['POST'])
@jwt_required()
def create_relationship():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'source_id', 'target_id', 'relation_type')
    if not valid:
        return jsonify({'error': error}), 400

    source = Character.query.filter_by(id=data['source_id'], user_id=user_id).first()
    if not source:
        return jsonify({'error': 'Personaje no autorizado'}), 403

    relationship = CharacterRelationship(
        source_id=source.id,
        target_id=data['target_id'],
        relation_type=data['relation_type']
    )
    db.session.add(relationship)
    db.session.commit()

    return jsonify({
        'message': 'Relación creada correctamente',
        'relationship_id': relationship.id
    }), 201

@relationship.route('/relationship/<int:relationship_id>', methods=['DELETE'])
@jwt_required()
def delete_relationship(relationship_id):
    user_id = get_jwt_identity()
    relationship = CharacterRelationship.query.get(relationship_id)
    if not relationship:
        return jsonify({'error': 'Relación no encontrada'}), 404

    source = Character.query.filter_by(id=relationship.source_id, user_id=user_id).first()
    if not source:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(relationship)
    db.session.commit()
    return jsonify({
        'message': 'Relación eliminada correctamente',
        'relationship_id': relationship_id
    }), 200
