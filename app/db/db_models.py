from __future__ import annotations

import enum
import random
import uuid

from config.settings import Config
from db.db import db
from flask_login import UserMixin
from flask_security import RoleMixin
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, func, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import ChoiceType
from werkzeug.security import check_password_hash, generate_password_hash


def get_user(email):
    user = User.query.filter_by(email=email).first()
    return user


class AuthType(enum.Enum):
    site = 'Site'
    google = 'Google'


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(255), unique=False)
    email_is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))
    auth_type = db.Column(ChoiceType(AuthType), nullable=False)

    def __init__(self, email, password, auth_type=AuthType.site.value):
        self.email = email
        self.password = self.generate_password_hash(password)
        self.auth_type = auth_type

    def __repr__(self):
        return f'<User {self.username}>'

    @staticmethod
    def generate_password_hash(password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_user_by_universal_login(cls, login: str | None = None, email: str | None = None):
        return cls.query.filter(or_(cls.login == login, cls.email == email)).first()


class SocialAccount(db.Model):
    __tablename__ = 'social_account'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, user_id, social_id):
        self.user_id = user_id
        self.social_id = social_id

    def __repr__(self):
        return f'<SocialAccount {self.social_id}:{self.user_id}>'


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id

    def __repr__(self):
        return f'<User role {self.user_id}:{self.role_id}>'


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Role {self.name}>'


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_y2023m05" PARTITION OF "session" 
         FOR VALUES FROM ('2023-05-01') TO ('2023-06-01');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_y2023m06" PARTITION OF "session" 
         FOR VALUES FROM ('2023-06-01') TO ('2023-07-01');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "session_y2023m07" PARTITION OF "session" 
         FOR VALUES FROM ('2023-07-01') TO ('2023-08-01');"""
    )


class UserSession(db.Model):
    __tablename__ = 'user_session'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'auth_date'),
        {
            'postgresql_partition_by': 'RANGE (auth_date)',
            'listeners': [('after_create', create_partition)],
        }
    )
    id = db.Column(db.Integer(), autoincrement=True)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
    user_agent = db.Column(db.String(255))
    auth_date = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    logout_date = db.Column(db.DateTime(timezone=True))


def get_short() -> str:
    return ''.join(
        random.choices(
            Config.CHARACTERS,
            k=Config.TOKEN_LENGTH,
        )
    )


class TinyUrl(db.Model):
    __tablename__ = 'tiny_urls'
    full_url = db.Column(db.String(255), unique=True, nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False, primary_key=True)
    requests_count = db.Column(db.Integer, default=0)
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __init__(self, full_url):
        self.full_url = full_url
        while True:
            self.short_url = get_short()
            if not TinyUrl.query.filter_by(short_url=self.short_url).first():
                break
