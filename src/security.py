import hmac
import hashlib
import time
from fastapi import Request, HTTPException, Header
from .config import get_settings

settings = get_settings()

async def verify_slack_signature(
    request: Request,
    x_slack_signature: str = Header(...),
    x_slack_request_timestamp: str = Header(...)
):
    if abs(time.time() - int(x_slack_request_timestamp)) > 60 * 5:
        raise HTTPException(status_code=400, detail="Request timestamp expired")

    body_bytes = await request.body()
    body_text = body_bytes.decode()

    sig_basestring = f"v0:{x_slack_request_timestamp}:{body_text}"

    my_signature = "v0=" + hmac.new(
        settings.SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_signature, x_slack_signature):
        raise HTTPException(status_code=403, detail="Invalid Slack signature")
