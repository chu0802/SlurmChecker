from typing import Dict
from ..config import get_settings
from .base import BaseCommand
from .simple import SimpleCommand
from .show import ShowCommand
from .bind_unbind import BindCommand, UnbindCommand
from .list_bind import ListBindCommand
from .scancel import SCancelCommand

settings = get_settings()

_commands = [
    SimpleCommand("/sq", settings.SLURM_CMD_FULL_SQUEUE),
    SimpleCommand("/share", settings.SLURM_CMD_SSHARE),
    ShowCommand(),
    BindCommand(),
    UnbindCommand(),
    ListBindCommand(),
    SCancelCommand(),
]

COMMAND_REGISTRY: Dict[str, BaseCommand] = {cmd.name: cmd for cmd in _commands}

def get_command_handler(command_name: str) -> BaseCommand | None:
    return COMMAND_REGISTRY.get(command_name)
