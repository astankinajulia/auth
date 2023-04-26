import abc
from typing import Optional

from db.db import db
from db.db_models import Role
from db.errors import IntegrityDBError
from sqlalchemy.exc import IntegrityError


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
    def get_all(self):
        roles = Role.query.all()
        return roles

    def create(self, name: str, description: str):
        role = Role(name=name, description=description)
        try:
            db.session.add(role)
            db.session.commit()
        except IntegrityError:
            params = {
                'name': name,
                'description': description,
            }
            raise IntegrityDBError(params)
        return role

    def delete(self, role_id: str):
        role = Role.query.filter_by(id=role_id).first()
        db.session.delete(role)
        db.session.commit()

    def update(self, role_id: str, name: Optional[str] = None, description: Optional[str] = None):
        if not any([name, description]):
            return

        role = Role.query.filter_by(id=role_id).first()
        if name:
            role.name = name
        if description:
            role.description = description
        db.session.commit()
        return role


role_service_db = RoleServiceDB()
