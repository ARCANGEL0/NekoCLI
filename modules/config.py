# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import os

IS_WINDOWS = os.name == "nt"

# general config
VERSION = "6.7"
NEKO_BINARY = "https://raw.githubusercontent.com/ARCANGEL0/nekoCLI/main/neko"
VERSION_URL = "https://raw.githubusercontent.com/ARCANGEL0/nekoCLI/main/version.txt"
API_OLLAMA_URL = "http://localhost:11434"
VIDEO_URL = "https://api.arcangelo.net/genVideo"
PENTEST_URL = "https://api.arcangelo.net/neko_agent"
PHOTOEDIT_URL = "https://api.arcangelo.net/edit"
VISION_URL = "https://api.arcangelo.net/neko_vision"
COMMAND_URL = "https://api.arcangelo.net/neko_shell"
CODE_URL = "https://api.arcangelo.net/neko_code"
EXTRACT_URL = "https://api.arcangelo.net/neko_extract"
IMAGEGEN_URL = "https://api.arcangelo.net/imagine"
BASE_URL = "https://api.arcangelo.net/neko"
HISTORY_DIR = os.path.expanduser("~/neko")
HISTORY_FILE = os.path.join(HISTORY_DIR, "chat.json")
TOKEN_NEKO_FILE = os.path.join(HISTORY_DIR, ".token_neko")
CHATS_AGENT_FILE = os.path.join(HISTORY_DIR, "pentest.json")
MEDIA_DIR = os.path.join(HISTORY_DIR, "media/")
MAX_RETRIES = 10
RETRY_DELAY = 10
