from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from back.models import db, Character, InventoryItem
from back.utils import validate_required_fields

inventory = Blueprint("inventory", __name__)

@inventory.route('/inventory/<int:character_id>', methods=['GET'])
@jwt_required()
def get_inventory(character_id):
    response = {}
    user_id = get_jwt_identity()

    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        response['error'] = 'Personaje no encontrado'
        return jsonify(response), 404

    items = InventoryItem.query.filter_by(character_id=character.id).all()
    response['message'] = 'Inventario obtenido correctamente'
    response['items'] = [item.to_dict() for item in items]
    return jsonify(response), 200

@inventory.route('/inventory', methods=['POST'])
@jwt_required()
def create_item():
    response = {}
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'character_id', 'item', 'description')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first()
    if not character:
        response['error'] = 'Personaje no encontrado'
        return jsonify(response), 404

    item = InventoryItem(
        character_id=character.id,
        item=data['item'],
        description=data['description'],
        image_url=data.get('image_url'),
        magical=data.get('magical', False),
        notes=data.get('notes')
    )
    db.session.add(item)
    db.session.commit()

    response['message'] = 'Item añadido al inventario'
    response['item_id'] = item.id
    return jsonify(response), 201

@inventory.route('/inventory/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    response = {}
    user_id = get_jwt_identity()
    item = InventoryItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item no encontrado'}), 404

    character = Character.query.filter_by(id=item.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json() or {}
    for field in ['item', 'description', 'image_url', 'magical', 'notes']:
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()
    response['message'] = 'Item actualizado correctamente'
    response['item_id'] = item.id
    return jsonify(response), 200

@inventory.route('/inventory/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    response = {}
    user_id = get_jwt_identity()
    item = InventoryItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item no encontrado'}), 404

    character = Character.query.filter_by(id=item.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(item)
    db.session.commit()
    response['message'] = 'Item eliminado correctamente'
    response['item_id'] = item_id
    return jsonify(response), 200
