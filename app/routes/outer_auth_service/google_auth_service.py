import logging

import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import requests
from config.settings import Config
from db.db_models import AuthType
from db.user_service import user_service_db
from db.user_session_service import user_session_service_db
from flask import request
from google_auth.google_auth import API_SERVICE_NAME, API_VERSION, SCOPES
from routes.outer_auth_service.base_auth_service import (CALLBACK_URL,
                                                         ENTRYPOINT_URL,
                                                         BaseOuterAuth,
                                                         UserInfo)

log = logging.getLogger(__name__)


class GoogleAuth(BaseOuterAuth):
    entrypoint_url = f'{ENTRYPOINT_URL}?auth_provider=google'
    callback_url = f'{CALLBACK_URL}?auth_provider=google'

    def __init__(self):
        self.flow = None
        self.user_id = None
        self.credentials = None

    def _flow(self, state):
        self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            Config.CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
        self.flow.redirect_uri = self.callback_url

    def authorize(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            Config.CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = self.callback_url
        authorization_url, state = flow.authorization_url(access_type='offline', )
        # Store the state so the callback can verify the auth server response.
        flask.session['state'] = state
        return flask.redirect(authorization_url)

    def fetch_token(self):
        state = flask.session['state']
        self._flow(state)
        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = flask.request.url
        token = self.flow.fetch_token(authorization_response=authorization_response)
        log.debug(token)

    def revoke(self):
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

    def store_credentials(self):
        # Store credentials in the session.
        credentials = self.flow.credentials
        log.debug(credentials)
        flask.session['credentials'] = self.credentials_to_dict(credentials)

    def get_credentials(self):
        self.credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])

    def get_user_info(self) -> UserInfo:
        user_info_service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=self.credentials)
        user_info = user_info_service.userinfo().get().execute()
        log.info(user_info['email'])
        return UserInfo(
            email=user_info['email'],
            id=user_info['id'],
        )

    def save_user_data(self, user_info: UserInfo):
        self.user_id = user_service_db.get_or_create_user_by_social_id(
            email=user_info.email,
            social_id=user_info.id,
            auth_type=AuthType.google.value)
        user_session_service_db.create_user_session(user_id=self.user_id, user_agent=str(request.user_agent))
