from __future__ import annotations

import datetime

from config.settings import Config
from db.db import db
from db.db_models import TinyUrl


def get_expire_timestamp():
    expire_utc_time = datetime.datetime.utcnow() + datetime.timedelta(days=Config.CONFIRM_EMAIL_EXPIRATION_DAYS)
    return int(expire_utc_time.timestamp())


def create_tiny_url_confirm_email(user_id: str) -> str:
    """Create and get tiny url."""

    full_url = (
        f'{Config.BASE_CONFIRM_EMAIL_URL}/'
        f'?user_id={user_id}'
        f'&timestamp={get_expire_timestamp()}'
        f'&redirect={Config.MAIN_PAGE_REDIRECT_URL}'
    )
    short_url = TinyUrl(
        full_url=full_url,
    )
    db.session.add(short_url)
    db.session.commit()
    return short_url.short_url


def get_url(short_url: str) -> TinyUrl | None:
    url: TinyUrl = TinyUrl.query.filter_by(short_url=short_url).first()
    if url:
        return url


def delete_url(short_url: str) -> None:
    url: TinyUrl = TinyUrl.query.filter_by(short_url=short_url).first()
    if url:
        db.session.delete(url)
        db.session.commit()


def increase_counter(short_url: str) -> None:
    url: TinyUrl = TinyUrl.query.filter_by(short_url=short_url).first()
    url.requests_count = url.requests_count + 1
    db.session.commit()
