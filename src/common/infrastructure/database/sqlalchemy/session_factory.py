from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class ISessionFactory(ABC):
    @abstractmethod
    def create(self) -> AsyncSession: ...


class MakerSessionFactory(ISessionFactory):
    _maker: async_sessionmaker[AsyncSession]

    def __init__(self, maker: async_sessionmaker[AsyncSession]) -> None:
        self._maker = maker

    def create(self) -> AsyncSession:
        return self._maker()

    def set_maker(self, maker: async_sessionmaker[AsyncSession]) -> None:
        self._maker = maker
