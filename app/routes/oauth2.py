import logging

import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import requests
from config.settings import Config
from db.user_service import user_service_db
from db.user_session_service import user_session_service_db
from flask import request
from flask_restx import Api, Resource
from google_auth.google_auth import API_SERVICE_NAME, API_VERSION, SCOPES
from jwt_service import prepare_response_with_tokens

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

CALLBACK_ENDPOINT = 'oauth2callback'
ENTRYPOINT_AUTHORIZATION_ENDPOINT = 'google_authorization'

FULL_URL = f'https://{Config.SERVER_NAME}/oauth2/'
CALLBACK_URL = FULL_URL + CALLBACK_ENDPOINT
ENTRYPOINT_URL = FULL_URL + ENTRYPOINT_AUTHORIZATION_ENDPOINT


@api.route('/google_authorization')
class GetSessions(Resource):
    def get(self):
        if 'credentials' not in flask.session:
            return flask.redirect('authorize')

        # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])

        user_info_service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        log.info(user_info['email'])

        user_id = user_service_db.get_or_create_user_by_social_id(email=user_info['email'], social_id=user_info['id'])

        user_session_service_db.create_user_session(user_id=user_id, user_agent=str(request.user_agent))

        response = prepare_response_with_tokens(user_id, user_info)

        # Save credentials back to session in case access token was refreshed.
        flask.session['credentials'] = credentials_to_dict(credentials)
        return response


@api.route('/authorize')
class Authorize(Resource):
    def get(self):
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            Config.CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = CALLBACK_URL
        authorization_url, state = flow.authorization_url(access_type='offline', )
        # Store the state so the callback can verify the auth server response.
        flask.session['state'] = state
        return flask.redirect(authorization_url)


@api.route('/oauth2callback')
class Oauth2callback(Resource):
    def get(self):
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        state = flask.session['state']

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            Config.CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
        flow.redirect_uri = CALLBACK_URL

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = flask.request.url
        token = flow.fetch_token(authorization_response=authorization_response)
        log.info(token)

        # Store credentials in the session.
        credentials = flow.credentials
        log.info(credentials)
        flask.session['credentials'] = credentials_to_dict(credentials)

        return flask.redirect(ENTRYPOINT_URL)


@api.route('/revoke')
class Revoke(Resource):
    def get(self):
        """Revoke the access token associated with the current user session."""
        if 'credentials' not in flask.session:
            return 'You need to authorize before revoking credentials.'

        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])

        revoke = requests.post('https://oauth2.googleapis.com/revoke',
                               params={'token': credentials.token},
                               headers={'content-type': 'application/x-www-form-urlencoded'})

        status_code = getattr(revoke, 'status_code')
        if status_code == 200:
            return 'Credentials successfully revoked.'
        else:
            return 'An error occurred.'


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
