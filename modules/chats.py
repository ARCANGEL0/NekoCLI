import os
import json
import uuid

from config import HISTORY_DIR, HISTORY_FILE, TOKEN_NEKO_FILE, CHATS_AGENT_FILE

LEGACY_TOKEN_AGENT_FILE = os.path.join(HISTORY_DIR, ".token_agent")

def ensure_history_dir():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def _new_session_id():
    return uuid.uuid4().hex

def _read_or_create_token():
    ensure_history_dir()
    if os.path.isfile(TOKEN_NEKO_FILE):
        try:
            with open(TOKEN_NEKO_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()
            if len(token) == 32 and all(c in "0123456789abcdefABCDEF" for c in token):
                return token.lower()
        except Exception:
            pass

    token = _new_session_id()
    with open(TOKEN_NEKO_FILE, "w", encoding="utf-8") as f:
        f.write(token)
    return token

def get_session_id(agent=False):
    # For compatibility, agent mode no longer uses token files.
    if agent:
        return None
    return _read_or_create_token()

def load_agent_history():
    ensure_history_dir()
    if not os.path.isfile(CHATS_AGENT_FILE):
        return []
    try:
        with open(CHATS_AGENT_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, list):
            return []
        sanitized = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "system") and isinstance(content, str):
                sanitized.append({"role": role, "content": content})
        return sanitized
    except Exception:
        return []

def save_agent_history(history):
    ensure_history_dir()
    safe_history = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "system") and isinstance(content, str):
            safe_history.append({"role": role, "content": content})
    with open(CHATS_AGENT_FILE, "w", encoding="utf-8") as f:
        json.dump(safe_history, f, indent=2, ensure_ascii=False)

def load_history():
    # Kept for backward compatibility with old chats.json flow.
    ensure_history_dir()
    if not os.path.isfile(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    # Legacy no-op path retained for compatibility.
    ensure_history_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def reset_history():
    ensure_history_dir()
    if os.path.isfile(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    if os.path.isfile(TOKEN_NEKO_FILE):
        os.remove(TOKEN_NEKO_FILE)
    if os.path.isfile(CHATS_AGENT_FILE):
        os.remove(CHATS_AGENT_FILE)
    if os.path.isfile(LEGACY_TOKEN_AGENT_FILE):
        os.remove(LEGACY_TOKEN_AGENT_FILE)
