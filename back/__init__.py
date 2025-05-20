from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from back.config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from back.auth.routes import auth
    from back.character.routes import character

    app.register_blueprint(auth, url_prefix='/api')
    app.register_blueprint(character, url_prefix='/api')

    return app
