import abc

from db.db import db
from db.db_models import Role, RolesUsers, User
from db.errors import AlreadyExistsDBError, NotFoundInDBError


class BaseUserRoleServiceDB:
    @abc.abstractmethod
    def get_user_role(self, user_id: str):
        pass

    @abc.abstractmethod
    def put_user_role(self, user_id: str, role_id: str):
        pass

    @abc.abstractmethod
    def delete_user_role(self, user_id: str, role_id: str):
        pass


class UserRoleServiceDB(BaseUserRoleServiceDB):
    def get_user_role(self, user_id: str, is_optional: bool = True):
        user = User.query.filter_by(id=user_id).first()
        if not is_optional and not user:
            raise NotFoundInDBError(entity='user_role')
        return user.roles

    def put_user_role(self, user_id: str, role_id: str):
        if RolesUsers.query.filter_by(user_id=user_id, role_id=role_id).first():
            raise AlreadyExistsDBError(params={'user_id': user_id, 'role_id': role_id})
        if not Role.query.filter_by(id=role_id).first():
            raise NotFoundInDBError(entity='role')
        if not User.query.filter_by(id=user_id).first():
            raise NotFoundInDBError(entity='user')
        user_role = RolesUsers(user_id=user_id, role_id=role_id)
        db.session.add(user_role)
        db.session.commit()

    def delete_user_role(self, user_id: str, role_id: str):
        user_role = RolesUsers.query.filter_by(user_id=user_id, role_id=role_id).first()
        if not user_role:
            raise NotFoundInDBError(entity='user_role')
        db.session.delete(user_role)
        db.session.commit()


user_role_service_db = UserRoleServiceDB()
