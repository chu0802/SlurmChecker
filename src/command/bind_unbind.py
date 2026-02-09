import re
from .base import BaseCommand
from ..monitor import monitor_service

class BindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/bind"

    def validate(self, user_input: str) -> str | None:
        if not re.match(r"^\d+$", user_input.strip()):
            return "❌ Invalid Job ID. Usage: `/bind <server> <job_id>`"
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used

    @property
    def is_local(self) -> bool:
        return True

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        job_id = user_input.strip()
        channel_id = context.get("channel_id")
        
        if not channel_id:
            return "❌ Error: Could not determine Slack Channel ID."

        monitor_service.bind_job(server, job_id, channel_id)
        return f"✅ Started monitoring Job *{job_id}* on `{server}`.\nI will notify you here when new results arrive."


class UnbindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/unbind"

    def validate(self, user_input: str) -> str | None:
        if not re.match(r"^\d+$", user_input.strip()):
            return "❌ Invalid Job ID. Usage: `/unbind <server> <job_id>`"
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used

    @property
    def is_local(self) -> bool:
        return True

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        job_id = user_input.strip()
        if monitor_service.unbind_job(server, job_id):
            return f"✅ Stopped monitoring Job *{job_id}* on `{server}`."
        else:
            return f"⚠️ Job *{job_id}* was not being monitored on `{server}`."
