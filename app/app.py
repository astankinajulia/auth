from flask import Flask
from flask_jwt_extended import JWTManager

from users.users import user_bp
from settings import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    from db import db

    db.init_app(app)
    app.app_context().push()
    db.create_all()

    app.register_blueprint(user_bp, url_prefix='/user')
    jwt = JWTManager(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
