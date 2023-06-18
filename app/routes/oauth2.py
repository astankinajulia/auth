import logging

import flask
from flask import request
from flask_restx import Api, Resource, abort
from jwt_service import prepare_response_with_tokens
from routes.outer_auth_service.base_auth_service import BaseOuterAuth, UserInfo
from routes.outer_auth_service.google_auth_service import GoogleAuth

log = logging.getLogger(__name__)

oauth2_bp = flask.Blueprint('oauth2_bp', __name__)
api = Api(
    oauth2_bp,
    doc='/doc',
    title='OAUTH2 API',
    description='OAUTH2 API for oauth true google',
    default='OAuth2',
    default_label='OAuth2 API',
)


@api.route('/authorization')
class GetSessions(Resource):
    def get(self):
        auth_provider = request.args.get('auth_provider')
        if auth_provider == 'google':
            outer_auth: BaseOuterAuth = GoogleAuth()
        else:
            abort(400, message='Bad auth provider {}'.format(auth_provider))

        if 'credentials' not in flask.session:
            return flask.redirect(f'authorize?auth_provider={auth_provider}')

        outer_auth.get_credentials()
        user_info: UserInfo = outer_auth.get_user_info()
        outer_auth.save_user_data(user_info=user_info)

        response = prepare_response_with_tokens(outer_auth.user_id, user_info.dict())
        # Save credentials back to session in case access token was refreshed.
        flask.session['credentials'] = outer_auth.credentials_to_dict(outer_auth.credentials)
        return response


@api.route('/authorize')
class Authorize(Resource):
    def get(self):
        auth_provider = request.args.get('auth_provider')
        if auth_provider == 'google':
            outer_auth: BaseOuterAuth = GoogleAuth()
        else:
            abort(400, message='Bad auth provider {}'.format(auth_provider))

        return outer_auth.authorize()


@api.route('/oauth2callback')
class Oauth2callback(Resource):
    def get(self):
        auth_provider = request.args.get('auth_provider')
        if auth_provider == 'google':
            outer_auth: BaseOuterAuth = GoogleAuth()
        else:
            abort(400, message='Bad auth provider {}'.format(auth_provider))

        outer_auth.fetch_token()
        outer_auth.store_credentials()
        return flask.redirect(outer_auth.entrypoint_url)


@api.route('/revoke')
class Revoke(Resource):
    def get(self):
        """Revoke the access token associated with the current user session."""
        auth_provider = request.args.get('auth_provider')
        if auth_provider == 'google':
            outer_auth: BaseOuterAuth = GoogleAuth()
        else:
            abort(400, message='Bad auth provider {}'.format(auth_provider))

        return outer_auth.revoke()
