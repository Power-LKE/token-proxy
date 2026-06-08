import re, os

BASE = r'C:\Users\QQ136\Documents\New project\token-proxy-git'

# 1. models.py: add email field to UserInfo
path = os.path.join(BASE, 'proxy', 'models.py')
content = open(path, encoding='utf-8').read()
content = content.replace(
    '    created_at: str = ""\n    transactions: List[dict] = []',
    '    created_at: str = ""\n    email: str = ""\n    transactions: List[dict] = []'
)
content = content.replace(
    'class RegistrationRequest(BaseModel):\n    name: str = Field(..., min_length=1, max_length=50)',
    'class RegistrationRequest(BaseModel):\n    name: str = Field(..., min_length=1, max_length=50)\n    email: str = Field(default="", max_length=200)'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK - models.py')

# 2. auth.py: update register() to accept email
path = os.path.join(BASE, 'proxy', 'auth.py')
content = open(path, encoding='utf-8').read()

# Update register method
content = content.replace(
    '    def register(self, name):\n        for u in self._users.values():\n            if u.name == name:\n                return None\n        return self.create_user(name, note="registration_bonus")',
    '    def register(self, name, email=""):\n        email = email.strip().lower()\n        for u in self._users.values():\n            if u.name == name:\n                return None\n            if email and u.email and u.email.lower() == email:\n                return None\n        return self.create_user(name, note="registration_bonus", email=email)'
)

# Update create_user to accept email parameter
content = content.replace(
    '    def create_user(self, name, balance=None, note=""):\n        api_key = self._generate_key()\n        user = UserInfo(\n            api_key=api_key, name=name,\n            balance=balance if balance is not None else DEFAULT_BALANCE,\n            created_at=datetime.now().isoformat(),\n        )',
    '    def create_user(self, name, balance=None, note="", email=""):\n        api_key = self._generate_key()\n        user = UserInfo(\n            api_key=api_key, name=name,\n            balance=balance if balance is not None else DEFAULT_BALANCE,\n            created_at=datetime.now().isoformat(),\n            email=email,\n        )'
)

open(path, 'w', encoding='utf-8').write(content)
print('OK - auth.py')

# 3. router.py: update /v1/register to accept email
path = os.path.join(BASE, 'proxy', 'router.py')
content = open(path, encoding='utf-8').read()

# Replace the register_user function
old_register = '''async def register_user(body: dict):
    if DISABLE_REGISTRATION:
        return JSONResponse(status_code=403, content={"error": "注册已关闭，请联系管理员开通账号"})
    name = body.get("name", "").strip()
    if not name:
        return JSONResponse(status_code=400, content={"error": "请输入用户名"})
    if len(name) > 50:
        return JSONResponse(status_code=400, content={"error": "用户名过长"})
    user = user_manager.register(name)
    if not user:
        return JSONResponse(status_code=409, content={"error": "用户名已被使用"})
    return {"api_key": user.api_key, "name": user.name, "balance": user.balance, "message": "注册成功，赠送启动余额"}'''

new_register = '''async def register_user(body: dict):
    if DISABLE_REGISTRATION:
        return JSONResponse(status_code=403, content={"error": "注册已关闭，请联系管理员开通账号"})
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    if not name:
        return JSONResponse(status_code=400, content={"error": "请输入用户名"})
    if len(name) > 50:
        return JSONResponse(status_code=400, content={"error": "用户名过长"})
    if not email or "@" not in email or "." not in email:
        return JSONResponse(status_code=400, content={"error": "请输入有效的邮箱地址"})
    user = user_manager.register(name, email)
    if not user:
        return JSONResponse(status_code=409, content={"error": "用户名或邮箱已被使用"})
    return {"api_key": user.api_key, "name": user.name, "email": user.email, "balance": user.balance, "message": "注册成功，赠送启动余额"}'''

content = content.replace(old_register, new_register)
open(path, 'w', encoding='utf-8').write(content)
print('OK - router.py')

print('\\nAll files updated!')
