import re
from .base import BaseCommand
from ..monitor import monitor_service
from ..ssh_client import execute_remote_command

class BindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/bind"

    def validate(self, user_input: str) -> str | None:
        if not user_input.strip():
             return None # Auto-bind mode
        
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
        
        if not job_ids:
            # Auto-bind all running jobs
            squeue_cmd = f"{monitor_service.settings.SLURM_CMD_SQUEUE} --me --noheader --format=%i"
            output = execute_remote_command(server, squeue_cmd).strip()
            
            if "Connection Dead" in output:
                return output
                
            if not output:
                return f"ℹ️ No running jobs found on `{server}` to bind."
                
            job_ids = output.split()

        # channel_id is now ignored, using SLACK_LOG_CHANNEL_ID from env
        
        added_jobs = []
        for job_id in job_ids:
            monitor_service.bind_job(server, job_id)
            added_jobs.append(job_id)
        
        jobs_str = ", ".join([f"*{jid}*" for jid in added_jobs])
        return f"✅ Started monitoring Jobs {jobs_str} on `{server}`.\nI will notify you in the configured log channel when new results arrive."


class UnbindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/unbind"

    def validate(self, user_input: str) -> str | None:
        if not user_input.strip():
             return None # Auto-unbind mode

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
        
        if not job_ids:
            # Auto-unbind all monitored jobs for this server
            jobs_map = monitor_service.list_jobs()
            server_jobs = jobs_map.get(server, [])
            job_ids = [str(j["job_id"]) for j in server_jobs]
            
            if not job_ids:
                return f"ℹ️ No jobs are currently being monitored on `{server}`."

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
