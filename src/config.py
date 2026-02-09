from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SLACK_SIGNING_SECRET: str
    
    SSH_HOST: str
    SSH_USER: str

    SLURM_CMD_SQUEUE: str
    SLURM_CMD_SSHARE: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
