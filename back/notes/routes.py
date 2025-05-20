from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from back.models import db, Character, JournalEntry, Decision
from back.utils import validate_required_fields
from datetime import datetime, timezone

notes = Blueprint("notes", __name__)

# --- Journal Endpoints ---

@notes.route('/journal/<int:character_id>', methods=['GET'])
@jwt_required()
def get_journal(character_id):
    user_id = get_jwt_identity()
    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    entries = JournalEntry.query.filter_by(character_id=character.id).order_by(JournalEntry.created_at.desc()).all()
    return jsonify({
        'message': 'Entradas de diario obtenidas correctamente',
        'entries': [e.to_dict() for e in entries]
    }), 200

@notes.route('/journal', methods=['POST'])
@jwt_required()
def create_journal_entry():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    valid, error = validate_required_fields(data, 'character_id', 'content')
    if not valid:
        return jsonify({'error': error}), 400

    character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    entry = JournalEntry(
        character_id=character.id,
        content=data['content'],
        created_at=datetime.now(timezone.utc)
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'message': 'Entrada creada', 'entry_id': entry.id}), 201

@notes.route('/journal/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_journal_entry(entry_id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Entrada no encontrada'}), 404

    character = Character.query.filter_by(id=entry.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entrada eliminada', 'entry_id': entry_id}), 200

# --- Decision Endpoints ---

@notes.route('/decision/<int:character_id>', methods=['GET'])
@jwt_required()
def get_decisions(character_id):
    user_id = get_jwt_identity()
    character = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    decisions = Decision.query.filter_by(character_id=character.id).order_by(Decision.id.desc()).all()
    return jsonify({
        'message': 'Decisiones obtenidas correctamente',
        'decisions': [d.to_dict() for d in decisions]
    }), 200

@notes.route('/decision', methods=['POST'])
@jwt_required()
def create_decision():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    valid, error = validate_required_fields(data, 'character_id', 'description')
    if not valid:
        return jsonify({'error': error}), 400

    character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first()
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    decision = Decision(
        character_id=character.id,
        description=data['description'],
        impact=data.get('impact')
    )
    db.session.add(decision)
    db.session.commit()

    return jsonify({'message': 'Decisión creada', 'decision_id': decision.id}), 201

@notes.route('/decision/<int:decision_id>', methods=['DELETE'])
@jwt_required()
def delete_decision(decision_id):
    user_id = get_jwt_identity()
    decision = Decision.query.get(decision_id)
    if not decision:
        return jsonify({'error': 'Decisión no encontrada'}), 404

    character = Character.query.filter_by(id=decision.character_id, user_id=user_id).first()
    if not character:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(decision)
    db.session.commit()
    return jsonify({'message': 'Decisión eliminada', 'decision_id': decision_id}), 200
