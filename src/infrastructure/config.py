from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./data/harvest.db"
    weather_latitude: float = 4.7110
    weather_longitude: float = -74.0721
    news_feed_url: str = "https://news.google.com/rss?hl=es-419&gl=CO&ceid=CO:es-419"
    http_timeout_seconds: float = 5.0

    api_key: str
    reports_dir: str = "./data/reports"
    scheduler_timezone: str = "America/Bogota"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_address: str = "no-reply@harvest.local"
    smtp_use_tls: bool = True
    report_recipients: list[str] = ["ops@harvest.local"]


settings = Settings()  # type: ignore[call-arg]
