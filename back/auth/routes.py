from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token, get_jwt
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

    valid, error = validate_required_fields(data, 'login_name', 'password')
    if not valid:
        response['error'] = error
        return jsonify(response), 400

    user = User.query.filter(
        (User.username == data['login_name']) | (User.email == data['login_name'])
    ).first()

    if not user:
        current_app.logger.warning(f"Intento de login fallido: usuario '{data['login_name']}' no existe.")
    elif not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        current_app.logger.warning(f"Intento de login fallido: contraseña incorrecta para '{data['login_name']}'.")
    else:
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response['message'] = 'Login exitoso'
        response['access_token'] = access_token
        response['refresh_token'] = refresh_token
        return jsonify(response), 200

    response['error'] = 'Credenciales inválidas'
    return jsonify(response), 401

@auth.route('/userinfo', methods=['GET'])
@jwt_required()
def get_user_info():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    }), 200


@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    new_token = create_access_token(identity=str(identity))
    return jsonify({'access_token': new_token}), 200
