import uuid

from flask_security import RoleMixin, UserMixin
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from db import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f'<User {self.username}>'

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
