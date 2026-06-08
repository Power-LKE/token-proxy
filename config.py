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
    "zhipu": UpstreamProvider(
        name="Zhipu GLM",
        api_base="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="ZHIPU_API_KEY",
        models={
            "glm-4": 0.1,
            "glm-4-flash": 0.01,
        },
    ),
    "azure-gpt4o": UpstreamProvider(
        name="Azure OpenAI GPT-4o",
        api_base=os.getenv("AZURE_OPENAI_ENDPOINT", "https://YOUR_RESOURCE.openai.azure.com"),
        api_key_env="AZURE_OPENAI_API_KEY",
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        models={
            "gpt-4o": 2.5,
            "gpt-4o-mini": 0.15,
        },
    ),
}

HOST = os.getenv("PROXY_HOST", "0.0.0.0")
PORT = int(os.getenv("PROXY_PORT", "8000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "TokenProxy")
DEFAULT_BALANCE = float(os.getenv("DEFAULT_BALANCE", "1.0"))
USER_DATA_PATH = os.getenv("USER_DATA_PATH", "data/users.json")
MARKUP = float(os.getenv("MARKUP", "1.3"))
