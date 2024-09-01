from src.db.models import User
from sqlmodel import Session, select
from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_password_hash


class UserService:

    def get_user_by_email(self, email: str, session: Session):
        statement = select(User).where(User.email == email)

        user = session.exec(statement).first()

        return user

    def user_exists(self, email: str, session: Session):
        user = self.get_user_by_email(email, session)

        return True if user is not None else False

    def create_user(self, user_data: UserCreateModel, session: Session):
        user_data_dict = user_data.model_dump()

        new_user = User(
            **user_data_dict
        )

        new_user.password_hash = generate_password_hash(
            user_data_dict['password'])
        new_user.role = 'user'

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    def update_user(self, user: User, user_data: dict, session: Session):
        for k, v in user_data.items():
            setattr(user, k, v)

            session.commit()

        return user
