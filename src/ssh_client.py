import subprocess
from .config import get_settings

settings = get_settings()

def execute_remote_command(server: str, cmd_string: str) -> str:
    SOCKET_PATH = f"/tmp/ssh_mux/{server}"
    
    final_command = f"bash -l -c '{cmd_string}'"

    cmd = [
        "ssh",
        "-S", SOCKET_PATH,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=no",
        f"{settings.SSH_USER}@{server}.{settings.SSH_HOST}",
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
            return f"⚠️ Error:\n{result.stdout}\n{result.stderr}"

        output = result.stdout
        if result.stderr:
            output += f"\n{result.stderr}"

        return output if output.strip() else "No active jobs."

    except subprocess.TimeoutExpired:
        return "❌ Command Timed Out."
    except Exception as e:
        return f"❌ System Error: {str(e)}"
