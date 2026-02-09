from abc import ABC, abstractmethod

class BaseCommand(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def validate(self, user_input: str) -> str | None:
        pass

    @abstractmethod
    def build_shell_command(self, user_input: str) -> str:
        pass
