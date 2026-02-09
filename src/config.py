from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SLACK_SIGNING_SECRET: str
    SLACK_BOT_TOKEN: str
    SLACK_LOG_CHANNEL_ID: str
    
    SSH_HOST: str
    SSH_USER: str

    TUNNEL_TOKEN: str

    SLURM_CMD_SQUEUE: str
    SLURM_CMD_SSHARE: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
