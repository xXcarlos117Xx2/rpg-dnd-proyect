from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import create_access_token
from back.models import User, db
from back.utils import validate_required_fields
from datetime import datetime, timezone
import bcrypt

auth = Blueprint("auth", __name__)

@auth.route('/signup', methods=['POST'])
def register_user():
    response = {}
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'username', 'email', 'password')
    if not valid:
        response['error'] = error #TODO: cambiar a un mensaje mas genérico
        return jsonify(response), 400

    if User.query.filter_by(username=data['username']).first():
        response['error'] = 'El nombre de usuario ya existe'
        return jsonify(response), 400

    if User.query.filter_by(email=data['email']).first():
        response['error'] = 'El correo ya está registrado'
        return jsonify(response), 400

    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    now = datetime.now(timezone.utc)
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed,
        created_at=now,
        last_login=now,
        last_logout=now
    )
    db.session.add(user)
    db.session.commit()

    response['message'] = 'Usuario registrado correctamente'
    response['user_id'] = user.id
    return jsonify(response), 201

@auth.route('/login', methods=['POST'])
def login_user():
    response = {}
    data = request.get_json() or {}

    valid, error = validate_required_fields(data, 'username', 'password')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        current_app.logger.warning(f"Intento de login fallido: usuario '{data['username']}' no existe.")
    elif not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        current_app.logger.warning(f"Intento de login fallido: contraseña incorrecta para '{data['username']}'.")
    else:
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        token = create_access_token(identity=user.id)
        response['message'] = 'Login exitoso'
        response['token'] = token
        return jsonify(response), 200

    response['error'] = 'Credenciales inválidas'
    return jsonify(response), 401
