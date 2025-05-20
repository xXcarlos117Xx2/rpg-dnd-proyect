from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from back.models import db, Character, Spell
from back.utils import validate_required_fields

spell = Blueprint("spell", __name__)

@spell.route('/spell/<int:character_id>', methods=['GET'])
@jwt_required()
def get_spells(character_id):
    user_id = get_jwt_identity()
    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    spells = Spell.query.filter_by(character_id=character.id).all()
    return jsonify({
        'message': 'Hechizos obtenidos correctamente',
        'spells': [s.to_dict() for s in spells]
    }), 200

@spell.route('/spell', methods=['POST'])
@jwt_required()
def create_spell():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'character_id', 'name', 'type', 'description', 'uses', 'uses_max')
    if not valid:
        return jsonify({'error': error}), 400

    character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    spell = Spell(
        character_id=character.id,
        name=data['name'],
        type=data['type'],
        description=data['description'],
        uses=data['uses'],
        uses_max=data.get('uses_max', 1),
        image_url=data.get('image_url')
    )
    db.session.add(spell)
    db.session.commit()

    return jsonify({
        'message': 'Hechizo creado correctamente',
        'spell_id': spell.id
    }), 201

@spell.route('/spell/<int:spell_id>', methods=['PUT'])
@jwt_required()
def update_spell(spell_id):
    user_id = get_jwt_identity()
    spell = Spell.query.get(spell_id)
    if not spell:
        return jsonify({'error': 'Hechizo no encontrado'}), 404

    character = Character.query.filter_by(id=spell.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json() or {}
    for field in ['name', 'type', 'description', 'uses', 'image_url']:
        if field in data:
            setattr(spell, field, data[field])

    db.session.commit()
    return jsonify({
        'message': 'Hechizo actualizado correctamente',
        'spell_id': spell.id
    }), 200

@spell.route('/spell/<int:spell_id>', methods=['DELETE'])
@jwt_required()
def delete_spell(spell_id):
    user_id = get_jwt_identity()
    spell = Spell.query.get(spell_id)
    if not spell:
        return jsonify({'error': 'Hechizo no encontrado'}), 404

    character = Character.query.filter_by(id=spell.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(spell)
    db.session.commit()
    return jsonify({
        'message': 'Hechizo eliminado correctamente',
        'spell_id': spell_id
    }), 200

@spell.route('/spell/reset/<int:character_id>', methods=['POST'])
@jwt_required()
def reset_spells(character_id):
    user_id = get_jwt_identity()
    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    spells = Spell.query.filter_by(character_id=character.id).all()
    for spell in spells:
        spell.uses = spell.uses_max

    db.session.commit()
    return jsonify({
        'message': 'Hechizos reiniciados correctamente',
        'character_id': character_id
    }), 200

@spell.route('/spell/use/<int:spell_id>', methods=['POST'])
@jwt_required()
def use_spell(spell_id):
    user_id = get_jwt_identity()
    spell = Spell.query.get(spell_id)
    if not spell:
        return jsonify({'error': 'Hechizo no encontrado'}), 404

    character = Character.query.filter_by(id=spell.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    if spell.uses <= 0:
        return jsonify({'error': 'El hechizo no tiene usos restantes'}), 400

    spell.uses -= 1
    db.session.commit()
    return jsonify({
        'message': 'Hechizo usado correctamente',
        'spell_id': spell.id,
        'remaining_uses': spell.uses
    }), 200
