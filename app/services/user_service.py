# app/services/user_services.py
from sqlalchemy.orm import Session
from app.db.models.user_model import User

class UserService:

    def get_by_id(self, db: Session, user_id: str) -> User | None:
        """Get a non-deleted user by primary key for auth dependency checks."""
        return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

















user_service = UserService()
