import logging

from config.settings import Config
from db.db_models import get_user
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from users.roles import roles_bp
from users.user_roles import user_roles_bp
from users.users import user_bp

log = logging.getLogger(__name__)


def create_app():
    log.info('Create app...')

    app = Flask(__name__)
    app.config.from_object(Config)

    from db.db import db

    db.init_app(app)
    app.app_context().push()
    db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user_bp.login'

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    @login_manager.user_loader
    def load_user(id):
        return get_user(id)

    app.register_blueprint(user_bp, url_prefix='')
    app.register_blueprint(roles_bp, url_prefix='')
    app.register_blueprint(user_roles_bp, url_prefix='')

    JWTManager(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
