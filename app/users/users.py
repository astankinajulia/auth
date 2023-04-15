from flask import Blueprint, request, abort, Response, jsonify
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, create_refresh_token, \
    jwt_required, get_jwt_identity
from flask_login import login_required
from flask_security import logout_user, login_user

from users.utils import create_user, get_user, validate_email


user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/register', methods=['POST'])
def register():
    params = request.get_json()
    email = params.get('email')
    password = params.get('password')

    if not email:
        abort(400, description='Request without email')
    if not password:
        abort(400, description='Request without password')
    if not validate_email(email):
        abort(400, description='Not valid email')

    user = get_user(email)
    if user:
        abort(400, description='User has already registered')

    create_user(email=email, password=password)
    return Response('', status=201, mimetype='application/json')


@user_bp.route('/login', methods=['POST'])
def login():
    params = request.get_json()
    email = params.get('email')
    password = params.get('password')
    if not email:
        abort(400, description='Request without email')
    if not password:
        abort(400, description='Request without password')

    user = get_user(email)
    if user and user.verify_password(password):
        login_user(user)
        response = jsonify({'msg': 'login successful'})

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        set_access_cookies(response, access_token)

        return jsonify(access_token=access_token, refresh_token=refresh_token)
    else:
        return jsonify({'msg': 'Bad username or password'}), 401


@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return jsonify(access_token=access_token)


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    response = jsonify({'msg': 'logout successful'})
    unset_jwt_cookies(response)

    return response


@user_bp.route('/change')
@login_required
def change():
    return 'change'


@user_bp.route('/get_sessions')
@login_required
def get_sessions():
    return 'get_sessions'
