import click
from db.roles_service import role_service_db


@click.command()
def create_superuser():
    """Create superuser."""
    role_service_db.create(name='superuser', description='superuser')
    click.echo('Superuser created')
