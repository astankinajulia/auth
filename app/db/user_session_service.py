import abc

from db.db import db
from db.db_models import UserSession


class BaseUserSessionServiceDB:
    @abc.abstractmethod
    def create_user_session(self, user_id: str, user_agent: str):
        pass

    @abc.abstractmethod
    def delete_user_session_by_id(self, user_session_id: int):
        pass

    @abc.abstractmethod
    def get_all_user_sessions(self, user_session_id: int):
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
        db.session.delete(user_session)
        db.session.commit()

    def get_all_user_sessions(self, user_id):
        return UserSession.query.filter_by(user_id=user_id).all()

    def delete_user_session(self, user_id: str, user_agent: str):
        user_sessions = UserSession.query.filter_by(user_id=user_id, user_agent=user_agent).all()

        for session in user_sessions:
            db.session.delete(session)
        db.session.commit()


user_session_service_db = UserSessionServiceDB()
