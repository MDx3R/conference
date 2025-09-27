from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from idp.identity.application.exceptions import IdentityNotFoundError
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.value_objects.password import Password
from idp.identity.domain.value_objects.username import Username
from idp.identity.infrastructure.database.postgres.sqlalchemy.mappers.identity_mapper import (
    IdentityMapper,
)
from idp.identity.infrastructure.database.postgres.sqlalchemy.models.identity_base import (
    IdentityBase,
)
from idp.identity.infrastructure.database.postgres.sqlalchemy.repositories.identity_repository import (
    IdentityRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@pytest.mark.asyncio
class TestIdentityRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.identity_repository = IdentityRepository(query_executor)

    async def _exists(self, identity: Identity) -> bool:
        return await self._get(identity) is not None

    async def _get(self, identity: Identity) -> Identity | None:
        async with self.maker() as session:
            result = await session.get(IdentityBase, identity.identity_id)
            if not result:
                return None
            return IdentityMapper.to_domain(result)

    async def _add_user(self) -> Identity:
        identity = self._get_user()
        async with self.maker() as session:
            session.add(IdentityMapper.to_persistence(identity))
            await session.commit()
        return identity

    def _get_user(self) -> Identity:
        return Identity(uuid4(), Username("test identity"), Password("hash"))

    async def test_get_by_id_success(self):
        identity = await self._add_user()

        result = await self.identity_repository.get_by_id(identity.identity_id)
        assert result == identity

    async def test_get_by_id_not_found(self):
        with pytest.raises(IdentityNotFoundError):
            await self.identity_repository.get_by_id(uuid4())

    async def test_exists_by_username_true(self):
        identity = await self._add_user()
        assert await self.identity_repository.exists_by_username(
            identity.username.value
        )

    async def test_exists_by_username_false(self):
        assert await self.identity_repository.exists_by_username("nonexistent") is False

    async def test_get_by_usernamed_success(self):
        identity = await self._add_user()

        result = await self.identity_repository.get_by_username(identity.username.value)

        assert identity == result

    async def test_get_by_usernamed_nonexistent_fails(self):
        with pytest.raises(IdentityNotFoundError):
            await self.identity_repository.get_by_username("nonexistent")

    async def test_add_success(self):
        identity = self._get_user()

        await self.identity_repository.add(identity)

        assert await self._exists(identity)
