"""

Storage backends for user data persistence.

Supports Supabase (recommended) and local file fallback.

"""

import json

import os

from typing import Dict, Optional, Any

import httpx





class DataStore:

    """Abstract data store for user data."""



    def load(self) -> Optional[bytes]:

        raise NotImplementedError



    def save(self, data: bytes) -> bool:

        raise NotImplementedError





class FileDataStore(DataStore):

    """Store data as a local JSON file."""



    def __init__(self, path: str):

        self.path = path



    def load(self) -> Optional[bytes]:

        try:

            data_dir = os.path.dirname(self.path)

            if data_dir:

                os.makedirs(data_dir, exist_ok=True)

            with open(self.path, "r", encoding="utf-8") as f:

                return f.read().encode("utf-8")

        except (FileNotFoundError, json.JSONDecodeError):

            return None

        except Exception:

            return None



    def save(self, data: bytes) -> bool:

        try:

            data_dir = os.path.dirname(self.path)

            if data_dir:

                os.makedirs(data_dir, exist_ok=True)

            with open(self.path, "w", encoding="utf-8") as f:

                f.write(data.decode("utf-8"))

            return True

        except Exception:

            return False





class SupabaseDataStore(DataStore):

    """Store data in Supabase PostgreSQL via REST API.

    

    Requires a table named 'app_data' with columns: id (TEXT PK), value (TEXT).

    Table creation SQL:

      CREATE TABLE app_data (id TEXT PRIMARY KEY, value TEXT NOT NULL);

    """



    def __init__(self, url: str, key: str, row_id: str = "token_proxy_users", timeout: int = 10):
        self.timeout = timeout

        self.url = url.rstrip("/")

        self._headers = {

            "apikey": key,

            "Authorization": f"Bearer {key}",

            "Content-Type": "application/json",

        }

        self.row_id = row_id

        self._endpoint = f"{self.url}/rest/v1/app_data"



    def load(self) -> Optional[bytes]:

        try:

            resp = httpx.get(

                self._endpoint,

                headers=self._headers,

                params={"id": f"eq.{self.row_id}", "select": "value"},

                timeout=self.timeout,

            )

            if resp.status_code == 200:

                rows = resp.json()

                if rows and rows[0].get("value"):

                    return rows[0]["value"].encode("utf-8")

            return None

        except Exception:

            return None



    def save(self, data: bytes) -> bool:

        try:

            value = data.decode("utf-8")

            # Upsert: insert if not exists, update if exists

            resp = httpx.post(

                self._endpoint,

                headers={

                    **self._headers,

                    "Prefer": "resolution=merge-duplicates",

                },

                json={"id": self.row_id, "value": value},

                timeout=10,

            )

            return resp.status_code in (200, 201, 204)

        except Exception:

            return False





def create_store() -> DataStore:
    """Create the appropriate DataStore based on environment config.
    
    Uses file storage by default. Enable Supabase by setting SUPABASE_ENABLED=true
    """
    from config import SUPABASE_URL as _SU, SUPABASE_KEY as _SK, USER_DATA_PATH
    
    supabase_enabled = os.environ.get("SUPABASE_ENABLED", "false").lower() in ("1", "true", "yes")
    
    if supabase_enabled:
        supabase_url = os.environ.get("SUPABASE_URL", _SU).strip()
        supabase_key = os.environ.get("SUPABASE_KEY", _SK).strip()
        if supabase_url and supabase_key:
            print("[Storage] Using Supabase backend")
            return SupabaseDataStore(supabase_url, supabase_key, timeout=5)
    
    print("[Storage] Using file backend:" + " " + USER_DATA_PATH)
    os.makedirs(os.path.dirname(USER_DATA_PATH), exist_ok=True)
    return FileDataStore(USER_DATA_PATH)



    if supabase_url and supabase_key:

        print("[Storage] Using Supabase backend")

        return SupabaseDataStore(supabase_url, supabase_key)



    from config import USER_DATA_PATH

    print(f"[Storage] Using file backend: {USER_DATA_PATH}")

    return FileDataStore(USER_DATA_PATH)

