# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import sys
import time
import threading
import itertools


# npm-like spinner attempt to run along iwth neko 
_spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
_spinner_delay = 0.10
_spinner_running = False
_spinner_thread = None
_spinner_text = " L O A D I N G "


def _spinner_animate():
    for i, frame in enumerate(itertools.cycle(_spinner_frames)):
        if not _spinner_running:
            break
        dot_count = (i // 3) % 4 + 1
        dots = "." * dot_count
        spaces = " " * (4 - dot_count)
        sys.stdout.write(f"\r  {frame}  {_spinner_text}{dots}{spaces}")
        sys.stdout.flush()
        time.sleep(_spinner_delay)


def spinner_start(text=None):
    global _spinner_running, _spinner_thread, _spinner_text
    if _spinner_running:
        return
    if isinstance(text, str) and text.strip():
        _spinner_text = f" {text} "
    else:
        _spinner_text = " L O A D I N G "
    _spinner_running = True
    sys.stdout.write("\n\n")
    _spinner_thread = threading.Thread(target=_spinner_animate, daemon=True)
    _spinner_thread.start()


def spinner_stop():
    global _spinner_running
    _spinner_running = False
    if _spinner_thread:
        _spinner_thread.join()
    sys.stdout.write("\r" + " " * (len(_spinner_text) + 10) + "\r")
    sys.stdout.flush()
