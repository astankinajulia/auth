import datetime

from pydantic import BaseModel, Field


class UserSession(BaseModel):
    user_agent: str = Field(..., description='User-Agent')
    auth_date: datetime.datetime = Field(..., description='Session auth date')


class Role(BaseModel):
    id: str
    name: str
    description: str
