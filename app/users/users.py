import logging

from db.errors import NotFoundInDBError
from db.redis_service import Redis
from db.user_service import user_service_db
from errors import BadRequestError, NotFoundError, UnauthorizedError
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required,
                                set_access_cookies, unset_jwt_cookies,
                                verify_jwt_in_request)
from flask_login import login_required, login_user
from users.utils import validate_email

log = logging.getLogger(__name__)

user_bp = Blueprint('user_bp', __name__)


@user_bp.errorhandler(NotFoundError)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code


@user_bp.errorhandler(BadRequestError)
def bad_request_api_usage(e):
    return jsonify(e.to_dict()), e.status_code


@user_bp.errorhandler(UnauthorizedError)
def unauthorized_api_usage(e):
    return jsonify(e.to_dict()), e.status_code


def validate_email_param(email: str):
    if not validate_email(email):
        raise BadRequestError(message='Not valid email')


def get_param(params: dict, param_name: str):
    param = params.get(param_name)
    if not param:
        raise BadRequestError(message=f'Request without {param_name}')


@user_bp.route('/register', methods=['POST'])
def register():
    log.info('Register api')

    params = request.get_json()
    email = get_param(params, 'email')
    password = get_param(params, 'password')

    validate_email_param(password)

    user = user_service_db.get_user_by_email(email)
    if user:
        raise BadRequestError(message='User has already registered')

    user_service_db.create_user(email=email, password=password)
    return Response('', status=201, mimetype='application/json')


@user_bp.route('/login', methods=['POST'])
def login():
    log.info('Login api')

    params = request.get_json()
    email = get_param(params, 'email')
    password = get_param(params, 'password')

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
    log.info('Refresh api')

    identity = get_jwt_identity()
    log.info(f'{identity=}')

    redis = Redis()
    refresh_token_in_db = redis.get(key=identity)
    if not refresh_token_in_db:
        raise UnauthorizedError(message='Not found refresh token in db')
    k = request.cookies['refresh_token_cookie']
    if refresh_token_in_db != k:
        raise UnauthorizedError(message='Not correct refresh token in db')

    access_token = create_access_token(identity=identity, fresh=False)
    refresh_token = create_refresh_token(identity=identity)

    Redis().set(key=identity, value=refresh_token)

    response = jsonify('')
    set_access_cookies(response, access_token)

    return response


@user_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    log.info('Logout api')

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
        raise BadRequestError(message='Request without email')

    params = request.get_json()
    email = get_param(params, 'email')
    password = get_param(params, 'password')
    validate_email_param(email)

    user_id = get_jwt_identity()
    try:
        user_service_db.get_user_by_id(user_id=user_id, is_optional=False)
    except NotFoundInDBError:
        raise NotFoundError(message='User not found')

    user_service_db.update_user(user_id, email, password)

    response = jsonify({'msg': 'User updated'})
    return response


@user_bp.route('/get_sessions', methods=['GET'])
@login_required
def get_sessions():
    return 'get_sessions'
