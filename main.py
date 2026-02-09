import httpx
from fastapi import FastAPI, Depends, BackgroundTasks, Request
from src.security import verify_slack_signature
from src.ssh_client import execute_remote_command
from src.command import get_command_handler

app = FastAPI()

def background_job_runner(final_cmd: str, response_url: str):
    result_text = execute_remote_command(final_cmd)
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
    command_name = form_data.get("command")
    user_input = form_data.get("text", "").strip()
    response_url = form_data.get("response_url")

    handler = get_command_handler(command_name)
    if not handler:
        return {"response_type": "ephemeral", "text": f"❌ Unknown command: `{command_name}`"}

    error = handler.validate(user_input)
    if error:
        return {"response_type": "ephemeral", "text": error}

    final_cmd = handler.build_shell_command(user_input)

    background_tasks.add_task(background_job_runner, final_cmd, response_url)
    
    return {
        "response_type": "ephemeral",
        "text": f"⏳ Processing `{command_name} {user_input}`..."
    }
