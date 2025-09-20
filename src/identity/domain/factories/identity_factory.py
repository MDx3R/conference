from common.domain.interfaces.uuid_generator import IUUIDGenerator
from identity.domain.entity.identity import Identity
from identity.domain.interfaces.identity_factory import IIdentityFactory


class IdentityFactory(IIdentityFactory):
    def __init__(self, uuid_generator: IUUIDGenerator) -> None:
        self.uuid_generator = uuid_generator

    def create(self, username: str, password: str) -> Identity:
        return Identity.create(self.uuid_generator.create(), username, password)
