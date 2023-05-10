from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field


class UserSession(BaseModel):
    user_agent: str = Field(..., description='User-Agent')
    auth_date: str = Field(..., description='Session auth date')
    logout_date: str | None = Field(..., description='Session logout date')


class Role(BaseModel):
    id: str
    name: str
    description: str


class PaginateSchema(BaseModel):
    page: int
    previous_page: int | None
    next_page: int | None
    first_page: int = 1
    last_page: int
    total: int
    items: List[Any]


class PaginatedUserSessions(PaginateSchema):
    items: List[UserSession]
