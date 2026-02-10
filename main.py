import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks, Request
from src.security import verify_slack_signature
from src.ssh_client import execute_remote_command
from src.command import get_command_handler
from src.monitor import monitor_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    monitor_service.start()
    yield
    monitor_service.stop()

app = FastAPI(lifespan=lifespan)

def background_job_runner(server: str, final_cmd: str, response_url: str):
    result_text = execute_remote_command(server, final_cmd)
    payload = {"text": f"💻 Output:\n```{result_text}```"}
    try:
        httpx.post(response_url, json=payload)
    except Exception as e:
        print(f"Failed to send: {e}")

@app.post("/dispatch", dependencies=[Depends(verify_slack_signature)])
async def dispatch_command(
    request: Request,
    background_tasks: BackgroundTasks
):
    form_data = await request.form()
    command_name = form_data.get("command", "").lower()
    user_input = form_data.get("text", "").strip().lower()
    response_url = form_data.get("response_url")

    handler = get_command_handler(command_name)
    if not handler:
        return {"response_type": "ephemeral", "text": f"❌ Unknown command: `{command_name}`"}

    server = ""
    command_args = ""

    if handler.requires_server:
        if not user_input:
            return {"response_type": "ephemeral", "text": "❌ Missing required argument: `<server>`. Usage: `/command <server> [args]`"}
        
        parts = user_input.split(maxsplit=1)
        server = parts[0]
        command_args = parts[1] if len(parts) > 1 else ""
    else:
        # Commands that don't need a server argument (e.g., /lsbind)
        server = "local"
        command_args = user_input

    error = handler.validate(command_args)
    if error:
        return {"response_type": "ephemeral", "text": error}

    if handler.is_local:
        channel_id = form_data.get("channel_id")
        result_text = handler.execute_local(server, command_args, {"channel_id": channel_id})
        return {
            "response_type": "in_channel",
            "text": result_text
        }

    final_cmd = handler.build_shell_command(command_args)

    background_tasks.add_task(background_job_runner, server, final_cmd, response_url)
    
    return {
        "response_type": "ephemeral",
        "text": f"⏳ Processing `{command_name} {user_input}`..."
    }
