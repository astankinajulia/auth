from pydantic import BaseSettings


class TestSettings(BaseSettings):

    service_url: str

    class Config:
        env_file = '.env'


test_settings = TestSettings()
