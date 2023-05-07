import re

email_filter = re.compile(r'(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')


def validate_email(email: str) -> bool:
    match = re.search(email_filter, email)
    return True if match else False
