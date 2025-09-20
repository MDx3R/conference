from common.domain.interfaces.uuid_generator import IUUIDGenerator
from user.domain.entity.user import User
from user.domain.interfaces.user_factory import IUserFactory


class UserFactory(IUserFactory):
    def __init__(self, uuid_generator: IUUIDGenerator) -> None:
        self.uuid_generator = uuid_generator

    def create(self, username: str) -> User:
        return User.create(self.uuid_generator.create(), username)
