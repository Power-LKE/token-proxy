"""入口文件 — 启动代理服务"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
import pathlib as _p

from config import HOST, PORT, SERVICE_NAME
from proxy.router import router

app = FastAPI(
    title=f"{SERVICE_NAME} - AI API 代理服务",
    description="将 OpenAI 兼容格式的请求转发到 DeepSeek / 智谱等上游 AI 供应商，支持鉴权、计费、多供应商管理。",
    version="1.0.0",
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


def _serve_html(file_name: str) -> Response:
    file_path = _p.Path(__file__).parent / "static" / file_name
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        return Response(
            content=content,
            media_type="text/html; charset=utf-8",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
    return Response(
        content=f"<h1>{file_name} not found</h1>",
        media_type="text/html",
        status_code=404,
    )


@app.get("/")
async def root():
    return _serve_html("index.html")


@app.get("/dashboard")
async def dashboard():
    return _serve_html("dashboard.html")


@app.get("/admin")
async def admin_page():
    return _serve_html("admin.html")


@app.get("/user")
async def user_page():
    return RedirectResponse(url="/static/user.html")


if __name__ == "__main__":
    print(f"正在启动 {SERVICE_NAME}...")
    print(f"监听地址: http://{HOST}:{PORT}")
    print(f"API 文档: http://localhost:{PORT}/docs")
    uvicorn.run(app, host=HOST, port=PORT)
