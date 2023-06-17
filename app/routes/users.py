import logging

from db.base_cache_service import AbstractCacheService
from db.errors import NotFoundInDBError
from db.redis_service import RedisCache
from db.user_service import user_service_db
from db.user_session_service import user_session_service_db
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies, verify_jwt_in_request)
from flask_login import login_user
from flask_restx import Api, Resource, fields
from flask_restx.reqparse import RequestParser
from jwt_service import prepare_response_with_tokens
from routes.errors import BadRequestError, NotFoundError, UnauthorizedError
from routes.schemas import PaginatedUserSessions
from routes.utils import validate_email

log = logging.getLogger(__name__)

cache_service: AbstractCacheService = RedisCache()

user_bp = Blueprint('api', __name__)
api = Api(
    user_bp,
    doc='/doc',
    title='AUTH API',
    description='API for register, login, logout, update user, refresh token, get user sessions.',
    default='Auth',
    default_label='Auth API',
)

parser = api.parser()
parser.add_argument('email', type=str, required=True, location='json')
parser.add_argument('password', type=str, required=True, location='json')


pagination_parser = RequestParser()
pagination_parser.add_argument(
    'page', type=int, required=False, default=1, help='Page number',
)
pagination_parser.add_argument(
    'pageSize', type=int, required=False, default=10, help='Page size',
)

user_session = api.model(
    'UserSession',
    {
        'user_agent': fields.String(required=True, description='user_agent'),
        'auth_date': fields.String(required=True, description='auth_date'),
        'logout_date': fields.String(required=True, description='logout_date'),
    }
)

paginated_user_session = api.model(
    'PaginatedUserSessions',
    {
        'page': fields.Integer(required=True, description='page'),
        'previous_page': fields.Integer(required=True, description='previous page'),
        'next_page': fields.Integer(required=True, description='next page'),
        'first_page': fields.Integer(required=True, description='first page', default=1),
        'last_page': fields.Integer(required=True, description='last page'),
        'total': fields.Integer(required=True, description='total pages'),
        'items': fields.List(fields.Nested(user_session), required=True),
    }
)


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
        raise BadRequestError(message=f'Not valid email {email}')


def get_param(params: dict, param_name: str):
    param = params.get(param_name)
    if not param:
        raise BadRequestError(message=f'Request without {param_name}')
    return param


@api.route('/register')
class Register(Resource):
    @api.doc(parser=parser, responses={201: ''})
    def post(self):
        """Register user with email and password."""
        log.info('Register api')

        params = request.get_json()
        email = get_param(params, 'email')
        password = get_param(params, 'password')

        validate_email_param(email)

        user = user_service_db.get_user_by_email(email)
        if user:
            raise BadRequestError(message='User has already registered')

        user_service_db.create_user(email=email, password=password)
        return Response('', status=201, mimetype='application/json')


@api.route('/login', methods=['POST'])
class Login(Resource):
    @api.doc(parser=parser)
    def post(self):
        """Login user."""
        log.info('Login api')

        params = request.get_json()
        email = get_param(params, 'email')
        password = get_param(params, 'password')

        try:
            user = user_service_db.get_user_by_email(email=email, is_optional=False)
        except NotFoundInDBError:
            raise NotFoundError(message='User not found')
        if not user.verify_password(password):
            api.abort(401, 'Bad username or password')

        login_user(user)

        user_session_service_db.create_user_session(user_id=user.id, user_agent=str(request.user_agent))

        response = prepare_response_with_tokens(user_id=user.id)

        return response


@api.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Update refresh token."""
        log.info('Refresh api')

        identity = get_jwt_identity()

        refresh_token_in_db = cache_service.get_from_cache(key=identity)
        if not refresh_token_in_db:
            raise UnauthorizedError(message='Not found refresh token in db')
        refresh_token_cookie = request.cookies['refresh_token_cookie']
        if refresh_token_in_db != refresh_token_cookie:
            raise UnauthorizedError(message='Not correct refresh token in db')

        access_token = create_access_token(identity=identity, fresh=False)
        refresh_token = create_refresh_token(identity=identity)

        cache_service.set_to_cache(key=identity, value=refresh_token)

        response = jsonify('')
        set_access_cookies(response=response, encoded_access_token=access_token)
        set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)

        return response


@api.route('/logout')
class Logout(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Logout user."""
        log.info('Logout api')

        identity = get_jwt_identity()

        cache_service.delete_from_cache(key=identity)
        response = jsonify({'message': 'logout successful'})
        unset_jwt_cookies(response)

        user_session_service_db.delete_user_session(user_id=identity, user_agent=str(request.user_agent))

        return response


@api.route('/update')
class Update(Resource):
    @api.doc(parser=parser)
    @jwt_required()
    def post(self):
        """Update user."""
        log.info('Update user api')

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
            log.info('User %s not found', user_id)
            raise NotFoundError(message='User not found')

        user_service_db.update_user(user_id, email, password)

        response = jsonify({'message': 'User updated'})

        access_token_cookie = request.cookies.get('access_token_cookie')
        refresh_token_cookie = request.cookies.get('refresh_token_cookie')

        set_access_cookies(response=response, encoded_access_token=access_token_cookie)
        set_refresh_cookies(response=response, encoded_refresh_token=refresh_token_cookie)

        return response


@api.route('/get_user_login_history')
class GetSessions(Resource):
    @api.marshal_list_with(paginated_user_session)
    @jwt_required()
    @api.expect(pagination_parser)
    def get(self):
        """Get user sessions."""
        user_id = get_jwt_identity()

        p_args = pagination_parser.parse_args()
        page = p_args.get('page')
        limit = p_args.get('pageSize')

        user_sessions: PaginatedUserSessions = user_session_service_db.get_all_user_sessions(
            user_id=user_id,
            page=page,
            per_page=limit,
        )

        return user_sessions.dict()
