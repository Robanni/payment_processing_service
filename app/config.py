from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/payments"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    API_KEY: str = "changeme"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
