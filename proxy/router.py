"""API 路由 — 中文标签"""
import time
import os
from fastapi import APIRouter, Request
from datetime import datetime
from fastapi.responses import JSONResponse
from config import UPSTREAM_PROVIDERS, SERVICE_NAME, DEFAULT_BALANCE, DISABLE_REGISTRATION
from proxy.models import ChatCompletionRequest
from proxy.auth import user_manager
from proxy.upstream import _detect_provider, forward_chat_completion

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
        # Only show models with configured API keys
        env_key = os.getenv(provider.api_key_env, "").strip()
        if not env_key:
            continue
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

    # Strip streaming flag so upstream returns regular JSON
    request_data = body.model_dump()
    request_data.pop("stream", None)
    try:
        resp_data, sell_price = await forward_chat_completion(
            provider_key, upstream_api_key, request_data
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"error": {"message": f"上游请求失败: {str(e)}", "type": "upstream_error"}},
        )

    usage = resp_data.get("usage", {})
    if not user_manager.deduct_balance(api_key, sell_price, model=body.model, tokens=usage.get("total_tokens", 0)):
        return JSONResponse(
            status_code=402,
            content={"error": {"message": "余额不足", "type": "insufficient_balance"}},
        )

    resp_data["_cost"] = sell_price
    remaining = user_manager.get_user(api_key)
    resp_data["_balance_remaining"] = round(remaining.balance, 4) if remaining else 0
    return resp_data


# === 用户自助注册 ===

@router.post("/v1/register", summary="用户注册", tags=["用户"])
async def register_user(body: dict):
    if DISABLE_REGISTRATION:
        return JSONResponse(status_code=403, content={"error": "注册已关闭，请联系管理员开通账号"})
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    if not name:
        return JSONResponse(status_code=400, content={"error": "请输入用户名"})
    if len(name) > 50:
        return JSONResponse(status_code=400, content={"error": "用户名过长"})
    if not email or "@" not in email:
        return JSONResponse(status_code=400, content={"error": "请输入有效的邮箱地址"})
    user = user_manager.register(name, email)
    if not user:
        return JSONResponse(status_code=409, content={"error": "用户名或邮箱已被使用"})
    return {"api_key": user.api_key, "name": user.name, "email": user.email, "balance": user.balance, "message": "注册成功，注册成功"}


@router.post("/v1/user/query", summary="用户面板", tags=["用户"])
async def user_query(request: Request):
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not api_key:
        return JSONResponse(status_code=401, content={"error": "请提供 API Key"})
    user = user_manager.get_user(api_key)
    if not user:
        return JSONResponse(status_code=401, content={"error": "无效的 API Key"})
    return {"name": user.name, "balance": user.balance, "is_active": user.is_active, "created_at": user.created_at, "transactions": user.transactions[-20:][::-1]}

# === 管理后台 API ===

@router.api_route("/v1/admin/verify", methods=["GET", "POST"], summary="验证管理员", tags=["管理"])
async def admin_verify(request: Request):
    api_key = _get_api_key(request)
    if not api_key or not user_manager.is_admin_key(api_key):
        return JSONResponse(status_code=401, content={"error": "无效的管理员 Key"})
    users = user_manager.list_users()
    total_balance = sum(u.balance for u in users)
    return {
        "status": "ok",
        "admin_key": api_key,
        "user_count": len(users),
        "total_balance": round(total_balance, 4),
    }


@router.get("/v1/admin/users", summary="用户列表", tags=["管理"])
async def admin_list_users(request: Request):
    api_key = _get_api_key(request)
    if not api_key or not user_manager.is_admin_key(api_key):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    users = user_manager.list_users()
    return {
        "users": [
            {
                "name": u.name,
                "api_key": u.api_key,
                "balance": u.balance,
                "is_active": u.is_active,
                "created_at": u.created_at,
                "email": u.email,
            }
            for u in users
        ]
    }


@router.post("/v1/admin/users", summary="创建用户", tags=["管理"])
async def admin_create_user(request: Request):
    api_key = _get_api_key(request)
    if not api_key or not user_manager.is_admin_key(api_key):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    body = await request.json()
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    balance = float(body.get("balance", DEFAULT_BALANCE))
    if not name:
        return JSONResponse(status_code=400, content={"error": "请提供用户名"})
    user = user_manager.create_user(name, balance, email=email)
    result = {"api_key": user.api_key, "name": user.name, "balance": user.balance}
    if email:
        result["email"] = email
    return result


@router.post("/v1/admin/users/topup", summary="用户充值", tags=["管理"])
async def admin_topup(request: Request):
    api_key = _get_api_key(request)
    if not api_key or not user_manager.is_admin_key(api_key):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    body = await request.json()
    user_key = body.get("api_key", "").strip()
    amount = float(body.get("amount", 0))
    if amount <= 0:
        return JSONResponse(status_code=400, content={"error": "充值金额必须大于 0"})
    user = user_manager.get_user(user_key)
    if not user:
        return JSONResponse(status_code=404, content={"error": "用户不存在"})
    user.balance += amount
    user_manager._save()
    return {"name": user.name, "balance": user.balance}


@router.post("/v1/admin/users/toggle", summary="启用/禁用用户", tags=["管理"])
async def admin_toggle_user(request: Request):
    api_key = _get_api_key(request)
    if not api_key or not user_manager.is_admin_key(api_key):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    body = await request.json()
    user_key = body.get("api_key", "").strip()
    user = user_manager.get_user(user_key)
    if not user:
        return JSONResponse(status_code=404, content={"error": "用户不存在"})
    user.is_active = not user.is_active
    user_manager._save()
    return {"name": user.name, "is_active": user.is_active}



@router.get("/v1/admin/stats", summary="系统统计", tags=["管理"])
async def admin_stats(request: Request):
    api_key = _get_api_key(request)
    if not api_key or not user_manager.is_admin_key(api_key):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    users = user_manager.list_users()
    total_balance = sum(u.balance for u in users)
    active_users = sum(1 for u in users if u.is_active)
    today = datetime.now().isoformat()[:10]

    total_topup = 0.0
    today_revenue = 0.0
    today_tokens = 0
    all_txns = []

    for u in users:
        for tx in u.transactions:
            ttype = tx.get("type", "")
            ttime = tx.get("time", "")
            if ttype in ("manual_create",) and tx.get("amount", 0) > 0:
                total_topup += tx["amount"]
            if ttype == "registration_bonus":
                total_topup += tx.get("amount", 0)
            if ttime.startswith(today):
                if ttype == "usage":
                    today_revenue += abs(tx.get("amount", 0))
                    today_tokens += tx.get("tokens", 0)
            all_txns.append({
                "time": ttime,
                "user": u.name,
                "type": ttype,
                "amount": tx.get("amount", 0),
                "model": tx.get("model", ""),
                "tokens": tx.get("tokens", 0),
            })

    all_txns.sort(key=lambda x: x["time"], reverse=True)

    return {
        "total_users": len(users),
        "active_users": active_users,
        "total_balance": round(total_balance, 4),
        "total_topup": round(total_topup, 4),
        "today_revenue": round(today_revenue, 4),
        "today_tokens": today_tokens,
        "recent_transactions": all_txns[:200],
    }

@router.get("/v1/admin/init", summary="获取管理员 Key", tags=["管理"])
async def admin_init():
    """获取当前管理员 API Key（无需认证）"""
    key = user_manager.admin_api_key
    if not key:
        return JSONResponse(status_code=404, content={"error": "没有管理员用户"})
    return {"admin_key": key, "message": "请立即保存此 Key"}
