# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import sys
import re
from textwrap import wrap
from colorama import Fore, Style, init
from utils.spinner import spinner_start, spinner_stop

init(autoreset=True)

def format_in_box_markdown(text, width=80, color=Fore.RED):
    paragraphs = text.strip().split("\n")
    formatted_lines = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            formatted_lines.append("")
            continue
        wrapped = wrap(para, width=width-4)
        formatted_lines.extend(wrapped)

    max_len = max(len(line) for line in formatted_lines) if formatted_lines else 0
    top_border = f"{color}╭{'─' * (max_len + 2)}╮{Style.RESET_ALL}"
    bottom_border = f"{color}╰{'─' * (max_len + 2)}╯{Style.RESET_ALL}"
    box_lines = [top_border]
    for line in formatted_lines:
        box_lines.append(f"{color}│{Style.RESET_ALL} {line.ljust(max_len)} {color}│{Style.RESET_ALL}")
    box_lines.append(bottom_border)
    return "\n".join(box_lines)

SORRY_KEYWORDS = [
    "sorry", "apology", "apologies", "unfortunately",
    "i can't", "i cannot", "can't assist",
    "desculpa", "desculpe", "sinto muito", "lamento"
] # i hate when LLM model has his morality issues typesh.

def is_apology(text):
    return any(k in text.lower() for k in SORRY_KEYWORDS)

def clean_shell_input(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    text = "".join(char for char in text if char.isprintable() or char in "\n\r\t")
    return text.strip()
