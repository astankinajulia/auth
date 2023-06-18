import abc

from config.settings import Config
from pydantic import BaseModel

CALLBACK_ENDPOINT = 'oauth2callback'
ENTRYPOINT_AUTHORIZATION_ENDPOINT = 'authorization'

FULL_URL = f'https://{Config.SERVER_NAME}/oauth2/'
CALLBACK_URL = FULL_URL + CALLBACK_ENDPOINT
ENTRYPOINT_URL = FULL_URL + ENTRYPOINT_AUTHORIZATION_ENDPOINT


class UserInfo(BaseModel):
    email: str
    id: str


class BaseOuterAuth:
    entrypoint_url = ENTRYPOINT_URL
    callback_url = CALLBACK_URL

    @abc.abstractmethod
    def authorize(self):
        pass

    @abc.abstractmethod
    def get_user_info(self) -> UserInfo:
        pass

    @abc.abstractmethod
    def fetch_token(self):
        pass

    @abc.abstractmethod
    def revoke(self):
        pass

    @abc.abstractmethod
    def store_credentials(self):
        pass

    @abc.abstractmethod
    def get_credentials(self):
        pass

    @abc.abstractmethod
    def save_user_data(self, user_info: UserInfo):
        pass

    @staticmethod
    def credentials_to_dict(credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}
