"""入口文件 — 启动代理服务"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from config import HOST, PORT, SERVICE_NAME
from proxy.router import router

app = FastAPI(
    title=f"{SERVICE_NAME} - AI API 代理服务",
    description="将 OpenAI 兼容格式的请求转发到 DeepSeek / 智谱等上游 AI 供应商，支持鉴权、计费、多供应商管理。",
    version="1.0.0",
    swagger_ui_parameters={
        "locale": "zh-cn",
        "defaultModelsExpandDepth": -1,
        "docExpansion": "list",
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
    contact={
        "name": "管理员",
        "url": "http://localhost:8000",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/admin")
async def admin_page():
    return RedirectResponse(url="/static/admin.html")


@app.get("/user")
async def user_page():
    return RedirectResponse(url="/static/user.html")


@app.get("/")
async def root():
    return {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "docs": "/docs (API 文档)",
        "health": "/v1/health (健康检查)",
        "models": "/v1/models (模型列表)",
    }


if __name__ == "__main__":
    print(f"正在启动 {SERVICE_NAME}...")
    print(f"监听地址: http://{HOST}:{PORT}")
    print(f"API 文档: http://localhost:{PORT}/docs")
    uvicorn.run(app, host=HOST, port=PORT)
# Admin UI: /admin /user
