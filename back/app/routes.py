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

from flask import request, jsonify
from .models import Character, Stat, db

@api.route('/character', methods=['GET', 'POST', 'PUT', 'DELETE'])
def character_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)

    # GET
    if request.method == 'GET':
        if character_id:
            character = Character.query.get_or_404(character_id)
            response['message'] = 'Success'
            response['character'] = character.to_dict(include_relationships=True)
            return jsonify(response), 200
        else:
            characters = Character.query.all()
            response['message'] = 'Success'
            response['characters'] = [
                char.to_dict(include_relationships=True) for char in characters
            ]
            return jsonify(response), 200

    # POST
    elif request.method == 'POST':
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
        db.session.flush()

        stats_data = data.get('stats', {})
        default_stats = {
            'FUE': stats_data.get('FUE', 0),
            'AGI': stats_data.get('AGI', 0),
            'MEN': stats_data.get('MEN', 0),
            'CAR': stats_data.get('CAR', 0),
        }

        for stat_name, value in default_stats.items():
            db.session.add(Stat(name=stat_name, value=value, character_id=character.id))

        db.session.commit()
        response['message'] = 'Personaje creado correctamente'
        response['character_id'] = character.id
        return jsonify(response), 201

    # PUT
    elif request.method == 'PUT':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para actualizar'
            return jsonify(response), 400

        data = request.get_json()
        if not data:
            response['error'] = 'Invalid body'
            return jsonify(response), 400

        character = Character.query.get_or_404(character_id)

        valid, error = validate_required_fields(data, 'name', 'race', 'goal', 'background')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        for field in ['name', 'race', 'goal', 'background', 'level',
                      'health_current', 'health_max', 'mana_current', 'mana_max', 'image_url']:
            if field in data:
                setattr(character, field, data[field])

        db.session.commit()
        response['message'] = 'Personaje actualizado correctamente'
        response['character_id'] = character.id
        return jsonify(response), 200

    # DELETE
    elif request.method == 'DELETE':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para eliminar'
            return jsonify(response), 400

        character = Character.query.get_or_404(character_id)
        db.session.delete(character)
        db.session.commit()
        response['message'] = 'Personaje eliminado correctamente'
        response['character_id'] = character_id
        return jsonify(response), 200
