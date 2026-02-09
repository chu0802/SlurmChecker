from .base import BaseCommand
from ..monitor import monitor_service

class ListBindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/lsbind"

    @property
    def requires_server(self) -> bool:
        return False

    def validate(self, user_input: str) -> str | None:
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used

    @property
    def is_local(self) -> bool:
        return True

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        jobs_map = monitor_service.list_jobs()
        
        if not jobs_map:
            return "📭 No jobs are currently being monitored."
            
        msg = "📊 *Currently Monitored Jobs:*\n"
        for srv, jobs in jobs_map.items():
            msg += f"\n🖥️ `{srv}`:\n"
            for job in jobs:
                last_epoch = job["last_epoch"]
                epoch_str = f"(Last Epoch: {last_epoch})" if last_epoch != -1 else "(Waiting for first result)"
                msg += f"  • Job *{job['job_id']}* {epoch_str}\n"
                
        return msg
