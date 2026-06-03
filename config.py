"""
Configuration — Edit upstream API keys and pricing here
"""
import os
from dataclasses import dataclass, field
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# 设置上游 API Key（会覆盖 .env 文件中的值，但不覆盖已存在的系统环境变量）
os.environ.setdefault("DEEPSEEK_API_KEY", "sk-1d8fc48c02e34404998c933534fd8d04")


@dataclass
class UpstreamProvider:
    name: str
    api_base: str
    api_key_env: str
    models: Dict[str, float] = field(default_factory=dict)


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
}

HOST = os.getenv("PROXY_HOST", "0.0.0.0")
PORT = int(os.getenv("PROXY_PORT", "8000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "TokenProxy")
DEFAULT_BALANCE = float(os.getenv("DEFAULT_BALANCE", "1.0"))
USER_DATA_PATH = os.getenv("USER_DATA_PATH", "/tmp/users.json")
MARKUP = float(os.getenv("MARKUP", "1.3"))
