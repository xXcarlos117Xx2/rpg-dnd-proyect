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
    from .models import PersistentToken
    jti = jwt_payload["jti"]
    token = db.session.query(PersistentToken).filter_by(jti=jti).first()
    return token is not None and token.revoked

from . import models # Si se usa para importarlo hacia arriba a run.py y los pipfile etc