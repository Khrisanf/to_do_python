from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/task_tracker"
    access_token_expire_minutes: int = 60 * 24 * 7
    token_length: int = 32

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")


settings = Settings()
