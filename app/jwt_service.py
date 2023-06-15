from __future__ import annotations

import flask
from db.user_roles_service import user_role_service_db
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                set_access_cookies, set_refresh_cookies)
from routes.users import cache_service


def prepare_response_with_tokens(user_id: str, user_info: dict | None = None):
    if not user_info:
        user_info = {}

    user_roles = user_role_service_db.get_user_role(user_id=user_id)
    additional_claims = {'user_roles': user_roles}

    access_token = create_access_token(identity=user_id, fresh=True, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user_id)

    cache_service.set_to_cache(key=str(user_id), value=refresh_token)

    response = flask.jsonify(access_token=access_token, refresh_token=refresh_token, **user_info)
    set_access_cookies(response=response, encoded_access_token=access_token)
    set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)
    return response
