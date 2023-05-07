import aiohttp
import pytest
from faker import Faker

from tests.functional.settings import TestSettings

fake = Faker()


def get_settings() -> TestSettings:
    return TestSettings()


test_settings = get_settings()

pytest_plugins = "tests.functional.fixtures"


@pytest.fixture
def make_get_request():
    async def inner(url_ending, query_data=None, cookies=None, headers=None):
        async with aiohttp.ClientSession(trust_env=True) as session:
            url = test_settings.service_url + url_ending
            return await session.get(
                url,
                params=query_data,
                ssl=False,
                cookies=cookies,
                headers=headers,
            )

    return inner


@pytest.fixture
def make_post_request():
    async def inner(url_ending, query_data=None, json=None, cookies=None, headers=None):
        async with aiohttp.ClientSession(trust_env=True) as session:
            url = test_settings.service_url + url_ending
            return await session.post(
                url,
                params=query_data,
                json=json,
                ssl=False,
                cookies=cookies,
                headers=headers,
            )

    return inner


@pytest.fixture
def email():
    return fake.email()


@pytest.fixture
def email2():
    return fake.email()


@pytest.fixture
def password():
    return fake.password()
