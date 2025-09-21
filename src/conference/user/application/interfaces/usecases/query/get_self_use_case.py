from abc import ABC, abstractmethod

from conference.user.application.dtos.queries.get_user_be_id_query import (
    GetUserByIdQuery,
)
from conference.user.application.dtos.responses.user_dto import UserDTO


class IGetSelfUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetUserByIdQuery) -> UserDTO: ...
