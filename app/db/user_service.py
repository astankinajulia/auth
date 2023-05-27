import abc
import logging

from db.db import db
from db.db_models import User
from db.errors import NotFoundInDBError

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
    def get_user_by_id(self, user_id: str, is_optional: bool = True) -> User:
        user = User.query.filter_by(id=user_id).first()
        if not is_optional and not user:
            raise NotFoundInDBError(entity='user')
        return user

    def get_user_by_email(self, email: str, is_optional: bool = True) -> User:
        user = User.query.filter_by(email=email).first()
        if not is_optional and not user:
            raise NotFoundInDBError(entity='user')
        return user

    def create_user(self, email: str, password: str) -> str:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user.id

    def get_or_create_user(self, email: str, password: str) -> str:
        user = self.get_user_by_email(email=email)
        if not user:
            user = self.create_user(email=email, password=password)
        return user.id

    def update_user(self, user_id, email, password) -> None:
        log.info('Update user %s in db', user_id)
        user = self.get_user_by_id(user_id=user_id)
        user.email = email
        user.password = User.generate_password_hash(password)
        db.session.commit()


user_service_db = UserServiceDB()
