import re
from .base import BaseCommand
from ..monitor import monitor_service

class BindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/bind"

    def validate(self, user_input: str) -> str | None:
        if not user_input.strip():
             return "❌ Missing Job IDs. Usage: `/bind <server> <job_id_1> <job_id_2> ...`"
        
        parts = user_input.split()
        if not all(p.isdigit() for p in parts):
            return "❌ Invalid Job ID format. All Job IDs must be numbers."
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used

    @property
    def is_local(self) -> bool:
        return True

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        job_ids = user_input.split()
        # channel_id is now ignored, using SLACK_LOG_CHANNEL_ID from env
        
        for job_id in job_ids:
            monitor_service.bind_job(server, job_id)
        
        jobs_str = ", ".join([f"*{jid}*" for jid in job_ids])
        return f"✅ Started monitoring Jobs {jobs_str} on `{server}`.\nI will notify you in the configured log channel when new results arrive."


class UnbindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/unbind"

    def validate(self, user_input: str) -> str | None:
        if not user_input.strip():
             return "❌ Missing Job IDs. Usage: `/unbind <server> <job_id_1> <job_id_2> ...`"

        parts = user_input.split()
        if not all(p.isdigit() for p in parts):
            return "❌ Invalid Job ID format. All Job IDs must be numbers."
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used

    @property
    def is_local(self) -> bool:
        return True

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        job_ids = user_input.split()
        stopped = []
        not_found = []

        for job_id in job_ids:
            if monitor_service.unbind_job(server, job_id):
                stopped.append(job_id)
            else:
                not_found.append(job_id)
        
        msg = []
        if stopped:
            s_str = ", ".join([f"*{jid}*" for jid in stopped])
            msg.append(f"✅ Stopped monitoring Jobs {s_str} on `{server}`.")
        
        if not_found:
            nf_str = ", ".join([f"*{jid}*" for jid in not_found])
            msg.append(f"⚠️ Jobs {nf_str} were not being monitored on `{server}`.")
            
        return "\n".join(msg)
