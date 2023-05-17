import logging

from db.errors import NotFoundInDBError
from db.roles_service import BaseRoleServiceDB, role_service_db
from flask import Blueprint, Flask
from flask_restful import abort, fields, marshal_with, reqparse
from flask_restx import Api, Resource

log = logging.getLogger(__name__)

roles_bp = Blueprint('roles_bp', __name__)
api = Api(
    roles_bp,
    doc='/doc',
    title='ROLES API',
    description='API for create, delete, update role and get all roles.',
    default='Roles',
    default_label='Roles API',
)

parser = reqparse.RequestParser()

parser.add_argument('name', type=str, help='Role name')
parser.add_argument('description', type=str, help='Role description')

role_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}


class BaseRolesApi(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_service: BaseRoleServiceDB = role_service_db


class Roles(BaseRolesApi):

    @marshal_with(role_fields)
    def patch(self, role_id):
        """Update the role."""
        args = parser.parse_args()
        try:
            return self.role_service.update(
                role_id=role_id,
                name=args['name'],
                description=args['description']
            )
        except NotFoundInDBError:
            abort(404, message="Role with id {} doesn't exist".format(role_id))

    def delete(self, role_id):
        """Delete the role."""
        try:
            self.role_service.delete(
                role_id=role_id
            )
        except NotFoundInDBError:
            abort(404, message="Role with id {} doesn't exist".format(role_id))
        return '', 204


class RolesList(BaseRolesApi):

    @marshal_with(role_fields)
    def get(self):
        """Get all roles."""
        roles = self.role_service.get_all()
        return roles

    @marshal_with(role_fields)
    def post(self):
        """Create a role."""
        args = parser.parse_args()
        role = self.role_service.create(
            name=args['name'],
            description=args['description']
        )
        return role


api.add_resource(Roles, '/<int:role_id>')
api.add_resource(RolesList, '')
