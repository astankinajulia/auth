import logging

import click

from db.errors import AlreadyExistsDBError
from db.roles_service import role_service_db
from db.user_roles_service import user_role_service_db
from db.user_service import user_service_db

log = logging.getLogger(__name__)

log.info('Create command create_superuser')


def create_superuser_command(email: str, password: str) -> None:
    """Create superuser role and add this role to new user with email and password."""
    log.info('Create superuser')
    role = role_service_db.create(name='superuser', description='superuser')
    click.echo('Superuser role created')
    user_id = user_service_db.get_or_create_user(email, password)
    click.echo('Superuser user created')
    try:
        user_role_service_db.put_user_role(user_id=user_id, role_id=role.id)
    except AlreadyExistsDBError:
        click.echo('Superuser role already added to user')
    else:
        click.echo('Superuser role added to user')
