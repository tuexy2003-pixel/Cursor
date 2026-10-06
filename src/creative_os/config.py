from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="COS_", extra="ignore")

    database_url: str = "sqlite:///./storage/creative_os.db"
    snapshot_root: Path = Path("source_snapshots/2026-10-05")
    storage_root: Path = Path("storage")
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    operator_identity: str = "operator"
    live_text_reasoning_enabled: bool = False
    text_reasoning_daily_run_limit: int = 10
    text_reasoning_max_input_tokens: int = 100_000
    text_reasoning_max_output_tokens: int = 4096
    text_reasoning_max_providers: int = 2

    def resolved_snapshot_root(self) -> Path:
        path = self.snapshot_root
        if not path.is_absolute():
            path = repo_root() / path
        return path

    def resolved_storage_root(self) -> Path:
        path = self.storage_root
        if not path.is_absolute():
            path = repo_root() / path
        return path

    def sqlite_path(self) -> Path | None:
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            return None
        raw = self.database_url.removeprefix(prefix)
        path = Path(raw)
        if not path.is_absolute():
            path = repo_root() / path
        return path


def get_settings() -> Settings:
    return Settings()
