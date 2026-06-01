"""API 路由 — 中文标签"""
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from config import UPSTREAM_PROVIDERS, SERVICE_NAME
from proxy.models import ChatCompletionRequest
from proxy.auth import user_manager
from proxy.upstream import _detect_provider, forward_chat_completion
import os

router = APIRouter(tags=["代理服务"])


def _get_api_key(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return auth_header


@router.get("/v1/health", summary="健康检查", description="检查服务是否正常运行")
async def health():
    return {"status": "ok", "service": SERVICE_NAME}


@router.get("/v1/models", summary="模型列表", description="获取所有可用的 AI 模型及其定价")
async def list_models():
    models = []
    for provider_key, provider in UPSTREAM_PROVIDERS.items():
        for model_name, price in provider.models.items():
            models.append({
                "id": model_name,
                "object": "model",
                "created": int(time.time()),
                "owned_by": provider.name,
                "price_per_1m_input": price,
            })
    return {"object": "list", "data": models}


@router.get("/v1/balance", summary="查询余额", description="查询当前 API Key 的余额和使用状态")
async def get_balance(request: Request):
    api_key = _get_api_key(request)
    if not api_key:
        return JSONResponse(status_code=401, content={"error": "请提供 API Key"})
    user = user_manager.get_user(api_key)
    if not user:
        return JSONResponse(status_code=401, content={"error": "无效的 API Key"})
    return {"name": user.name, "balance": user.balance, "is_active": user.is_active}


def _list_supported_models_str() -> str:
    models = []
    for provider_key, provider in UPSTREAM_PROVIDERS.items():
        for model_name in provider.models:
            models.append(model_name)
    return ", ".join(models)


@router.post("/v1/chat/completions", summary="聊天补全", description="发送聊天消息到 AI 模型，获取回复（兼容 OpenAI 格式）")
async def chat_completions(request: Request, body: ChatCompletionRequest):
    api_key = _get_api_key(request)
    user = user_manager.authenticate(api_key)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": {"message": "API Key 无效或余额不足", "type": "auth_error"}},
        )

    provider_key = _detect_provider(body.model)
    if not provider_key:
        return JSONResponse(
            status_code=400,
            content={"error": {"message": f"不支持的模型: {body.model}。支持的模型: {_list_supported_models_str()}", "type": "invalid_model"}},
        )

    upstream_api_key = os.getenv(UPSTREAM_PROVIDERS[provider_key].api_key_env, "")
    if not upstream_api_key:
        return JSONResponse(
            status_code=500,
            content={"error": {"message": "上游 API Key 未配置", "type": "server_error"}},
        )

    try:
        resp_data, sell_price = await forward_chat_completion(
            provider_key, upstream_api_key, body.model_dump()
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"error": {"message": f"上游请求失败: {str(e)}", "type": "upstream_error"}},
        )

    if not user_manager.deduct_balance(api_key, sell_price):
        return JSONResponse(
            status_code=402,
            content={"error": {"message": "余额不足", "type": "insufficient_balance"}},
        )

    resp_data["_cost"] = sell_price
    remaining = user_manager.get_user(api_key)
    resp_data["_balance_remaining"] = round(remaining.balance, 4) if remaining else 0
    return resp_data
