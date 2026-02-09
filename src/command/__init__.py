from typing import Dict
from ..config import get_settings
from .base import BaseCommand
from .simple import SimpleCommand
from .show import ShowCommand

settings = get_settings()

_commands = [
    SimpleCommand("/sq", settings.SLURM_CMD_SQUEUE),
    SimpleCommand("/share", settings.SLURM_CMD_SSHARE),
    ShowCommand(),
]

COMMAND_REGISTRY: Dict[str, BaseCommand] = {cmd.name: cmd for cmd in _commands}

def get_command_handler(command_name: str) -> BaseCommand | None:
    return COMMAND_REGISTRY.get(command_name)
