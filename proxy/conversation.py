"""
Conversation history storage and management.
Local JSON file + optional Supabase backend.
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from proxy.storage import create_store, DataStore


class ConversationManager:
    """Manages chat conversation history."""

    def __init__(self):
        self._store: DataStore = create_store(row_id="linkpower_conversations")
        self._data: Dict[str, List[dict]] = {}  # user_api_key -> [conversations]
        self._load()

    def _load(self):
        try:
            raw = self._store.load()
            if raw:
                self._data = json.loads(raw.decode("utf-8"))
        except Exception:
            self._data = {}

    def _save(self):
        data = json.dumps(self._data, ensure_ascii=False, indent=2).encode("utf-8")
        self._store.save(data)

    def list(self, api_key: str, page: int = 1, per_page: int = 50) -> dict:
        """List conversations for a user, newest first."""
        user_convs = self._data.get(api_key, [])
        total = len(user_convs)
        start = (page - 1) * per_page
        end = start + per_page
        convs = sorted(user_convs, key=lambda c: c.get("updated_at", ""), reverse=True)
        return {
            "conversations": convs[start:end],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def get(self, api_key: str, conv_id: str) -> Optional[dict]:
        """Get a single conversation by ID."""
        user_convs = self._data.get(api_key, [])
        for c in user_convs:
            if c.get("id") == conv_id:
                return c
        return None

    def create(self, api_key: str, conv_data: dict) -> dict:
        """Create a new conversation."""
        conv_id = conv_data.get("id") or str(int(datetime.now().timestamp() * 1000))
        conv = {
            "id": conv_id,
            "title": conv_data.get("title", "新对话"),
            "messages": conv_data.get("messages", []),
            "model": conv_data.get("model", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        user_convs = self._data.get(api_key, [])
        user_convs.insert(0, conv)
        self._data[api_key] = user_convs
        self._save()
        return conv

    def update(self, api_key: str, conv_id: str, updates: dict) -> Optional[dict]:
        """Update a conversation (title, messages, etc.)."""
        user_convs = self._data.get(api_key, [])
        for c in user_convs:
            if c.get("id") == conv_id:
                c.update(updates)
                c["updated_at"] = datetime.now().isoformat()
                self._save()
                return c
        return None

    def delete(self, api_key: str, conv_id: str) -> bool:
        """Delete a conversation."""
        user_convs = self._data.get(api_key, [])
        for i, c in enumerate(user_convs):
            if c.get("id") == conv_id:
                user_convs.pop(i)
                self._data[api_key] = user_convs
                self._save()
                return True
        return False

    def save(self, api_key: str, convs: list):
        """Batch save all conversations for a user."""
        self._data[api_key] = convs
        self._save()


conv_manager = ConversationManager()
