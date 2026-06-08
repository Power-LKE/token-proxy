"""Forward requests to upstream AI API providers"""
import httpx
import tiktoken
from typing import Tuple, Optional, AsyncGenerator
from config import UPSTREAM_PROVIDERS, MARKUP


def _detect_provider(model: str) -> Optional[str]:
    for provider_key, provider in UPSTREAM_PROVIDERS.items():
        if model in provider.models:
            return provider_key
    return None


def _count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return len(text) // 2


def _estimate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    provider_key = _detect_provider(model)
    if not provider_key:
        return 0.0
    provider = UPSTREAM_PROVIDERS[provider_key]
    price_per_1m = provider.models.get(model, 0)
    cost = (prompt_tokens / 1_000_000) * price_per_1m
    cost += (completion_tokens / 1_000_000) * price_per_1m * 2
    return cost


def _calculate_sell_price(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    cost = _estimate_cost(prompt_tokens, completion_tokens, model)
    return round(cost * MARKUP, 6)


def _build_url(provider, request_data: dict) -> str:
    """Build the API URL based on provider type."""
    if provider.is_azure:
        deployment = provider.azure_deployment
        model = request_data.get("model", "gpt-4o")
        return (
            f"{provider.api_base.rstrip('/')}"
            f"/openai/deployments/{deployment}"
            f"/chat/completions?api-version={provider.azure_api_version}"
        )
    else:
        from urllib.parse import urljoin
        return urljoin(provider.api_base, "/v1/chat/completions")


def _build_headers(provider, api_key: str) -> dict:
    """Build request headers based on provider type."""
    if provider.is_azure:
        return {
            "api-key": api_key,
            "Content-Type": "application/json",
        }
    else:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }


async def forward_chat_completion(
    provider_key: str,
    api_key: str,
    request_data: dict,
) -> Tuple[dict, float]:
    provider = UPSTREAM_PROVIDERS[provider_key]
    url = _build_url(provider, request_data)
    headers = _build_headers(provider, api_key)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=request_data)
        resp.raise_for_status()
        data = resp.json()

    usage = data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    sell_price = _calculate_sell_price(prompt_tokens, completion_tokens, request_data["model"])

    return data, sell_price


async def forward_stream(
    provider_key: str,
    api_key: str,
    request_data: dict,
) -> AsyncGenerator[bytes, None]:
    provider = UPSTREAM_PROVIDERS[provider_key]
    url = _build_url(provider, request_data)
    headers = _build_headers(provider, api_key)
    
    request_data["stream"] = True
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", url, headers=headers, json=request_data) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    yield (line + "\n\n").encode("utf-8")
