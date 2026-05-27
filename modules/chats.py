# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import os
import json
from datetime import datetime
from typing import List, Optional, Dict

try:
    from .config import SESSIONS_DIR, HISTORY_DIR, HISTORY_FILE, TOKEN_NEKO_FILE
except ImportError:
    from modules.config import SESSIONS_DIR, HISTORY_DIR, HISTORY_FILE, TOKEN_NEKO_FILE

LEGACY_HISTORY_FILE = os.path.join(HISTORY_DIR, "chats.json")

VALID_ROLES = {"user", "assistant", "system"}

def persistSessionsDir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR, exist_ok=True)

def persistentHistory():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR, exist_ok=True)

def parseHistory(payload):
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

def load_history(path):
    persistentHistory()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return parseHistory(payload)
    except Exception:
        return []

def saveHistory(path, history):
    persistentHistory()
    safe_history = parseHistory(history)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(safe_history, f, indent=2, ensure_ascii=False)

def load_history():
    persistentHistory()
    if os.path.isfile(HISTORY_FILE):
        return load_history(HISTORY_FILE)
    return load_history(LEGACY_HISTORY_FILE)

def save_history(history):
    saveHistory(HISTORY_FILE, history)

def list_sessions() -> List[Dict[str, str]]:
    """List all available sessions"""
    persistSessionsDir()
    sessions = []
    
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SESSIONS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session_id = data.get('session_id', filename.replace('.json', ''))
                    created = data.get('created', 'Unknown')
                    session_type = data.get('session_type', 'CHAT')
                    messages_count = len(data.get('messages', []))
                    
                    sessions.append({
                        'id': session_id,
                        'type': session_type,
                        'created': created,
                        'messages': messages_count
                    })
            except (json.JSONDecodeError, IOError):
                continue
    
    return sorted(sessions, key=lambda x: x['created'], reverse=True)

def load_session(session_id: str) -> Optional[Dict]:
    """Load a specific session by ID/name"""
    persistSessionsDir()
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not os.path.isfile(session_file):
        return None
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError):
        return None

def session_exists(session_id: str) -> bool:
    """Check if a session exists"""
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    return os.path.isfile(session_file)

def get_session_type(session_id: str) -> str:
    data = load_session(session_id)
    if data:
        return data.get('session_type', 'CHAT')
    return 'UNKNOWN'

def save_session_data(session_id: str, session_type: str, messages: List[Dict], created: Optional[str] = None):
    """Save session data to configured session directory"""
    persistSessionsDir()
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not created:
        created = datetime.now().isoformat()
    
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump({
            "session_id": session_id,
            "session_type": session_type,
            "created": created,
            "messages": messages
        }, f, indent=2, ensure_ascii=False)

def reset_all_sessions():
    """Clear all sessions"""
    persistSessionsDir()
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            os.remove(os.path.join(SESSIONS_DIR, filename))
