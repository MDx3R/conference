import logging
from typing import Self

from common.infrastructure.config.database_config import DatabaseConfig
from common.infrastructure.database.sqlalchemy.session_factory import MAKER
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(self, engine: AsyncEngine, logger: logging.Logger):
        self._engine = engine
        self._logger = logger
        self._create_session_maker()

    @classmethod
    def create(
        cls, config: DatabaseConfig, logger: logging.Logger | None = None
    ) -> Self:
        return cls(
            engine=cls.create_engine(config),
            logger=logger or logging.getLogger(),
        )

    @staticmethod
    def create_engine(config: DatabaseConfig) -> AsyncEngine:
        return create_async_engine(
            config.database_url, echo=False
        )  # echo=True for detailed logs

    def _create_session_maker(self) -> None:
        self._session_maker = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    def get_engine(self) -> AsyncEngine:
        return self._engine

    def get_session_maker(self) -> MAKER:
        return self._session_maker

    async def truncate_database(self, metadata: MetaData) -> None:
        async with self._engine.begin() as conn:
            table_names = [table.name for table in metadata.sorted_tables]
            if not table_names:
                return

            quoted_tables = ", ".join(f'"{name}"' for name in table_names)
            stmt = text(f"TRUNCATE {quoted_tables} CASCADE;")

            await conn.execute(stmt)

    async def shutdown(self) -> None:
        self._logger.info("disposing database engine...")
        await self._engine.dispose()
        self._logger.info("database engine disposed gracefully")
