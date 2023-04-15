import re

from db_models import User

from db import db

email_filter = re.compile(r'(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')


def validate_email(email: str) -> bool:
    match = re.search(email_filter, email)
    return True if match else False


def get_user(email: str):
    user = User.query.filter_by(email=email).first()
    return user


def create_user(email, password):
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
