"""Configuration - Edit upstream API keys and pricing here"""
import os
from dataclasses import dataclass, field
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class UpstreamProvider:
    name: str
    api_base: str
    api_key_env: str
    models: Dict[str, float] = field(default_factory=dict)
    """model_name -> price per 1M input tokens"""
    
    azure_deployment: Optional[str] = None
    """Azure OpenAI deployment name (if using Azure)"""
    
    azure_api_version: str = "2024-10-21"
    """Azure OpenAI API version"""
    
    @property
    def is_azure(self) -> bool:
        return self.azure_deployment is not None


UPSTREAM_PROVIDERS: Dict[str, UpstreamProvider] = {
    "deepseek": UpstreamProvider(
        name="DeepSeek",
        api_base="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
        models={
            "deepseek-chat": 1.0,
            "deepseek-reasoner": 4.0,
        },
    ),
    "openai": UpstreamProvider(
        name="OpenAI",
        api_base="https://api.openai.com",
        api_key_env="OPENAI_API_KEY",
        models={
            "gpt-4o": 2.5,
            "gpt-4o-mini": 0.15,
            "gpt-4-turbo": 10.0,
            "gpt-3.5-turbo": 0.5,
        },
    ),
    "api2d": UpstreamProvider(
        name="API2D (OpenAI)",
        api_base="https://openapi.api2d.com",
        api_key_env="API2D_API_KEY",
        models={
            "gpt-4o": 2.5,
            "gpt-4o-mini": 0.15,
            "gpt-4-turbo": 10.0,
            "gpt-3.5-turbo": 0.5,
        },
    ),
}

HOST = os.getenv("PROXY_HOST", "0.0.0.0")
PORT = int(os.getenv("PROXY_PORT", "8000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "TokenProxy")
DEFAULT_BALANCE = float(os.getenv("DEFAULT_BALANCE", "1.0"))
USER_DATA_PATH = os.getenv("USER_DATA_PATH", "/tmp/users.json")
MARKUP = float(os.getenv("MARKUP", "1.3"))


# Supabase (optional, for persistent data across deploys)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yxcmfajehkstxrsxzpqg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4Y21mYWplaGtzdHhyc3h6cHFnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4ODc1MTUsImV4cCI6MjA5NjQ2MzUxNX0.ab4sjO2lVdwj0btLQO41Txzo1ZssGU_KZL2H3E3VbcE")


# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yxcmfajehkstxrsxzpqg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4Y21mYWplaGtzdHhyc3h6cHFnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4ODc1MTUsImV4cCI6MjA5NjQ2MzUxNX0.ab4sjO2lVdwj0btLQO41Txzo1ZssGU_KZL2H3E3VbcE")
