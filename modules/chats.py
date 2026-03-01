# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import os
import json

try:
    from .config import HISTORY_DIR, HISTORY_FILE, TOKEN_NEKO_FILE, CHATS_AGENT_FILE
except ImportError:
    from modules.config import HISTORY_DIR, HISTORY_FILE, TOKEN_NEKO_FILE, CHATS_AGENT_FILE

LEGACY_TOKEN_AGENT_FILE = os.path.join(HISTORY_DIR, ".token_agent")
LEGACY_HISTORY_FILE = os.path.join(HISTORY_DIR, "chats.json")
LEGACY_AGENT_FILE = os.path.join(HISTORY_DIR, ".chats_agent")
VALID_ROLES = {"user", "assistant", "system"}

def ensure_history_dir():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def _sanitize_history(payload):
    if not isinstance(payload, list):
        return []
    sanitized = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in VALID_ROLES and isinstance(content, str):
            sanitized.append({"role": role, "content": content})
    return sanitized

def _load_history_file(path):
    ensure_history_dir()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return _sanitize_history(payload)
    except Exception:
        return []

def _save_history_file(path, history):
    ensure_history_dir()
    safe_history = _sanitize_history(history)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(safe_history, f, indent=2, ensure_ascii=False)

def load_agent_history():
    ensure_history_dir()
    if os.path.isfile(CHATS_AGENT_FILE):
        return _load_history_file(CHATS_AGENT_FILE)
    return _load_history_file(LEGACY_AGENT_FILE)

def save_agent_history(history):
    _save_history_file(CHATS_AGENT_FILE, history)

def load_history():
    ensure_history_dir()
    if os.path.isfile(HISTORY_FILE):
        return _load_history_file(HISTORY_FILE)
    return _load_history_file(LEGACY_HISTORY_FILE)

def save_history(history):
    _save_history_file(HISTORY_FILE, history)

def reset_history():
    ensure_history_dir()
    if os.path.isfile(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    if os.path.isfile(LEGACY_HISTORY_FILE):
        os.remove(LEGACY_HISTORY_FILE)
    if os.path.isfile(TOKEN_NEKO_FILE):
        os.remove(TOKEN_NEKO_FILE)
    if os.path.isfile(CHATS_AGENT_FILE):
        os.remove(CHATS_AGENT_FILE)
    if os.path.isfile(LEGACY_AGENT_FILE):
        os.remove(LEGACY_AGENT_FILE)
    if os.path.isfile(LEGACY_TOKEN_AGENT_FILE):
        os.remove(LEGACY_TOKEN_AGENT_FILE)
