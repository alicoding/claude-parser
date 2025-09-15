#!/usr/bin/env python3
"""
Settings - 100% Pydantic Settings Framework Delegation
SRP: Single responsibility for configuration management
"""

from typing import Dict
from pydantic import Field
from pydantic_settings import BaseSettings


class TokenSettings(BaseSettings):
    """100% Pydantic: Token analysis configuration settings"""
    
    default_model: str = Field(default="gpt-4", description="Default model for token counting")
    
    # API Cost settings (per 1K tokens)
    gpt_4_cost: float = Field(default=0.03, description="GPT-4 cost per 1K tokens")
    gpt_35_turbo_cost: float = Field(default=0.002, description="GPT-3.5 Turbo cost per 1K tokens")
    claude_3_cost: float = Field(default=0.015, description="Claude-3 cost per 1K tokens")
    default_cost: float = Field(default=0.03, description="Default cost per 1K tokens")
    
    @property
    def cost_per_1k(self) -> Dict[str, float]:
        """100% framework delegation: Build cost mapping from settings"""
        return {
            "gpt-4": self.gpt_4_cost,
            "gpt-3.5-turbo": self.gpt_35_turbo_cost,
            "claude-3": self.claude_3_cost
        }
    
    class Config:
        """Pydantic configuration for environment variable loading"""
        env_prefix = "CLAUDE_PARSER_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore unknown environment variables


class AnalyticsSettings(BaseSettings):
    """100% Pydantic: Analytics configuration settings"""
    
    max_message_preview_length: int = Field(default=100, description="Max length for message preview")
    enable_extended_analytics: bool = Field(default=True, description="Enable extended analytics features")
    
    class Config:
        """Pydantic configuration for environment variable loading"""
        env_prefix = "CLAUDE_PARSER_ANALYTICS_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore unknown environment variables


class AppSettings(BaseSettings):
    """100% Pydantic: Main application settings"""
    
    # Token settings
    token: TokenSettings = Field(default_factory=TokenSettings)
    
    # Analytics settings  
    analytics: AnalyticsSettings = Field(default_factory=AnalyticsSettings)
    
    # Session settings
    default_session_limit: int = Field(default=1000, description="Default session message limit")
    
    class Config:
        """Pydantic configuration for environment variable loading"""
        env_prefix = "CLAUDE_PARSER_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore unknown environment variables


# Global settings instance - 100% Pydantic Settings delegation
settings = AppSettings()