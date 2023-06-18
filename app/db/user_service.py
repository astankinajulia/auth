from __future__ import annotations

import abc
import logging

from db.db import db
from db.db_models import AuthType, SocialAccount, User
from db.errors import NotFoundInDBError
from tracer_configurator import trace_func

log = logging.getLogger(__name__)


class BaseUserServiceDB:
    @abc.abstractmethod
    def get_user_by_id(self, user_id: str):
        pass

    @abc.abstractmethod
    def get_user_by_email(self, email: str):
        pass

    @abc.abstractmethod
    def create_user(self, email: str, password: str):
        pass

    @abc.abstractmethod
    def update_user(self, user_id, email, password):
        pass


class UserServiceDB(BaseUserServiceDB):
    @trace_func
    def get_user_by_id(self, user_id: str, is_optional: bool = True) -> User:
        user = User.query.filter_by(id=user_id).first()
        if not is_optional and not user:
            raise NotFoundInDBError(entity='user')
        return user

    @trace_func
    def get_user_by_email(self, email: str, is_optional: bool = True) -> User:
        user = User.query.filter_by(email=email, auth_type=AuthType.site.value).first()
        if not is_optional and not user:
            raise NotFoundInDBError(entity='user')
        return user

    @trace_func
    def create_user(self, email: str, password: str, auth_type: AuthType.value = AuthType.site.value) -> User:
        user = User(email=email, password=password, auth_type=auth_type)
        db.session.add(user)
        db.session.commit()
        return user

    def create_user_from_site(self, email: str, password: str) -> User:
        return self.create_user(email=email, password=password, auth_type=AuthType.site.value)

    def create_user_from_outer(self, email: str, password: str, auth_type: AuthType.value) -> User:
        return self.create_user(email=email, password=password, auth_type=auth_type)

    def get_or_create_user(self, email: str, password: str) -> str:
        user = self.get_user_by_email(email=email)
        if not user:
            user = self.create_user(email=email, password=password)
        return user.id

    @trace_func
    def update_user(self, user_id, email, password) -> None:
        log.info('Update user %s in db', user_id)
        user = self.get_user_by_id(user_id=user_id)
        user.email = email
        user.password = User.generate_password_hash(password)
        db.session.commit()

    @trace_func
    def get_social_account_by_social_id(self, social_id: str, is_optional: bool = True) -> User:
        user = SocialAccount.query.filter_by(social_id=social_id).first()
        if not is_optional and not user:
            raise NotFoundInDBError(entity='user')
        return user

    @trace_func
    def create_social_account(self, social_id: str, user_id: str):
        social_account = SocialAccount(social_id=social_id, user_id=user_id)
        db.session.add(social_account)
        db.session.commit()
        return social_account.id

    def get_or_create_user_by_social_id(self, social_id: str, email: str, auth_type: AuthType.value) -> str:
        social_account = self.get_social_account_by_social_id(social_id)
        if not social_account:
            user = self.create_user_from_outer(email=email, password=email+social_id, auth_type=auth_type)
            self.create_social_account(social_id=social_id, user_id=user.id)
        else:
            user = self.get_user_by_id(social_account.user_id)
        if user.email != email:
            user.email = email
            db.session.commit()
        return user.id


user_service_db = UserServiceDB()
