import logging

from db.errors import AlreadyExistsDBError, NotFoundInDBError
from db.user_roles_service import BaseUserRoleServiceDB, user_role_service_db
from flask import Blueprint
from flask_restful import abort, fields, marshal_with
from flask_restx import Api, Resource

log = logging.getLogger(__name__)

user_roles_bp = Blueprint('user_roles_bp', __name__)
api = Api(
    user_roles_bp,
    doc='/doc',
    title='USER ROLES API',
    description='API for get, put, delete user roles by user_id and role_id.',
    default='User roles',
    default_label='User roles API',
)


role_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}


class BaseUserRoleApi(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_role_service: BaseUserRoleServiceDB = user_role_service_db


class UserRole(BaseUserRoleApi):
    def put(self, user_id, role_id):
        """Add the role to the user."""
        try:
            self.user_role_service.put_user_role(
                user_id=user_id,
                role_id=role_id,
            )
        except AlreadyExistsDBError:
            pass
        except NotFoundInDBError as e:
            abort(404, message="Not found {} for user={}, role_id={}".format(e.entity, user_id, role_id))
        return '', 201

    def delete(self, user_id, role_id):
        """Delete the role from the user."""
        try:
            self.user_role_service.delete_user_role(
                user_id=user_id,
                role_id=role_id,
            )
        except NotFoundInDBError as e:
            abort(404, message="Not found {} for user={}, role_id={}".format(e.entity, user_id, role_id))
        return '', 204


class UserRoleList(BaseUserRoleApi):

    @marshal_with(role_fields)
    def get(self, user_id):
        """Get all user roles."""
        return self.user_role_service.get_user_role(user_id=user_id)


api.add_resource(UserRole, '/<string:user_id>/roles/<int:role_id>')
api.add_resource(UserRoleList, '/<string:user_id>/roles/')
