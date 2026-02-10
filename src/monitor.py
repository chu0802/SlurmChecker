import threading
import time
import httpx
import re
from typing import Dict, Tuple, Optional
from .ssh_client import execute_remote_command
from .config import get_settings

class JobMonitor:
    def __init__(self):
        self._jobs: Dict[Tuple[str, str], Dict] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.settings = get_settings()

    def start(self):
        """Start the background monitoring thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("✅ Job Monitor started.")

    def stop(self):
        """Stop the background monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join()

    def bind_job(self, server: str, job_id: str):
        """Add a job to the monitoring list."""
        with self._lock:
            key = (server, job_id)
            self._jobs[key] = {
                "last_epoch": -1
            }
        print(f"✅ Monitoring started for Job {job_id} on {server}")

    def unbind_job(self, server: str, job_id: str) -> bool:
        """Remove a job from the monitoring list."""
        with self._lock:
            key = (server, job_id)
            if key in self._jobs:
                del self._jobs[key]
                print(f"❌ Monitoring stopped for Job {job_id} on {server}")
                return True
        return False

    def list_jobs(self) -> Dict[str, list]:
        """List all currently monitored jobs grouped by server."""
        with self._lock:
            result = {}
            for (server, job_id), data in self._jobs.items():
                if server not in result:
                    result[server] = []
                result[server].append({
                    "job_id": job_id,
                    "status": data.get("status", "Unknown"),
                    "last_epoch": data.get("last_epoch", -1)
                })
        return result

    def _loop(self):
        while self._running:
            try:
                self._check_all_jobs()
            except Exception as e:
                print(f"⚠️ Error in monitoring loop: {e}")
            
            for _ in range(30):
                if not self._running:
                    break
                time.sleep(1)

    def _check_all_jobs(self):
        with self._lock:
            keys = list(self._jobs.keys())

        for server, job_id in keys:
            if not self._running:
                break
            
            self._process_job(server, job_id)

    def _process_job(self, server: str, job_id: str):
        squeue_cmd = f"{self.settings.SLURM_CMD_SQUEUE} --job {job_id} --noheader --format=%t"
        status_output = execute_remote_command(server, squeue_cmd).strip()

        if "Connection Dead" in status_output or "Network is unreachable" in status_output:
             print(f"⚠️ Skipping check for {server} due to connection issue.")
             return

        if not status_output or "Invalid job id" in status_output:
            self.unbind_job(server, job_id)
            self._notify_slack(server, job_id, "Job finished or disappeared. Unbinding.")
            return

        # Track status changes (specifically PD -> R)
        with self._lock:
            if (server, job_id) in self._jobs:
                job_data = self._jobs[(server, job_id)]
                last_status = job_data.get("status")
                
                # Update status
                job_data["status"] = status_output
                
                # Check for transition from PD to R
                if last_status and "PD" in last_status and "R" in status_output:
                    self._notify_slack(server, job_id, "🚀 Job transitioned from Pending (PD) to Running (R).")

        if "PD" in status_output:
            return 
        
        if "R" not in status_output and "CG" not in status_output:
            if "R" not in status_output: 
                 return 

        show_cmd = f"show {job_id} | tail -n 20"
        log_output = execute_remote_command(server, show_cmd)

        parsed_data = self._parse_accuracy(log_output)

        if parsed_data:
            new_epoch, experiment_name, new_accuracy = parsed_data
            
            with self._lock:
                key = (server, job_id)
                if key not in self._jobs:
                    return
                    
                last_epoch = self._jobs[key].get("last_epoch", -1)
                
                if int(new_epoch) > int(last_epoch):
                    self._jobs[key]["last_epoch"] = int(new_epoch)
                    self._notify_slack(
                        server, 
                        job_id, 
                        f"📈 Epoch {new_epoch}: Accuracy *{new_accuracy}*\n🧪 Experiment: `{experiment_name}`"
                    )

    def _parse_accuracy(self, log_output: str) -> Optional[Tuple[str, str, str]]:
        """
        Parse validation accuracy and experiment name from log output.
        Returns (epoch, accuracy, experiment_name) or None.
        """
        pattern = r"Epoch:\s+(\d+)\s+\|\s+Experiment:\s+(.+?)\s+\|\s+Validation Accuracy:\s+([\d\.]+)"
        matches = re.findall(pattern, log_output)
        
        if not matches:
            return None
            
        return matches[-1]

    def _notify_slack(self, server: str, job_id: str, message: str):
        # Always use the configured fixed channel
        channel_id = self.settings.SLACK_LOG_CHANNEL_ID
        text = f"[{server}] Job {job_id}:\n{message}"

        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.settings.SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel_id,
            "text": text
        }

        try:
            with httpx.Client() as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to send Slack notification: {e}")

monitor_service = JobMonitor()
