from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from back.models import Character, Stat, db
from back.utils import validate_required_fields

character = Blueprint("character", __name__)

@character.route('/character', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def character_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)

    if request.method == 'GET':
        if character_id:
            character = Character.query.filter_by(id=character_id, user_id=user_id).first()
            if not character:
                response['error'] = 'Personaje no encontrado'
                return jsonify(response), 404
            response['message'] = 'Success'
            response['character'] = character.to_dict(include_relationships=True)
        else:
            characters = Character.query.filter_by(user_id=user_id).all()
            response['message'] = 'Success'
            response['characters'] = [c.to_dict(include_relationships=True) for c in characters]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'name', 'race', 'goal', 'background')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        stats_data = data.get('stats', {})
        default_stats = {'FUE': 0, 'AGI': 0, 'MEN': 0, 'CAR': 0}
        default_stats.update(stats_data)

        fuerza = default_stats.get('FUE', 0)
        mente = default_stats.get('MEN', 0)

        character = Character(
            name=data['name'],
            user_id=user_id,
            race=data['race'],
            goal=data['goal'],
            background=data['background'],
            level=data.get('level', 1),
            health_current=data.get('health_current', 6 + fuerza),
            health_max=data.get('health_max', 6 + fuerza),
            mana_current=data.get('mana_current', 3 + mente),
            mana_max=data.get('mana_max', 3 + mente),
            image_url=data.get('image_url')
        )
        db.session.add(character)
        db.session.flush()  

        for stat_name, value in default_stats.items():
            db.session.add(Stat(name=stat_name, value=value, character_id=character.id))

        db.session.commit()
        response['message'] = 'Personaje creado correctamente'
        response['character_id'] = character.id
        return jsonify(response), 201

    elif request.method == 'PUT':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        data = request.get_json() or {}
        for field in ['name', 'race', 'goal', 'background', 'level', 'health_current', 'health_max', 'mana_current', 'mana_max', 'image_url']:
            if field in data:
                setattr(character, field, data[field])

        db.session.commit()
        response['message'] = 'Personaje actualizado correctamente'
        response['character_id'] = character.id
        return jsonify(response), 200

    elif request.method == 'DELETE':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        db.session.delete(character)
        db.session.commit()
        response['message'] = 'Personaje eliminado correctamente'
        response['character_id'] = character_id
        return jsonify(response), 200
