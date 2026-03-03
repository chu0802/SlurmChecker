from typing import Optional
from .base import BaseCommand
from ..config import get_settings

settings = get_settings()

class LsConfigCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/lsconfig"

    @property
    def requires_server(self) -> bool:
        return False

    @property
    def is_local(self) -> bool:
        return True

    def validate(self, user_input: str) -> Optional[str]:
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used for local commands

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        servers = [s.strip() for s in settings.SSH_SERVERS.split(",") if s.strip()]
        
        if not servers:
            return "❌ No SSH_SERVERS configured in `.env`."

        # Target only the first server
        target_server = servers[0]
        project_name = settings.DEFAULT_PROJECT_NAME
        
        # Command construction
        remote_cmd = f"cd ~/scratch/{project_name} && python -m script.show_config"

        background_tasks = context.get("background_tasks")
        job_runner = context.get("job_runner")
        response_url = context.get("response_url")

        if not background_tasks or not job_runner or not response_url:
            return "❌ Internal error: Missing background task context."

        background_tasks.add_task(job_runner, target_server, remote_cmd, response_url)

        return f"📜 Fetching configuration from `{target_server}` for project `{project_name}`..."
