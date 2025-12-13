from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.publish_conference_command import (
    PublishConferenceCommand,
)


class IPublishConferenceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: PublishConferenceCommand) -> None: ...
