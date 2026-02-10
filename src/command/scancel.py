import re
from .base import BaseCommand

class SCancelCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/scancel"

    def validate(self, user_input: str) -> str | None:
        if not re.match(r"^\d+$", user_input.strip()):
            return "❌ Invalid Job ID. Usage: `/scancel <server> <job_id>`"
        return None

    def build_shell_command(self, user_input: str) -> str:
        job_id = user_input.strip()
        return f"scancel {job_id} && echo '✅ Job {job_id} cancelled.'"
