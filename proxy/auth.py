import hashlib, json, uuid
from datetime import datetime
from typing import Optional, Dict
from config import DEFAULT_BALANCE
from proxy.models import UserInfo
from proxy.storage import create_store, DataStore

def _deterministic_admin_key() -> str:
    import os as _os
    val = _os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if val:
        digest = hashlib.sha256(val.encode()).hexdigest()[:24]
        return "admin-" + digest
    return "admin-d9832619d29729c5eb6e91df"


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return True  # legacy users without password
    return _hash_password(password) == password_hash

class UserManager:
    def __init__(self):
        self._store = create_store()
        self._users = {}
        self._load()

    def _load(self):
        try:
            raw_bytes = self._store.load()
            if raw_bytes:
                raw = json.loads(raw_bytes.decode("utf-8"))
                for item in raw:
                    u = UserInfo(**item)
                    self._users[u.api_key] = u
        except Exception:
            pass

        import os as _os
        admin_key_env = _os.environ.get("ADMIN_API_KEY", "").strip()
        expected = admin_key_env if admin_key_env else _deterministic_admin_key()

        # Force admin key to deterministic value
        for k in list(self._users.keys()):
            if self._users[k].name == "admin" and k != expected:
                del self._users[k]

        if expected not in self._users:
            admin = UserInfo(
                api_key=expected, name="admin", balance=100.0, is_active=True,
                created_at=datetime.now().isoformat(),
            )
            self._users[expected] = admin
            print(f"[Init] Admin ready, API Key: {expected}")
            self._save()

    def _save(self):
        raw = [u.model_dump() for u in self._users.values()]
        data = json.dumps(raw, ensure_ascii=False, indent=2).encode("utf-8")
        self._store.save(data)

    def _generate_key(self, prefix="sk"):
        return prefix + "-" + uuid.uuid4().hex

    def is_admin_key(self, api_key):
        user = self._users.get(api_key)
        if user and user.name == "admin":
            return api_key
        return None

    def is_reseller_key(self, api_key):
        user = self._users.get(api_key)
        return user is not None and user.role == "reseller"

    def authenticate(self, api_key):
        user = self._users.get(api_key)
        if user and user.is_active and user.balance > 0:
            return user
        return None

    def deduct_balance(self, api_key, amount, model="", tokens=0):
        user = self._users.get(api_key)
        if user and user.balance >= amount:
            before = user.balance
            user.balance -= amount
            tx = {"time": datetime.now().isoformat(), "type": "usage", "amount": -amount, "balance_before": before, "balance_after": user.balance, "model": model, "tokens": tokens}
            user.transactions.append(tx)
            self._save()
            return True
        return False

    def register(self, name, email="", password=""):
        import re
        email = email.strip().lower()

        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.\w{2,}$', email):
            return None

        for u in self._users.values():
            if u.name == name:
                return None
            if email and u.email and u.email.lower() == email:
                return None
        user = self.create_user(name, note="registration_bonus", email=email)
        if password:
            user.password_hash = _hash_password(password)
            self._save()
        return user

    def create_user(self, name, balance=None, note="", email="", parent_key=""):
        api_key = self._generate_key()
        user = UserInfo(
            api_key=api_key, name=name,
            balance=balance if balance is not None else DEFAULT_BALANCE,
            created_at=datetime.now().isoformat(),
            email=email,
            role="user",
            parent_key=parent_key,
        )
        user.transactions.append({"time": datetime.now().isoformat(), "type": note or "manual_create", "amount": user.balance, "balance_before": 0, "balance_after": user.balance})
        self._users[api_key] = user
        self._save()
        return user

    def find_by_email_and_password(self, email, password):
        email = email.strip().lower()
        for u in self._users.values():
            if u.email and u.email.lower() == email:
                if _verify_password(password, u.password_hash):
                    return u
        return None

    def find_by_email(self, email):
        """????????"""
        email = email.strip().lower()
        for u in self._users.values():
            if u.email and u.email.lower() == email:
                return u
        return None

    def get_user(self, api_key):
        return self._users.get(api_key)

    def delete_user(self, api_key):
        user = self._users.pop(api_key, None)
        if user:
            self._save()
            return True
        return False

    def filter_by_parent(self, parent_key):
        return [u for u in self._users.values() if u.parent_key == parent_key]

    @property
    def admin_api_key(self):
        for user in self._users.values():
            if user.name == "admin":
                return user.api_key
        return None

    def list_users(self):
        return list(self._users.values())

user_manager = UserManager()