from abc import ABC, abstractmethod

class BaseCommand(ABC):
    """
    Base class for all command handlers.
    
    The `server` argument is parsed by the main dispatcher and stripped from `user_input`.
    Commands are responsible for validating and processing the remaining arguments.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """The Slack command name (e.g., '/show')."""
        pass

    @property
    def requires_server(self) -> bool:
        """Whether the command requires a server argument as the first parameter. Defaults to True."""
        return True

    @abstractmethod
    def validate(self, user_input: str) -> str | None:
        """
        Validate the user input arguments (excluding the server argument).
        Return an error message string if invalid, or None if valid.
        """
        pass

    @abstractmethod
    def build_shell_command(self, user_input: str) -> str:
        """
        Build the final shell command to execute on the remote server.
        `user_input` contains arguments after the server name.
        """
        pass

    @property
    def is_local(self) -> bool:
        """Whether the command should be executed locally on the bot server."""
        return False

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        """
        Execute the command locally.
        `context` may contain extra info like channel_id.
        """
        raise NotImplementedError("This command does not support local execution.")
