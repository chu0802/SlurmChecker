from .base import BaseCommand

class SimpleCommand(BaseCommand):
    def __init__(self, slack_name: str, server_cmd: str):
        self._name = slack_name
        self._cmd = server_cmd

    @property
    def name(self) -> str:
        return self._name

    def validate(self, user_input: str) -> str | None:
        # Simple commands generally don't take extra complex arguments needed for validation,
        # or they just ignore extra arguments.
        return None

    def build_shell_command(self, user_input: str) -> str:
        # Ignores user_input (args) and returns the fixed command
        return self._cmd
