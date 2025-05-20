from flask import Blueprint, request, jsonify
from back.models import Character
import random

misc = Blueprint("misc", __name__)

@misc.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"})

@misc.route('/roll', methods=['GET'])
def roll_handler():
    response = {}

    character_id = request.args.get('character_id', type=int)
    stat_name = request.args.get('stat', type=str)
    difficulty = request.args.get('difficulty', type=int)

    if not character_id or not stat_name or difficulty is None:
        response['error'] = 'Parámetros character_id, stat y difficulty requeridos'
        return jsonify(response), 400

    character = Character.query.get(character_id)
    if not character:
        response['error'] = 'Personaje no encontrado'
        return jsonify(response), 404

    stat_name = stat_name.upper()
    stat = next((s for s in character.stats if s.name == stat_name), None)
    if not stat:
        response['error'] = f'Estadística \"{stat_name}\" no encontrada en el personaje'
        return jsonify(response), 400

    roll = random.randint(1, 20)
    total = roll + stat.value
    success = total >= difficulty

    response['message'] = 'Tirada realizada'
    response['result'] = {
        'stat': stat_name,
        'base_roll': roll,
        'modifier': stat.value,
        'total': total,
        'difficulty': difficulty,
        'success': success
    }
    return jsonify(response), 200