import re
from .base import BaseCommand

class ShowCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/show"

    def validate(self, user_input: str) -> str | None:
        pattern = r"^(\d+)(?:\s+(\d+))?$"
        if not re.match(pattern, user_input.strip()):
            return "❌ Invalid format. Usage: `/show <server> [Job ID]` or `/show <server> [Job ID] [N]`"
        return None

    def build_shell_command(self, user_input: str) -> str:
        match = re.match(r"^(\d+)(?:\s+(\d+))?$", user_input.strip())
        job_id = match.group(1)
        lines_n = match.group(2)

        cmd = f"show {job_id}"
        if lines_n:
            cmd += f" | tail -n {lines_n}"
        
        return cmd
