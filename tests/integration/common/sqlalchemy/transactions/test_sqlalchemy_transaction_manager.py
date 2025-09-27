from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.session_factory import (
    MakerSessionFactory,
)
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.common.sqlalchemy.transactions.conftest import MockModel


@pytest.mark.asyncio
class TestSQLAlchemyTransactionManager:
    @pytest.fixture(autouse=True)
    def setup(self, async_session_maker: async_sessionmaker[AsyncSession]):
        self.async_session_maker = async_session_maker

        self.factory = MakerSessionFactory(self.async_session_maker)
        self.uow = UnitOfWork(self.factory)

    def _get(self) -> MockModel:
        return MockModel(id=uuid4(), name="mock")

    async def _is_saved(self, model: MockModel) -> bool:
        async_session = self.async_session_maker()
        result = await async_session.get(MockModel, model.id) is not None
        await async_session.close()
        return result

    async def _create(self, model: MockModel, session: AsyncSession) -> MockModel:
        session.add(model)
        await session.flush()

        return model

    async def _update(self, model: MockModel, session: AsyncSession) -> MockModel:
        await session.merge(model)
        await session.flush()

        return model

    def _get_session(self) -> AsyncSession | None:
        if not self.uow._transaction_exists():  # noqa: SLF001
            return None
        return self.uow._get_session()  # noqa: SLF001

    def _get_session_raises(self) -> AsyncSession:
        return self.uow._get_session()  # noqa: SLF001

    async def test_session_cleared_on_exit(self) -> None:
        async with self.uow:
            assert self._get_session() is not None
        assert self._get_session() is None

    async def test_session_cleared_on_rollback(self) -> None:
        def raise_rollback() -> None:
            raise ValueError("Test rollback")

        async def run() -> None:
            async with self.uow:
                assert self._get_session() is not None
                raise_rollback()

        with pytest.raises(ValueError, match="Test rollback"):
            await run()
        assert self._get_session() is None

    async def test_consecutive_transactions_not_shared(self) -> None:
        async with self.uow:
            session1 = self._get_session()
        async with self.uow:
            session2 = self._get_session()
        assert id(session1) != id(session2)

    async def test_nested_transaction_is_shared(self) -> None:
        async with self.uow:
            outer_session = self._get_session()
            async with self.uow:
                inner_session = self._get_session()
                assert id(outer_session) == id(inner_session)

    async def test_get_session_reuses_session(self) -> None:
        async with self.uow:
            outer_session = self._get_session()
            async with self.uow.get_session() as inner_session:
                assert id(outer_session) == id(inner_session)

    async def test_get_session_creates_new_session(self) -> None:
        outer_session = self._get_session()
        assert outer_session is None
        async with self.uow.get_session() as inner_session:
            assert inner_session

    async def test_transaction_commit(self) -> None:
        model = self._get()
        async with self.uow:
            session = self._get_session_raises()
            result = await self._create(model, session)

        assert result is not None
        assert result.name == model.name
        assert result.created_at
        assert await self._is_saved(model)

    async def test_transaction_without_uow(self) -> None:
        model = self._get()
        async with self.uow.get_session() as session:
            result = await self._create(model, session)

        assert result is not None
        assert result.name == model.name
        assert await self._is_saved(model)

    async def test_transaction_rollback(self) -> None:
        model = self._get()

        def raise_rollback() -> None:
            raise ValueError("Test rollback")

        async def run() -> None:
            async with self.uow:
                session = self._get_session_raises()
                await self._create(model, session)
                raise_rollback()

        with pytest.raises(ValueError, match="Test rollback"):
            await run()

        assert not await self._is_saved(model)

    async def test_transaction_rollback_several_actions(self) -> None:
        model1 = self._get()
        model2 = self._get()

        def raise_rollback() -> None:
            raise ValueError("Test rollback")

        async def run() -> None:
            async with self.uow:
                session = self._get_session_raises()
                await self._create(model1, session)
                await self._create(model2, session)
                raise_rollback()

        with pytest.raises(ValueError, match="Test rollback"):
            await run()

        assert not await self._is_saved(model1)
        assert not await self._is_saved(model2)

    async def test_transaction_nested_no_commit(self) -> None:
        model1 = self._get()
        model2 = self._get()

        def raise_rollback() -> None:
            raise ValueError("Rollback")

        async def run() -> None:
            async with self.uow:
                outer_session = self._get_session_raises()
                await self._create(model1, outer_session)
                async with self.uow:
                    inner_session = self._get_session_raises()
                    await self._create(model2, inner_session)
                raise_rollback()

        with pytest.raises(ValueError, match="Rollback"):
            await run()

        assert not await self._is_saved(model1)
        assert not await self._is_saved(model2)

    async def test_transaction_nested_commit(self) -> None:
        model1 = self._get()
        model2 = self._get()
        async with self.uow:
            outer_session = self._get_session_raises()
            await self._create(model1, outer_session)
            async with self.uow:
                inner_session = self._get_session_raises()
                await self._create(model2, inner_session)

        assert await self._is_saved(model1)
        assert await self._is_saved(model2)
