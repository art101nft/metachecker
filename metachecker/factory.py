from logging.config import dictConfig

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from metachecker import config


db = SQLAlchemy()


def setup_db(app: Flask, db: SQLAlchemy = db):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.DATA_FOLDER}/sqlite.db' # noqa
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return db

def create_app_huey():
    _app = Flask(__name__)
    _db = SQLAlchemy()
    dictConfig(config.LOGGING_CONFIG)
    setup_db(_app, _db)
    return _app

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('FLASK_SECRETS')
    setup_db(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'meme.index'
    login_manager.logout_view = 'meta.disconnect'

    @login_manager.user_loader
    def load_user(user_id):
        from metachecker.models import User
        user = User.query.get(user_id)
        return user

    with app.app_context():
        from metachecker import filters
        from metachecker.routes import api, meta, collection
        from metachecker.cli import mod, cli
        app.register_blueprint(filters.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(collection.bp)
        app.register_blueprint(meta.bp)
        app.register_blueprint(mod.bp)
        app.register_blueprint(cli.bp)
        return app
