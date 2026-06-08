import os
content = open(r'C:\Users\QQ136\Documents\New project\token-proxy-git\proxy\router.py', encoding='utf-8').read()
content = content.replace(
    'from config import UPSTREAM_PROVIDERS, SERVICE_NAME, DEFAULT_BALANCE',
    'from config import UPSTREAM_PROVIDERS, SERVICE_NAME, DEFAULT_BALANCE, DISABLE_REGISTRATION'
)
old = 'async def register_user(body: dict):\n    name = body.get("name", "").strip()'
new = 'async def register_user(body: dict):\n    if DISABLE_REGISTRATION:\n        return JSONResponse(status_code=403, content={"error": "注册已关闭，请联系管理员开通账号"})\n    name = body.get("name", "").strip()'
if old in content:
    content = content.replace(old, new)
    open(r'C:\Users\QQ136\Documents\New project\token-proxy-git\proxy\router.py', 'w', encoding='utf-8').write(content)
    print('OK - router.py updated')
else:
    print('ERROR: old pattern not found')
