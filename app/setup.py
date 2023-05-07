from setuptools import setup

setup(
    name='app',
    entry_points={
        'flask.commands': [
            'create_superuser=app.commands:create_superuser'
        ],
    },
)
