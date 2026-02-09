import subprocess
from .config import get_settings

settings = get_settings()

def execute_remote_command(cmd_string: str) -> str:
    SOCKET_PATH = "/tmp/ssh_mux/slurm_socket"
    
    final_command = f"bash -l -c '{cmd_string}'"

    cmd = [
        "ssh",
        "-S", SOCKET_PATH,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=no",
        f"{settings.SSH_USER}@{settings.SSH_HOST}",
        final_command,
    ]

    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=15
        )

        if result.returncode != 0:
            if "No such file" in result.stderr or result.returncode == 255:
                return "❌ Connection Dead. Please re-authenticate on the Oracle Server."
            return f"⚠️ Error:\n{result.stderr}"

        return result.stdout if result.stdout else "No active jobs."

    except subprocess.TimeoutExpired:
        return "❌ Command Timed Out."
    except Exception as e:
        return f"❌ System Error: {str(e)}"
