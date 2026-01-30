"""
Configuration management for the District Pathway Analyzer.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class KnowledgeBaseConfig(BaseModel):
    """Configuration for knowledge base documents."""

    ai_foundations_pdf: str = "assets/AI_Foundations.pdf"
    career_clusters_pdf: str = "assets/Guidebook-National-Career-Clusters-Framework.pdf"


class LLMConfig(BaseModel):
    """Configuration for the LLM."""

    provider: str = "anthropic"
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000
    temperature: float = 0.3


class DiscoveryConfig(BaseModel):
    """Configuration for discovery phase."""

    max_search_results: int = 10
    timeout_seconds: int = 30
    cache_enabled: bool = True
    cache_ttl_days: int = 30


class GatesConfig(BaseModel):
    """Configuration for analysis gates."""

    min_courses_found: int = 3
    min_verified_percentage: float = 0.80
    max_uncertain_percentage: float = 0.20


class OutputConfig(BaseModel):
    """Configuration for output generation."""

    default_format: str = "pdf"
    include_technical_notes: bool = True
    include_assumptions: bool = True
    logo_path: str = "assets/code_org_logo.png"


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: str = "INFO"
    file: str = "logs/analysis.log"


class Config(BaseModel):
    """Complete application configuration."""

    knowledge_base: KnowledgeBaseConfig = Field(default_factory=KnowledgeBaseConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    discovery: DiscoveryConfig = Field(default_factory=DiscoveryConfig)
    gates: GatesConfig = Field(default_factory=GatesConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment or default config file."""
        config_path = os.environ.get("CONFIG_PATH", "config.yaml")
        if Path(config_path).exists():
            return cls.from_yaml(config_path)
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def load_config(path: str) -> Config:
    """Load configuration from a specific path and set as global."""
    global _config
    _config = Config.from_yaml(path)
    return _config
