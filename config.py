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
            "gpt-4.1-mini": 0.40,
        },
    ),

    "doubao": UpstreamProvider(
        name="豆包 (Doubao)",
        api_base="https://ark.cn-beijing.volces.com/api/v3",
        api_key_env="DOUBAO_API_KEY",
        models={
            "doubao-1.5-pro-32k": 1.0,
            "doubao-1.5-lite-32k": 0.3,
            "doubao-pro-32k": 2.0,
        },
    ),

    "zhipu": UpstreamProvider(
        name="智谱 GLM",
        api_base="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="ZHIPU_API_KEY",
        models={
            "glm-4-plus": 5.0,
            "glm-4-flash": 0.1,
        },
    ),

    "moonshot": UpstreamProvider(
        name="Moonshot (Kimi)",
        api_base="https://api.moonshot.cn/v1",
        api_key_env="MOONSHOT_API_KEY",
        models={
            "moonshot-v1-8k": 1.0,
            "moonshot-v1-32k": 2.0,
            "moonshot-v1-128k": 6.0,
        },
    ),

    "qwen": UpstreamProvider(
        name="通义千问",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key_env="QWEN_API_KEY",
        models={
            "qwen-plus": 0.8,
            "qwen-max": 2.0,
            "qwen-turbo": 0.3,
        },
    ),

    "api2d": UpstreamProvider(
        name="API2D",
        api_base="https://openapi.api2d.com",
        api_key_env="API2D_API_KEY",
        models={
            "gpt-4o": 2.5,
            "gpt-4o-mini": 0.15,
        },
    ),

}



HOST = os.getenv("PROXY_HOST", "0.0.0.0")

PORT = int(os.getenv("PROXY_PORT", "8000"))

SERVICE_NAME = os.getenv("SERVICE_NAME", "LinkPower")

DEFAULT_BALANCE = float(os.getenv("DEFAULT_BALANCE", "1.0"))

USER_DATA_PATH = os.getenv("USER_DATA_PATH", "/tmp/users.json")

MARKUP = float(os.getenv("MARKUP", "1.3"))


# Free registration
DISABLE_REGISTRATION = os.getenv("DISABLE_REGISTRATION", "false").lower() in ("1", "true", "yes")





# Supabase (required for persistent data across deploys)
# Set SUPABASE_URL and SUPABASE_KEY in Render environment variables
# Create a free account at https://supabase.com
# Then create a project and run this SQL in SQL Editor:
#   CREATE TABLE IF NOT EXISTS app_data (id TEXT PRIMARY KEY, value TEXT NOT NULL);
# Then insert initial data:
#   INSERT INTO app_data (id, value) VALUES ('token_proxy_users', '[]');
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yxcmfajehkstxrsxzpqg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4Y21mYWplaGtzdHhyc3h6cHFnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4ODc1MTUsImV4cCI6MjA5NjQ2MzUxNX0.ab4sjO2lVdwj0btLQO41Txzo1ZssGU_KZL2H3E3VbcE")
