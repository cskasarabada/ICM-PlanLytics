from __future__ import annotations

"""Unified configuration for comp_plan module.

Config hierarchy: YAML file -> env var overrides -> defaults.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class CompPlanConfig(BaseModel):
    """Configuration for comp_plan module."""

    # --- LLM settings ---
    llm_provider: str = Field(default="stub", description="ollama | openai | anthropic | stub")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_temperature: float = Field(default=0.2)
    llm_max_tokens: int = Field(default=2000)
    llm_api_base: Optional[str] = None
    llm_api_key: Optional[str] = None

    # --- File handling ---
    max_upload_mb: int = 50
    allowed_extensions: list[str] = Field(default=[".docx", ".pdf", ".txt"])
    data_dir: str = "data"

    # --- Security ---
    security_enabled: bool = True
    pii_scrub_inherent: bool = True  # PII scrubbing is ALWAYS on for data transfer

    # --- API settings ---
    api_keys: str = ""
    cors_origins: list[str] = Field(default=["*"])


def load_config(config_path: Optional[str] = None) -> CompPlanConfig:
    """Load config from YAML + env overrides."""
    path = config_path or os.environ.get("COMP_PLAN_CONFIG", "config/comp_plan_config.yaml")
    resolved = Path(path)

    cfg_dict: dict = {}
    if resolved.exists():
        try:
            import yaml
            with open(resolved) as f:
                cfg_dict = yaml.safe_load(f) or {}
        except Exception:
            pass

    env_overrides = {
        "llm_provider": ["COMP_PLAN_LLM_PROVIDER", "LLM_BACKEND", "OPENAI_API_KEY"],
        "llm_model": ["COMP_PLAN_LLM_MODEL", "OPENAI_MODEL"],
        "llm_api_key": ["COMP_PLAN_LLM_API_KEY", "OPENAI_API_KEY"],
        "llm_api_base": ["COMP_PLAN_LLM_API_BASE", "OLLAMA_URL"],
        "max_upload_mb": ["MAX_UPLOAD_MB"],
        "api_keys": ["COMP_PLAN_API_KEYS"],
    }

    for cfg_key, env_keys in env_overrides.items():
        for env_key in env_keys:
            val = os.environ.get(env_key)
            if val is not None:
                # Special: if OPENAI_API_KEY is set, auto-detect provider
                if cfg_key == "llm_provider" and env_key == "OPENAI_API_KEY":
                    cfg_dict["llm_provider"] = "openai"
                else:
                    cfg_dict[cfg_key] = val
                break

    valid_fields = set(CompPlanConfig.model_fields.keys())
    return CompPlanConfig(**{k: v for k, v in cfg_dict.items() if k in valid_fields})


_config: Optional[CompPlanConfig] = None


def get_config() -> CompPlanConfig:
    """Get or create the singleton config."""
    global _config
    if _config is None:
        _config = load_config()
    return _config
