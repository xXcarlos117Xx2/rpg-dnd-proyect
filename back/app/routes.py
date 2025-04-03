from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Character, Stat, InventoryItem, Ability, Spell, Condition, JournalEntry, Decision, CharacterRelationship, User, db
from datetime import datetime
import bcrypt

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

@api.route('/user', methods=['POST'])
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


@api.route('/user/login', methods=['POST'])
def login_user():
    response = {}
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'email', 'password')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        response['error'] = 'Usuario no encontrado'
        return jsonify(response), 404

    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        response['error'] = 'Contraseña incorrecta'
        return jsonify(response), 401

    response['message'] = 'Login exitoso'
    response['user_id'] = user.id
    access_token = create_access_token(identity=user.id)
    response['message'] = 'Login exitoso'
    response['access_token'] = access_token
    return jsonify(response), 200

@api.route('/user', methods=['GET'])
def get_user():
    response = {}
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        response['error'] = 'Parámetro user_id requerido'
        return jsonify(response), 400

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

        user_id = get_jwt_identity()
        character = Character(
            name=data['name'],
            user_id=user_id,
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

@api.route('/inventory', methods=['GET', 'POST', 'PUT', 'DELETE'])
def inventory_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)
    item_id = request.args.get('item_id', type=int)

    # GET - Obtener todos los items de un personaje
    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para obtener el inventario'
            return jsonify(response), 400

        items = InventoryItem.query.filter_by(character_id=character_id).all()
        response['message'] = 'Inventario obtenido correctamente'
        response['items'] = [item.to_dict() for item in items]
        return jsonify(response), 200

    # POST - Añadir nuevo item al inventario
    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'item', 'description')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        item = InventoryItem(
            character_id=data['character_id'],
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

    # PUT - Editar item
    elif request.method == 'PUT':
        if not item_id:
            response['error'] = 'Parámetro item_id requerido para editar'
            return jsonify(response), 400

        item = InventoryItem.query.get_or_404(item_id)
        data = request.get_json() or {}

        for field in ['item', 'description', 'image_url', 'magical', 'notes']:
            if field in data:
                setattr(item, field, data[field])

        db.session.commit()
        response['message'] = 'Item actualizado correctamente'
        response['item_id'] = item.id
        return jsonify(response), 200

    # DELETE - Eliminar item
    elif request.method == 'DELETE':
        if not item_id:
            response['error'] = 'Parámetro item_id requerido para eliminar'
            return jsonify(response), 400

        item = InventoryItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        response['message'] = 'Item eliminado correctamente'
        response['item_id'] = item_id
        return jsonify(response), 200
    
@api.route('/ability', methods=['GET', 'POST', 'PUT', 'DELETE'])
def ability_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)
    ability_id = request.args.get('ability_id', type=int)

    # GET - Obtener todas las habilidades de un personaje
    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para obtener habilidades'
            return jsonify(response), 400

        abilities = Ability.query.filter_by(character_id=character_id).all()
        response['message'] = 'Habilidades obtenidas correctamente'
        response['abilities'] = [a.to_dict() for a in abilities]
        return jsonify(response), 200

    # POST - Crear nueva habilidad
    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'name', 'description', 'uses_per_session')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        ability = Ability(
            character_id=data['character_id'],
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

    # PUT - Actualizar habilidad
    elif request.method == 'PUT':
        if not ability_id:
            response['error'] = 'Parámetro ability_id requerido para actualizar'
            return jsonify(response), 400

        ability = Ability.query.get_or_404(ability_id)
        data = request.get_json() or {}

        for field in ['name', 'description', 'image_url', 'uses_per_session', 'used']:
            if field in data:
                setattr(ability, field, data[field])

        db.session.commit()
        response['message'] = 'Habilidad actualizada correctamente'
        response['ability_id'] = ability.id
        return jsonify(response), 200

    # DELETE - Eliminar habilidad
    elif request.method == 'DELETE':
        if not ability_id:
            response['error'] = 'Parámetro ability_id requerido para eliminar'
            return jsonify(response), 400

        ability = Ability.query.get_or_404(ability_id)
        db.session.delete(ability)
        db.session.commit()
        response['message'] = 'Habilidad eliminada correctamente'
        response['ability_id'] = ability_id
        return jsonify(response), 200

@api.route('/reset_abilities', methods=['POST'])
def reset_abilities():
    response = {}
    character_id = request.args.get('character_id', type=int)

    if not character_id:
        response['error'] = 'Parámetro character_id requerido'
        return jsonify(response), 400

    abilities = Ability.query.filter_by(character_id=character_id).all()

    if not abilities:
        response['message'] = 'No se encontraron habilidades para este personaje'
        return jsonify(response), 200

    for ability in abilities:
        ability.used = False

    db.session.commit()
    response['message'] = 'Habilidades reiniciadas correctamente'
    response['character_id'] = character_id
    return jsonify(response), 200

@api.route('/spell', methods=['GET', 'POST', 'PUT', 'DELETE'])
def spell_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)
    spell_id = request.args.get('spell_id', type=int)

    # GET - Obtener todos los hechizos de un personaje
    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para obtener hechizos'
            return jsonify(response), 400

        spells = Spell.query.filter_by(character_id=character_id).all()
        response['message'] = 'Hechizos obtenidos correctamente'
        response['spells'] = [spell.to_dict() for spell in spells]
        return jsonify(response), 200

    # POST - Crear un nuevo hechizo
    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'name', 'type', 'description', 'uses')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        spell = Spell(
            character_id=data['character_id'],
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

    # PUT - Actualizar un hechizo
    elif request.method == 'PUT':
        if not spell_id:
            response['error'] = 'Parámetro spell_id requerido para actualizar'
            return jsonify(response), 400

        spell = Spell.query.get_or_404(spell_id)
        data = request.get_json() or {}

        for field in ['name', 'type', 'description', 'uses', 'image_url']:
            if field in data:
                setattr(spell, field, data[field])

        db.session.commit()
        response['message'] = 'Hechizo actualizado correctamente'
        response['spell_id'] = spell.id
        return jsonify(response), 200

    # DELETE - Eliminar un hechizo
    elif request.method == 'DELETE':
        if not spell_id:
            response['error'] = 'Parámetro spell_id requerido para eliminar'
            return jsonify(response), 400

        spell = Spell.query.get_or_404(spell_id)
        db.session.delete(spell)
        db.session.commit()
        response['message'] = 'Hechizo eliminado correctamente'
        response['spell_id'] = spell_id
        return jsonify(response), 200

@api.route('/condition', methods=['GET', 'POST', 'DELETE'])
def condition_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)
    condition_id = request.args.get('condition_id', type=int)

    # GET - Listar condiciones de un personaje
    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para obtener condiciones'
            return jsonify(response), 400

        conditions = Condition.query.filter_by(character_id=character_id).all()
        response['message'] = 'Condiciones obtenidas correctamente'
        response['conditions'] = [c.to_dict() for c in conditions]
        return jsonify(response), 200

    # POST - Crear una nueva condición
    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'name', 'description')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        condition = Condition(
            character_id=data['character_id'],
            name=data['name'],
            description=data['description'],
            temporary=data.get('temporary', True)
        )
        db.session.add(condition)
        db.session.commit()
        response['message'] = 'Condición creada correctamente'
        response['condition_id'] = condition.id
        return jsonify(response), 201

    # DELETE - Eliminar condición
    elif request.method == 'DELETE':
        if not condition_id:
            response['error'] = 'Parámetro condition_id requerido para eliminar'
            return jsonify(response), 400

        condition = Condition.query.get_or_404(condition_id)
        db.session.delete(condition)
        db.session.commit()
        response['message'] = 'Condición eliminada correctamente'
        response['condition_id'] = condition_id
        return jsonify(response), 200
    
@api.route('/journal', methods=['GET', 'POST', 'DELETE'])
def journal_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)
    entry_id = request.args.get('entry_id', type=int)

    # GET - Entradas del diario de un personaje
    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para obtener entradas'
            return jsonify(response), 400

        entries = JournalEntry.query.filter_by(character_id=character_id).order_by(JournalEntry.created_at.desc()).all()
        response['message'] = 'Entradas de diario obtenidas correctamente'
        response['entries'] = [e.to_dict() for e in entries]
        return jsonify(response), 200

    # POST - Crear una nueva entrada de diario
    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'content')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        entry = JournalEntry(
            character_id=data['character_id'],
            content=data['content'],
            created_at=datetime.utcnow()
        )
        db.session.add(entry)
        db.session.commit()
        response['message'] = 'Entrada de diario creada correctamente'
        response['entry_id'] = entry.id
        return jsonify(response), 201

    # DELETE - Eliminar entrada del diario
    elif request.method == 'DELETE':
        if not entry_id:
            response['error'] = 'Parámetro entry_id requerido para eliminar'
            return jsonify(response), 400

        entry = JournalEntry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        response['message'] = 'Entrada de diario eliminada correctamente'
        response['entry_id'] = entry_id
        return jsonify(response), 200

@api.route('/decision', methods=['GET', 'POST', 'DELETE'])
def decision_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)
    decision_id = request.args.get('decision_id', type=int)

    # GET - Listar decisiones de un personaje
    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para obtener decisiones'
            return jsonify(response), 400

        decisions = Decision.query.filter_by(character_id=character_id).order_by(Decision.id.desc()).all()
        response['message'] = 'Decisiones obtenidas correctamente'
        response['decisions'] = [d.to_dict() for d in decisions]
        return jsonify(response), 200

    # POST - Crear una nueva decisión
    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'character_id', 'description')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        decision = Decision(
            character_id=data['character_id'],
            description=data['description']
        )
        db.session.add(decision)
        db.session.commit()
        response['message'] = 'Decisión registrada correctamente'
        response['decision_id'] = decision.id
        return jsonify(response), 201

    # DELETE - Eliminar una decisión
    elif request.method == 'DELETE':
        if not decision_id:
            response['error'] = 'Parámetro decision_id requerido para eliminar'
            return jsonify(response), 400

        decision = Decision.query.get_or_404(decision_id)
        db.session.delete(decision)
        db.session.commit()
        response['message'] = 'Decisión eliminada correctamente'
        response['decision_id'] = decision_id
        return jsonify(response), 200
    
@api.route('/relationship', methods=['GET', 'POST', 'DELETE'])
def relationship_handler():
    response = {}
    character_id = request.args.get('character_id', type=int)
    relationship_id = request.args.get('relationship_id', type=int)

    # GET - Obtener relaciones donde el personaje es el origen
    if request.method == 'GET':
        if not character_id:
            response['error'] = 'Parámetro character_id requerido para obtener relaciones'
            return jsonify(response), 400

        relationships = CharacterRelationship.query.filter_by(source_id=character_id).all()
        response['message'] = 'Relaciones obtenidas correctamente'
        response['relationships'] = [r.to_dict() for r in relationships]
        return jsonify(response), 200

    # POST - Crear una nueva relación entre dos personajes
    elif request.method == 'POST':
        data = request.get_json() or {}
        valid, error = validate_required_fields(data, 'source_id', 'target_id', 'relation_type')
        if not valid:
            response['error'] = error
            return jsonify(response), 400

        relationship = CharacterRelationship(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=data['relation_type']
        )
        db.session.add(relationship)
        db.session.commit()
        response['message'] = 'Relación creada correctamente'
        response['relationship_id'] = relationship.id
        return jsonify(response), 201

    # DELETE - Eliminar una relación
    elif request.method == 'DELETE':
        if not relationship_id:
            response['error'] = 'Parámetro relationship_id requerido para eliminar'
            return jsonify(response), 400

        relationship = CharacterRelationship.query.get_or_404(relationship_id)
        db.session.delete(relationship)
        db.session.commit()
        response['message'] = 'Relación eliminada correctamente'
        response['relationship_id'] = relationship_id
        return jsonify(response), 200