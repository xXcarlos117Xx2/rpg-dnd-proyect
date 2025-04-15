from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token, decode_token, jwt_required, get_jwt_identity, get_jwt
from .models import Character, Stat, InventoryItem, Ability, Spell, Condition, JournalEntry, Decision, CharacterRelationship, User, PersistentToken, db
from datetime import datetime, timezone, timedelta
import bcrypt
import random
from uuid import uuid4

api = Blueprint('api', __name__, url_prefix='/api')

# Auxiliary functions
def validate_required_fields(data, *fields):
    missing = [field for field in fields if not data.get(field)]
    if missing:
        return False, f'Faltan los siguientes campos: {", ".join(missing)}'
    return True, None

def cleanup_expired_tokens():
    now = datetime.now(timezone.utc)
    expired_tokens = PersistentToken.query.filter(
        PersistentToken.permanent == False,
        PersistentToken.revoked == False,
        PersistentToken.created_at < now - current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    ).all()

    for token in expired_tokens:
        token.revoked = True

    db.session.commit()
    return len(expired_tokens)

@api.route('/test/cleanup_tokens', methods=['POST'])
def trigger_cleanup():
    count = cleanup_expired_tokens()
    return jsonify({"message": f"{count} token(s) expirados han sido revocados"}), 200

@api.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"})

@api.route('/roll', methods=['GET'])
# Ejemplo de llamada: [GET] /api/roll?character_id=1&stat=AGI&difficulty=14
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

@api.route('/signup', methods=['POST'])
def register_user():
    response = {}
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'username', 'email', 'password')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    if User.query.filter_by(username=data['username']).first():
        response['error'] = 'Ese nombre de usuario ya existe'
        return jsonify(response), 400

    if User.query.filter_by(email=data['email']).first():
        response['error'] = 'Ese correo ya está registrado'
        return jsonify(response), 400

    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed
    )
    db.session.add(user)
    db.session.commit()

    response['message'] = 'Usuario registrado correctamente'
    response['user_id'] = user.id
    return jsonify(response), 201

@api.route('/login', methods=['POST'])
def login_user():
    response = {}
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'user', 'password')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    user = User.query.filter(
        (User.username == data['user']) | (User.email == data['user'])
    ).first()

    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        response['error'] = 'Credenciales incorrectas'
        return jsonify(response), 401

    if data.get("no_expire"):
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=False,
            additional_claims={"no_expire": True}
        )
        jti = decode_token(access_token)["jti"]
        db.session.add(PersistentToken(
            jti=jti, 
            user_id=user.id, 
            permanent=True
        ))
        db.session.commit()
    else:
        access_token = create_access_token(identity=str(user.id))
        decoded = decode_token(access_token)
        jti = decoded['jti']
        expires_in = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        db.session.add(PersistentToken(
            jti=jti,
            user_id=user.id,
            permanent=False,
            expires_at=datetime.now(timezone.utc) + expires_in
        ))
        db.session.commit()

    response['message'] = 'Login exitoso'
    response['access_token'] = access_token
    response['user_id'] = user.id
    return jsonify(response), 200

@api.route('/revoke_tokens', methods=['POST'])
def revoke_tokens():
    response = {}
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'user', 'password')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    user = User.query.filter(
        (User.username == data['user']) | (User.email == data['user'])
    ).first()

    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        response['error'] = 'Credenciales incorrectas'
        return jsonify(response), 401

    tokens = PersistentToken.query.filter_by(user_id=user.id, revoked=False).all()

    revoked_total = 0
    revoked_persistent = 0
    revoked_temporal = 0

    for token in tokens:
        token.revoked = True
        revoked_total += 1
        if token.permanent:
            revoked_persistent += 1
        else:
            revoked_temporal += 1

    db.session.commit()

    response['message'] = 'Tokens revocados correctamente'
    response['revoked_total'] = revoked_total
    response['revoked_persistent'] = revoked_persistent
    response['revoked_temporal'] = revoked_temporal
    return jsonify(response), 200

@api.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    response = {}
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    response['message'] = 'Usuario obtenido correctamente'
    response['user'] = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'characters': [c.to_dict(include_relationships=True) for c in user.characters]
    }
    return jsonify(response), 200

@api.route('/character', methods=['GET', 'POST', 'PUT', 'DELETE'])
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
            race=data['race'],
            goal=data['goal'],
            background=data['background'],
            level=data.get('level', 1),
            health_current=data.get('health_current', 6 + fuerza),
            health_max=data.get('health_max', 6 + fuerza),
            mana_current=data.get('mana_current', 3 + mente),
            mana_max=data.get('mana_max', 3 + mente),
            image_url=data.get('image_url'),
            user_id=user_id
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

@api.route('/inventory', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def inventory_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)
    item_id = request.args.get('item_id', type=int)

    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        items = InventoryItem.query.filter_by(character_id=character.id).all()
        response['message'] = 'Inventario obtenido correctamente'
        response['items'] = [item.to_dict() for item in items]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'item', 'description')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first_or_404()

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

    elif request.method == 'PUT':
        if not item_id:
            response['error'] = 'Parámetro item_id requerido'
            return jsonify(response), 400

        item = InventoryItem.query.get_or_404(item_id)
        character = Character.query.filter_by(id=item.character_id, user_id=user_id).first_or_404()

        data = request.get_json() or {}
        for field in ['item', 'description', 'image_url', 'magical', 'notes']:
            if field in data:
                setattr(item, field, data[field])

        db.session.commit()
        response['message'] = 'Item actualizado correctamente'
        response['item_id'] = item.id
        return jsonify(response), 200

    elif request.method == 'DELETE':
        if not item_id:
            response['error'] = 'Parámetro item_id requerido'
            return jsonify(response), 400

        item = InventoryItem.query.get_or_404(item_id)
        character = Character.query.filter_by(id=item.character_id, user_id=user_id).first_or_404()
        db.session.delete(item)
        db.session.commit()
        response['message'] = 'Item eliminado correctamente'
        response['item_id'] = item_id
        return jsonify(response), 200

@api.route('/ability', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def ability_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)
    ability_id = request.args.get('ability_id', type=int)

    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        abilities = Ability.query.filter_by(character_id=character.id).all()
        response['message'] = 'Habilidades obtenidas correctamente'
        response['abilities'] = [a.to_dict() for a in abilities]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'name', 'description', 'uses_per_session')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first_or_404()

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

    elif request.method == 'PUT':
        if not ability_id:
            response['error'] = 'Parámetro ability_id requerido'
            return jsonify(response), 400

        ability = Ability.query.get_or_404(ability_id)
        character = Character.query.filter_by(id=ability.character_id, user_id=user_id).first_or_404()

        data = request.get_json() or {}
        for field in ['name', 'description', 'image_url', 'uses_per_session', 'used']:
            if field in data:
                setattr(ability, field, data[field])

        db.session.commit()
        response['message'] = 'Habilidad actualizada correctamente'
        response['ability_id'] = ability.id
        return jsonify(response), 200

    elif request.method == 'DELETE':
        if not ability_id:
            response['error'] = 'Parámetro ability_id requerido'
            return jsonify(response), 400

        ability = Ability.query.get_or_404(ability_id)
        character = Character.query.filter_by(id=ability.character_id, user_id=user_id).first_or_404()

        db.session.delete(ability)
        db.session.commit()
        response['message'] = 'Habilidad eliminada correctamente'
        response['ability_id'] = ability_id
        return jsonify(response), 200

@api.route('/spell', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def spell_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)
    spell_id = request.args.get('spell_id', type=int)

    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        spells = Spell.query.filter_by(character_id=character.id).all()
        response['message'] = 'Hechizos obtenidos correctamente'
        response['spells'] = [s.to_dict() for s in spells]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'name', 'type', 'description', 'uses')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first_or_404()

        spell = Spell(
            character_id=character.id,
            name=data['name'],
            type=data['type'],
            description=data['description'],
            uses=data['uses'],
            image_url=data.get('image_url')
        )
        db.session.add(spell)
        db.session.commit()
        response['message'] = 'Hechizo creado correctamente'
        response['spell_id'] = spell.id
        return jsonify(response), 201

    elif request.method == 'PUT':
        if not spell_id:
            response['error'] = 'Parámetro spell_id requerido'
            return jsonify(response), 400

        spell = Spell.query.get_or_404(spell_id)
        character = Character.query.filter_by(id=spell.character_id, user_id=user_id).first_or_404()

        data = request.get_json() or {}
        for field in ['name', 'type', 'description', 'uses', 'image_url']:
            if field in data:
                setattr(spell, field, data[field])

        db.session.commit()
        response['message'] = 'Hechizo actualizado correctamente'
        response['spell_id'] = spell.id
        return jsonify(response), 200

    elif request.method == 'DELETE':
        if not spell_id:
            response['error'] = 'Parámetro spell_id requerido'
            return jsonify(response), 400

        spell = Spell.query.get_or_404(spell_id)
        character = Character.query.filter_by(id=spell.character_id, user_id=user_id).first_or_404()

        db.session.delete(spell)
        db.session.commit()
        response['message'] = 'Hechizo eliminado correctamente'
        response['spell_id'] = spell_id
        return jsonify(response), 200
    
@api.route('/reset_abilities', methods=['POST'])
@jwt_required()
def reset_abilities():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)

    if not character_id:
        response['error'] = 'Parámetro character_id requerido'
        return jsonify(response), 400

    character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
    abilities = Ability.query.filter_by(character_id=character.id).all()

    for ability in abilities:
        ability.used = False

    db.session.commit()
    response['message'] = 'Habilidades reiniciadas correctamente'
    response['character_id'] = character_id
    return jsonify(response), 200

@api.route('/condition', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def condition_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)
    condition_id = request.args.get('condition_id', type=int)

    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        conditions = Condition.query.filter_by(character_id=character.id).all()
        response['message'] = 'Condiciones obtenidas correctamente'
        response['conditions'] = [c.to_dict() for c in conditions]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'name', 'description')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first_or_404()

        condition = Condition(
            character_id=character.id,
            name=data['name'],
            description=data['description'],
            temporary=data.get('temporary', True)
        )
        db.session.add(condition)
        db.session.commit()
        response['message'] = 'Condición creada correctamente'
        response['condition_id'] = condition.id
        return jsonify(response), 201

    elif request.method == 'DELETE':
        if not condition_id:
            response['error'] = 'Parámetro condition_id requerido'
            return jsonify(response), 400

        condition = Condition.query.get_or_404(condition_id)
        character = Character.query.filter_by(id=condition.character_id, user_id=user_id).first_or_404()

        db.session.delete(condition)
        db.session.commit()
        response['message'] = 'Condición eliminada correctamente'
        response['condition_id'] = condition_id
        return jsonify(response), 200

@api.route('/journal', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def journal_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)
    entry_id = request.args.get('entry_id', type=int)

    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        entries = JournalEntry.query.filter_by(character_id=character.id).order_by(JournalEntry.created_at.desc()).all()
        response['message'] = 'Entradas de diario obtenidas correctamente'
        response['entries'] = [e.to_dict() for e in entries]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'content')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first_or_404()

        entry = JournalEntry(
            character_id=character.id,
            content=data['content'],
            created_at=datetime.utcnow()
        )
        db.session.add(entry)
        db.session.commit()
        response['message'] = 'Entrada de diario creada correctamente'
        response['entry_id'] = entry.id
        return jsonify(response), 201

    elif request.method == 'DELETE':
        if not entry_id:
            response['error'] = 'Parámetro entry_id requerido'
            return jsonify(response), 400

        entry = JournalEntry.query.get_or_404(entry_id)
        character = Character.query.filter_by(id=entry.character_id, user_id=user_id).first_or_404()

        db.session.delete(entry)
        db.session.commit()
        response['message'] = 'Entrada de diario eliminada correctamente'
        response['entry_id'] = entry_id
        return jsonify(response), 200

from .models import Decision
from flask_jwt_extended import jwt_required, get_jwt_identity

@api.route('/decision', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def decision_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)
    decision_id = request.args.get('decision_id', type=int)

    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        decisions = Decision.query.filter_by(character_id=character.id).order_by(Decision.id.desc()).all()
        response['message'] = 'Decisiones obtenidas correctamente'
        response['decisions'] = [d.to_dict() for d in decisions]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'description')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        character = Character.query.filter_by(id=data['character_id'], user_id=user_id).first_or_404()

        decision = Decision(
            character_id=character.id,
            description=data['description'],
            impact=data.get('impact')
        )
        db.session.add(decision)
        db.session.commit()
        response['message'] = 'Decisión registrada correctamente'
        response['decision_id'] = decision.id
        return jsonify(response), 201

    elif request.method == 'DELETE':
        if not decision_id:
            response['error'] = 'Parámetro decision_id requerido'
            return jsonify(response), 400

        decision = Decision.query.get_or_404(decision_id)
        character = Character.query.filter_by(id=decision.character_id, user_id=user_id).first_or_404()

        db.session.delete(decision)
        db.session.commit()
        response['message'] = 'Decisión eliminada correctamente'
        response['decision_id'] = decision_id
        return jsonify(response), 200

from .models import CharacterRelationship

@api.route('/relationship', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def relationship_handler():
    response = {}
    user_id = get_jwt_identity()
    character_id = request.args.get('character_id', type=int)
    relationship_id = request.args.get('relationship_id', type=int)

    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido'
            return jsonify(response), 400

        character = Character.query.filter_by(id=character_id, user_id=user_id).first_or_404()
        relationships = CharacterRelationship.query.filter_by(source_id=character.id).all()
        response['message'] = 'Relaciones obtenidas correctamente'
        response['relationships'] = [r.to_dict() for r in relationships]
        return jsonify(response), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'source_id', 'target_id', 'relation_type')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        source = Character.query.filter_by(id=data['source_id'], user_id=user_id).first_or_404()

        relationship = CharacterRelationship(
            source_id=source.id,
            target_id=data['target_id'],
            relation_type=data['relation_type']
        )
        db.session.add(relationship)
        db.session.commit()
        response['message'] = 'Relación creada correctamente'
        response['relationship_id'] = relationship.id
        return jsonify(response), 201

    elif request.method == 'DELETE':
        if not relationship_id:
            response['error'] = 'Parámetro relationship_id requerido'
            return jsonify(response), 400

        relationship = CharacterRelationship.query.get_or_404(relationship_id)
        source = Character.query.filter_by(id=relationship.source_id, user_id=user_id).first_or_404()

        db.session.delete(relationship)
        db.session.commit()
        response['message'] = 'Relación eliminada correctamente'
        response['relationship_id'] = relationship_id
        return jsonify(response), 200
