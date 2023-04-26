import logging

from db.roles_service import BaseRoleServiceDB, role_service_db
from flask import Blueprint, Flask
from flask_restful import Api, Resource, fields, marshal_with, reqparse
from users.schemas import Role

log = logging.getLogger(__name__)

app = Flask(__name__)
roles_bp = Blueprint('roles_bp', __name__)
api = Api(roles_bp)

user_bp = Blueprint('roles_bp', __name__)

parser = reqparse.RequestParser()

parser.add_argument('name', type=str, help='Role name')
parser.add_argument('description', type=str, help='Role description')

role_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}


class BaseRolesApi(Resource):
    def __init__(self):
        self.role_service: BaseRoleServiceDB = role_service_db


class Roles(BaseRolesApi):

    @marshal_with(role_fields)
    def put(self, role_id):
        """Update the role"""
        args = parser.parse_args()
        role = self.role_service.update(
            role_id=role_id,
            name=args['name'],
            description=args['description']
        )
        return Role(**role)

    @marshal_with(role_fields)
    def delete(self, role_id):
        """Delete the role"""
        role = self.role_service.delete(
            role_id=role_id
        )
        return Role(**role)


class RolesList(BaseRolesApi):

    def get(self):
        """Get all roles"""
        roles = self.role_service.get_all()
        return [
            Role(
                id=role.id,
                name=role.name,
                description=role.description,
            ).dict()
            for role in roles
        ]

    @marshal_with(role_fields)
    def post(self):
        """Create a role"""
        args = parser.parse_args()
        role = self.role_service.create(
            name=args['name'],
            description=args['description']
        )
        return Role(**role)


api.add_resource(Roles, '/roles/<int:id>')
api.add_resource(RolesList, '/roles')
