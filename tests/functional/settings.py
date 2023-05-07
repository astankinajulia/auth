from pydantic import BaseSettings


class TestSettings(BaseSettings):

    redis_host: str
    redis_port: str

    service_url: str
    service_port: str = '5000'

    class Config:
        env_file = '.env'


test_settings = TestSettings()
