# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import os

IS_WINDOWS = os.name == "nt"

# general config
VERSION = "7.2"
NEKO_BINARY = "https://raw.githubusercontent.com/ARCANGEL0/nekoCLI/main/neko"
VERSION_URL = "https://raw.githubusercontent.com/ARCANGEL0/nekoCLI/main/version.txt"
API_OLLAMA_URL = "http://localhost:11434"
VIDEO_URL = "https://api.arcangelo.net/genVideo"
PHOTOEDIT_URL = "https://api.arcangelo.net/edit"
VISION_URL = "https://api.arcangelo.net/neko_vision"
COMMAND_URL = "https://api.arcangelo.net/neko_shell"
CODE_URL = "https://api.arcangelo.net/neko_code"
EXTRACT_URL = "https://api.arcangelo.net/neko_extract"
IMAGEGEN_URL = "https://api.arcangelo.net/imagine"
BASE_URL = "https://api.arcangelo.net/neko"
GPT4_URL = "https://api.arcangelo.net/gpt4"

# NEKO directory structure
NEKO_DIR = os.path.expanduser("~/NEKO")
SESSIONS_DIR = os.path.join(NEKO_DIR, "sessions")
IMAGES_DIR = os.path.join(NEKO_DIR, "images")
VIDEOS_DIR = os.path.join(NEKO_DIR, "videos")

# Legacy paths (for backwards compatibility)
HISTORY_DIR = os.path.expanduser("~/neko")
HISTORY_FILE = os.path.join(NEKO_DIR, "chat.json")
TOKEN_NEKO_FILE = os.path.join(NEKO_DIR, ".token_neko")
MEDIA_DIR = IMAGES_DIR

MAX_RETRIES = 10
RETRY_DELAY = 10
