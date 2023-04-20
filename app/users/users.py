import logging

from flask import Blueprint, request, abort, Response, jsonify
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies, create_refresh_token,
    jwt_required, get_jwt_identity, verify_jwt_in_request
)
from flask_login import login_required, login_user

from db.errors import NotFoundInDBError
from db.redis_service import Redis
from db.user_service import user_service_db
from errors import NotFoundError, BadRequestError
from users.utils import validate_email

log = logging.getLogger(__name__)

user_bp = Blueprint('user_bp', __name__)


@user_bp.errorhandler(NotFoundError)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code


@user_bp.errorhandler(BadRequestError)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code


@user_bp.route('/register', methods=['POST'])
def register():
    params = request.get_json()
    email = params.get('email')
    password = params.get('password')

    if not email:
        raise BadRequestError(message='Request without email')
        # abort(400, description='Request without email')
    if not password:
        abort(400, description='Request without password')
    if not validate_email(email):
        abort(400, description='Not valid email')

    user = user_service_db.get_user_by_email(email)
    if user:
        abort(400, description='User has already registered')

    user_service_db.create_user(email=email, password=password)
    return Response('', status=201, mimetype='application/json')


@user_bp.route('/login', methods=['POST'])
def login():
    log.info('Login')
    params = request.get_json()
    email = params.get('email')
    password = params.get('password')
    if not email:
        abort(400, description='Request without email')
    if not password:
        abort(400, description='Request without password')

    try:
        user = user_service_db.get_user_by_email(email=email, is_optional=False)
    except NotFoundInDBError:
        raise NotFoundError(message='User not found')
    if not user.verify_password(password):
        return jsonify({'msg': 'Bad username or password'}), 401

    login_user(user)

    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(identity=user.id)

    Redis().set(key=str(user.id), value=refresh_token)

    response = jsonify(access_token=access_token, refresh_token=refresh_token)
    set_access_cookies(response, access_token)

    return response


@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    log.info('Refresh')

    identity = get_jwt_identity()
    log.info(f'{identity=}')

    redis = Redis()
    refresh_token_in_db = redis.get(key=identity)
    if not refresh_token_in_db:
        abort(401, description='Not found refresh token in db')
    k = request.cookies['refresh_token_cookie']
    if refresh_token_in_db != k:
        abort(401, description='Not correct refresh token in db')

    access_token = create_access_token(identity=identity, fresh=False)
    refresh_token = create_refresh_token(identity=identity)

    Redis().set(key=identity, value=refresh_token)

    response = jsonify('')
    set_access_cookies(response, access_token)

    return response


@user_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
# @jwt_required()
def logout():
    identity = get_jwt_identity()

    Redis().delete(key=identity)
    response = jsonify({'msg': 'logout successful'})
    unset_jwt_cookies(response)

    return response


@user_bp.route('/update', methods=['POST'])
@jwt_required()
def update():
    jwt_data = verify_jwt_in_request()
    if not jwt_data:
        abort(400, description='Request without email')

    params = request.get_json()
    email = params.get('email')
    password = params.get('password')
    if not email:
        abort(400, description='Request without email')
    if not password:
        abort(400, description='Request without password')
    if not validate_email(email):
        abort(400, description='Not valid email')

    user_id = get_jwt_identity()
    try:
        user_service_db.get_user_by_id(user_id=user_id, is_optional=False)
    except NotFoundInDBError:
        raise NotFoundError(message='User not found')

    user_service_db.update_user(user_id, email, password)

    return 'change'


@user_bp.route('/get_sessions', methods=['GET'])
@login_required
def get_sessions():
    return 'get_sessions'
