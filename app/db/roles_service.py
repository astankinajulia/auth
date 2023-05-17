import abc
from typing import Optional

from db.db import db
from db.db_models import Role
from db.errors import NotFoundInDBError
from tracer_configurator import trace_func


class BaseRoleServiceDB:
    @abc.abstractmethod
    def create(self, name: str, description: str):
        pass

    @abc.abstractmethod
    def delete(self, role_id: str):
        pass

    @abc.abstractmethod
    def update(self, role_id: str, name: Optional[str], description: Optional[str]):
        pass

    @abc.abstractmethod
    def get_all(self):
        pass


class RoleServiceDB(BaseRoleServiceDB):
    @trace_func
    def get_all(self):
        roles = Role.query.all()
        return roles

    @trace_func
    def create(self, name: str, description: str):
        role = Role.query.filter_by(name=name).first()
        if role:
            return role
        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        return role

    @trace_func
    def delete(self, role_id: str):
        role = Role.query.filter_by(id=role_id).first()
        if not role:
            raise NotFoundInDBError(entity='role')
        db.session.delete(role)
        db.session.commit()

    @trace_func
    def update(self, role_id: str, name: Optional[str] = None, description: Optional[str] = None):
        if not any([name, description]):
            return

        role = Role.query.filter_by(id=role_id).first()
        if not role:
            raise NotFoundInDBError(entity='role')
        if name:
            role.name = name
        if description:
            role.description = description
        db.session.commit()
        return role


role_service_db = RoleServiceDB()
