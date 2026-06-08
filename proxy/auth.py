"""User authentication and balance management"""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict
from config import DEFAULT_BALANCE
from proxy.models import UserInfo
from proxy.storage import create_store, DataStore


class UserManager:
    def __init__(self):
        self._store: DataStore = create_store()
        self._users: Dict[str, UserInfo] = {}
        self._load()

    def _load(self):
        try:
            raw_bytes = self._store.load()
            if raw_bytes:
                raw = json.loads(raw_bytes.decode("utf-8"))
                for item in raw:
                    u = UserInfo(**item)
                    self._users[u.api_key] = u
                return
        except Exception:
            pass

        # No data found or error ? create admin user
        import os as _os
        admin_key_env = _os.environ.get("ADMIN_API_KEY", "").strip()
        admin_key = admin_key_env if admin_key_env else self._generate_key("admin")
        admin = UserInfo(
            api_key=admin_key,
            name="admin",
            balance=100.0,
            is_active=True,
            created_at=datetime.now().isoformat(),
        )
        self._users[admin_key] = admin
        self._save()
        print(f"[Init] Created admin user, API Key: {admin_key}")

    def _save(self):
        raw = [u.model_dump() for u in self._users.values()]
        data = json.dumps(raw, ensure_ascii=False, indent=2).encode("utf-8")
        self._store.save(data)

    def _generate_key(self, prefix: str = "sk") -> str:
        return f"{prefix}-{uuid.uuid4().hex}"

    def is_admin_key(self, api_key: str) -> bool:
        user = self._users.get(api_key)
        return user is not None and user.name == "admin"

    @property
    def admin_api_key(self) -> Optional[str]:
        for key, user in self._users.items():
            if user.name == "admin":
                return key
        return None

    def authenticate(self, api_key: str) -> Optional[UserInfo]:
        user = self._users.get(api_key)
        if user and user.is_active and user.balance > 0:
            return user
        return None

    def deduct_balance(self, api_key: str, amount: float, model: str = "", tokens: int = 0) -> bool:
        user = self._users.get(api_key)
        if user and user.balance >= amount:
            before = user.balance
            user.balance -= amount
            tx = {"time": datetime.now().isoformat(), "type": "usage", "amount": -amount, "balance_before": before, "balance_after": user.balance, "model": model, "tokens": tokens}
            user.transactions.append(tx)
            self._save()
            return True
        return False

    def register(self, name: str):
        for u in self._users.values():
            if u.name == name:
                return None
        return self.create_user(name, note="registration_bonus")

    def create_user(self, name: str, balance: float = None, note: str = "") -> UserInfo:
        api_key = self._generate_key()
        user = UserInfo(
            api_key=api_key,
            name=name,
            balance=balance if balance is not None else DEFAULT_BALANCE,
            created_at=datetime.now().isoformat(),
        )
        user.transactions.append({"time": datetime.now().isoformat(), "type": note if note else "manual_create", "amount": user.balance, "balance_before": 0, "balance_after": user.balance})
        self._users[api_key] = user
        self._save()
        return user

    def get_user(self, api_key: str) -> Optional[UserInfo]:
        return self._users.get(api_key)

    def list_users(self) -> list[UserInfo]:
        return list(self._users.values())


user_manager = UserManager()
