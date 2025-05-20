from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from back.config import Config

# imports from back
from back.auth.routes import auth
from back.character.routes import character
from back.inventory.routes import inventory
from back.ability.routes import ability
from back.spell.routes import spell
from back.condition.routes import condition
from back.notes.routes import notes
from back.relationship.routes import relationship
from back.models import db

jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    app.register_blueprint(auth, url_prefix='/api')
    app.register_blueprint(character, url_prefix='/api')
    app.register_blueprint(inventory, url_prefix='/api')
    app.register_blueprint(ability, url_prefix='/api')
    app.register_blueprint(spell, url_prefix='/api')
    app.register_blueprint(condition, url_prefix='/api')
    app.register_blueprint(notes, url_prefix='/api')
    app.register_blueprint(relationship, url_prefix='/api')

    return app
