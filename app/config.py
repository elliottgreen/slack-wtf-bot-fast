from pydantic import BaseSettings

class Settings(BaseSettings):
    SLACK_TOKEN: str
    DATA_URL: str

    class Config:
        env_file = '.env'
