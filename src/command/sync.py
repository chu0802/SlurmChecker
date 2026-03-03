from typing import List, Optional
from .base import BaseCommand
from ..config import get_settings

settings = get_settings()

class SyncCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/sync"

    @property
    def requires_server(self) -> bool:
        return False

    @property
    def is_local(self) -> bool:
        return True

    def validate(self, user_input: str) -> Optional[str]:
        # if not user_input.strip():
        #     return "❌ Please specify a project name. Usage: `/sync <project_name>`"
        
        servers = [s.strip() for s in settings.SSH_SERVERS.split(",") if s.strip()]
        if not servers:
            return "❌ No SSH_SERVERS configured in `.env`. Please add a comma-separated list of servers."
        
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used for local commands

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        project_name = user_input.strip() or settings.DEFAULT_PROJECT_NAME
        servers = [s.strip() for s in settings.SSH_SERVERS.split(",") if s.strip()]
        
        if not servers:
            return "❌ No servers found in configuration."

        background_tasks = context.get("background_tasks")
        job_runner = context.get("job_runner")
        response_url = context.get("response_url")

        if not background_tasks or not job_runner or not response_url:
            return "❌ Internal error: Missing background task context."

        # Enqueue tasks for each server
        for srv in servers:
            remote_cmd = f"cd ~/scratch/{project_name} && git -c core.sshCommand=\"ssh -i ~/.ssh/{srv}\" pull"
            
            background_tasks.add_task(job_runner, srv, remote_cmd, response_url)

        return f"🔄 Initiated sync for project `{project_name}` on {len(servers)} servers: `{', '.join(servers)}`"
