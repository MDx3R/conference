from uuid import UUID

from conference.user.domain.entity.user import User
from conference.user.domain.interfaces.user_factory import IUserFactory


class UserFactory(IUserFactory):
    def create(self, user_id: UUID, username: str) -> User:
        return User.create(user_id, username)
