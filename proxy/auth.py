"""
User authentication and balance management
"""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict
from config import USER_DATA_PATH, DEFAULT_BALANCE
from proxy.models import UserInfo


class UserManager:
    def __init__(self, data_path: str = USER_DATA_PATH):
        self.data_path = data_path
        self._users: Dict[str, UserInfo] = {}
        self._load()

    def _load(self):
        import os as _os
        data_dir = _os.path.dirname(self.data_path)
        if data_dir:
            _os.makedirs(data_dir, exist_ok=True)
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                for item in raw:
                    u = UserInfo(**item)
                    self._users[u.api_key] = u
        except (FileNotFoundError, json.JSONDecodeError):
            admin_key = self._generate_key("admin")
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
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)

    def _generate_key(self, prefix: str = "sk") -> str:
        return f"{prefix}-{uuid.uuid4().hex}"

    def is_admin_key(self, api_key: str) -> bool:
        """Check if the given API key belongs to the admin user."""
        user = self._users.get(api_key)
        return user is not None and user.name == "admin"

    @property
    def admin_api_key(self) -> Optional[str]:
        """Get the admin user's API key."""
        for key, user in self._users.items():
            if user.name == "admin":
                return key
        return None

    def authenticate(self, api_key: str) -> Optional[UserInfo]:
        user = self._users.get(api_key)
        if user and user.is_active and user.balance > 0:
            return user
        return None

    def deduct_balance(self, api_key: str, amount: float) -> bool:
        user = self._users.get(api_key)
        if user and user.balance >= amount:
            user.balance -= amount
            self._save()
            return True
        return False

    def create_user(self, name: str, balance: float = None) -> UserInfo:
        api_key = self._generate_key()
        user = UserInfo(
            api_key=api_key,
            name=name,
            balance=balance if balance is not None else DEFAULT_BALANCE,
            created_at=datetime.now().isoformat(),
        )
        self._users[api_key] = user
        self._save()
        return user

    def get_user(self, api_key: str) -> Optional[UserInfo]:
        return self._users.get(api_key)

    def list_users(self) -> list[UserInfo]:
        return list(self._users.values())


user_manager = UserManager()
