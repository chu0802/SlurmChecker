from typing import List, Optional
from .base import BaseCommand
from ..config import get_settings

settings = get_settings()

class RunCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/run"

    @property
    def requires_server(self) -> bool:
        return False

    @property
    def is_local(self) -> bool:
        return True

    def validate(self, user_input: str) -> Optional[str]:
        # Basic validation can happen here or in execute_local
        return None

    def build_shell_command(self, user_input: str) -> str:
        return "" # Not used for local commands

    def execute_local(self, server: str, user_input: str, context: dict) -> str:
        parts = user_input.strip().split()
        
        target_servers = [s.strip() for s in settings.SSH_SERVERS.split(",") if s.strip()]

        if not target_servers:
             return "❌ No servers configured in `SSH_SERVERS` and none provided."

        # Filter valid arguments (key=value)
        valid_args = []
        for arg in parts:
            if "=" in arg:
                arg_name, arg_value = arg.split("=")
                valid_args.append(f"--{arg_name} {arg_value}")
                
        # Build command
        project_name = settings.DEFAULT_PROJECT_NAME
        script_args = " ".join(valid_args)
        
        # Command construction
        remote_cmd = f"cd ~/scratch/{project_name} && python -m script.build_script {script_args}"

        background_tasks = context.get("background_tasks")
        job_runner = context.get("job_runner")
        response_url = context.get("response_url")

        if not background_tasks or not job_runner or not response_url:
            return "❌ Internal error: Missing background task context."

        # Enqueue tasks for each server
        for srv in target_servers:
            background_tasks.add_task(job_runner, srv, remote_cmd, response_url)

        return f"🚀 Launching on *{len(target_servers)}* servers: `{', '.join(target_servers)}`\n🔹 Command: `{remote_cmd}`"
