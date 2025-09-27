from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.value_objects.password import Password
from idp.identity.domain.value_objects.username import Username
from idp.identity.infrastructure.database.postgres.sqlalchemy.models.identity_base import (
    IdentityBase,
)


class IdentityMapper:
    @classmethod
    def to_domain(cls, base: IdentityBase) -> Identity:
        return Identity(
            identity_id=base.identity_id,
            username=Username(base.username),
            password=Password(base.password),
        )

    @classmethod
    def to_persistence(cls, user: Identity) -> IdentityBase:
        return IdentityBase(
            identity_id=user.identity_id,
            username=user.username.value,
            password=user.password.value,
        )
