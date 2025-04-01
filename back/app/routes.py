from flask import Blueprint, jsonify, request
from .models import Character, Stat, db

api = Blueprint('api', __name__, url_prefix='/api')

# Auxiliary functions
def validate_required_fields(data, *fields):
    missing = [field for field in fields if not data.get(field)]
    if missing:
        return False, f'Faltan los siguientes campos: {", ".join(missing)}'
    return True, None


# Endpoints characters
@api.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"})

@api.route('/get_characters', methods=['GET'])
def get_characters():
    response = {}
    characters = Character.query.all()
    response['message'] = 'Success'
    response['characters'] = [character.to_dict() for character in characters]
    return jsonify(response), 200

@api.route('/get_character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    response = {}
    character = Character.query.get_or_404(character_id)
    response['message'] = 'Success'
    response['character'] = character.to_dict()
    return jsonify(response), 200

@api.route('/create_character', methods=['POST'])
def create_character():
    response = {}
    data = request.get_json() or {}
    valid, error = validate_required_fields(data, 'name', 'race', 'goal', 'background')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    character = Character(
        name=data['name'],
        race=data['race'],
        goal=data['goal'],
        background=data['background'],
        level=data.get('level', 1),
        health_current=data.get('health_current', 6),
        health_max=data.get('health_max', 6),
        mana_current=data.get('mana_current', 3),
        mana_max=data.get('mana_max', 3),
        image_url=data.get('image_url')
    )

    db.session.add(character)
    db.session.flush()  # <-- Necesario para que character.id esté disponible

    stats_data = data.get('stats', {})
    default_stats = {
        'FUE': stats_data.get('FUE', 0),
        'AGI': stats_data.get('AGI', 0),
        'MEN': stats_data.get('MEN', 0),
        'CAR': stats_data.get('CAR', 0),
    }

    for stat_name, value in default_stats.items():
        stat = Stat(name=stat_name, value=value, character_id=character.id)
        db.session.add(stat)

    db.session.commit()
    response['message'] = 'Personaje creado correctamente'
    response['character_id'] = character.id
    return jsonify(response), 201

@api.route('/update_character/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    response = {}
    data = request.get_json() or {}
    character = Character.query.get_or_404(character_id)
    valid, error = validate_required_fields(data, 'name', 'race', 'goal', 'background')
    if not valid:
        return jsonify({'error': error}), 400
    fields_to_update = [
        'name', 'race', 'goal', 'background', 'level',
        'health_current', 'health_max', 'mana_current', 'mana_max', 'image_url'
    ]
    for field in fields_to_update:
        if field in data:
            setattr(character, field, data[field])
    db.session.commit()
    response['message'] = 'Personaje actualizado correctamente'
    return jsonify(response), 200

@api.route('/delete_character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    response = {}
    character = Character.query.get_or_404(character_id)
    db.session.delete(character)
    db.session.commit()
    response['message'] = 'Personaje eliminado correctamente'
    return jsonify(), 200