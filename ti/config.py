"""Central config: paths, model routing, feature flags.

Single source of truth. Read via `from ti.config import settings`.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=(),
    )

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    langfuse_public_key: str = Field(default="", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com", alias="LANGFUSE_HOST"
    )

    # Model routing — right model for the job (plan §3 decision 6).
    model_screen: str = Field(default="claude-haiku-4-5", alias="TI_MODEL_SCREEN")
    model_classify: str = Field(default="claude-sonnet-4-6", alias="TI_MODEL_CLASSIFY")
    model_synthesize: str = Field(
        default="claude-opus-4-7", alias="TI_MODEL_SYNTHESIZE"
    )

    # Paths
    data_raw: Path = REPO_ROOT / "data" / "raw"
    data_processed: Path = REPO_ROOT / "data" / "processed"
    data_enriched: Path = REPO_ROOT / "data" / "enriched"
    data_graph: Path = REPO_ROOT / "data" / "graph"
    prompts_dir: Path = REPO_ROOT / "ti" / "governance" / "prompts"
    audit_log: Path = REPO_ROOT / "data" / "audit.jsonl"


settings = Settings()
