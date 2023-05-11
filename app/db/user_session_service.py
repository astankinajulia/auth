import abc
import datetime

from db.db import db
from db.db_models import UserSession
from routes.schemas import PaginatedUserSessions, UserSession as UserSessionSchema


class BaseUserSessionServiceDB:
    @abc.abstractmethod
    def create_user_session(self, user_id: str, user_agent: str):
        pass

    @abc.abstractmethod
    def delete_user_session_by_id(self, user_session_id: int):
        pass

    @abc.abstractmethod
    def get_all_user_sessions(self, user_session_id: int, page: int):
        pass

    @abc.abstractmethod
    def delete_user_session(self, user_id: str, user_agent: str):
        pass


class UserSessionServiceDB(BaseUserSessionServiceDB):
    def create_user_session(self, user_id: str, user_agent: str) -> None:
        user_session = UserSession(user_id=user_id, user_agent=user_agent)
        db.session.add(user_session)
        db.session.commit()

    def delete_user_session_by_id(self, user_session_id: int):
        user_session = UserSession.query.filter_by(id=user_session_id).first()
        user_session.logout_date = datetime.datetime.now()
        db.session.commit()

    def get_all_user_sessions(self, user_id, page: int = 1, per_page: int = 10) -> PaginatedUserSessions:
        user_sessions = UserSession.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, count=True)
        return PaginatedUserSessions(
            page=page,
            previous_page=user_sessions.prev_num,
            next_page=user_sessions.next_num,
            first_page=1,
            last_page=user_sessions.pages,
            total=user_sessions.total,
            items=[
                UserSessionSchema(
                    user_agent=session.user_agent,
                    auth_date=str(session.auth_date.date()),
                    logout_date=str(session.logout_date.date()) if session.logout_date else None,
                )
                for session in user_sessions.items
            ],
        )

    def delete_user_session(self, user_id: str, user_agent: str):
        user_sessions = UserSession.query.filter_by(user_id=user_id, user_agent=user_agent).all()

        for session in user_sessions:
            session.logout_date = datetime.datetime.now()
        db.session.commit()


user_session_service_db = UserSessionServiceDB()
