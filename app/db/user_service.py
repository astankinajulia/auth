import abc
import logging

from db.db import db
from db.db_models import User
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
        user = User.query.filter_by(email=email).first()
        if not is_optional and not user:
            raise NotFoundInDBError(entity='user')
        return user

    @trace_func
    def create_user(self, email: str, password: str) -> None:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

    @trace_func
    def update_user(self, user_id, email, password) -> None:
        log.info('Update user %s in db', user_id)
        user = self.get_user_by_id(user_id=user_id)
        user.email = email
        user.password = User.generate_password_hash(password)
        db.session.commit()


user_service_db = UserServiceDB()
