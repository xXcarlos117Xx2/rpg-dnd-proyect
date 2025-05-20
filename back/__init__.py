from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config
import cloudinary

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)

    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET'],
        secure = True
    )

    from .routes import api
    app.register_blueprint(api)

    return app

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    from .models import User
    from flask import request
    from datetime import datetime

    user = db.session.get(User, int(jwt_payload["sub"]))
    if not user:
        return True  # El usuario ya no existe
    
    issued_at_str = jwt_payload.get("issued_at")
    if issued_at_str:
        try:
            issued_at = datetime.fromisoformat(issued_at_str)
            if user.last_logout and issued_at <= user.last_logout:
                return True
        except Exception as e:
            print(f"[ERROR] Error parsing issued_at: {e}")
            return True

    token_ip = jwt_payload.get("ip")
    current_ip = request.remote_addr
    if token_ip and token_ip != current_ip:
        print(f"[WARN] Cambio de IP detectado: Token: {token_ip}, Actual: {current_ip}")

    return False

from . import models # Si se usa para importarlo hacia arriba a run.py y los pipfile etc