from .base import BaseCommand

class SimpleCommand(BaseCommand):
    def __init__(self, slack_name: str, server_cmd: str):
        self._name = slack_name
        self._cmd = server_cmd

    @property
    def name(self) -> str:
        return self._name

    def validate(self, user_input: str) -> str | None:
        return None

    def build_shell_command(self, user_input: str) -> str:
        return self._cmd
