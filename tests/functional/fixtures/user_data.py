import pytest
from functional.conftest import fake


@pytest.fixture
def email():
    return fake.email()


@pytest.fixture
def email2():
    return fake.email()


@pytest.fixture
def password():
    return fake.password()
