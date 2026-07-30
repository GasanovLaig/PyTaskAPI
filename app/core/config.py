from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str
    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    AUTH_SECRET_KEY: str = "dd46ad1483074445be8bb4ad7b7eafb2a75be8bd418379457c8202b6f28a7241"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_EXPIRATION: int = 30
    
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    CLICKHOUSE_HOST: str = "127.0.0.1"
    CLICKHOUSE_PORT: int = 8123
    @property
    def CLICKHOUSE_URL(self) -> str:
        return f"http://{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_PORT}"
    
    MAIL_SMTP_HOST: str = "127.0.0.1"
    MAIL_SMTP_PORT: int = 1025
    MAIL_SENDER_EMAIL: str = "robot@pytaskapi.test"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix=""
    )
    
settings = Settings()
