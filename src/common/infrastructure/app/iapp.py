from abc import ABC, abstractmethod


class IApp(ABC):
    @abstractmethod
    def configure(self) -> None: ...
