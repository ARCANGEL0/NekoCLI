#!/usr/bin/env python3

import os
import re
import json
import sys
import shlex
import threading
import asyncio
import subprocess
import signal
import shutil
import tempfile
import webbrowser
from typing import Optional, List, Dict, Any
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Input, TextArea, Button
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.message import Message
from textual import work
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Console
import traceback

ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
RICH_STYLE_TAG_RE = re.compile(r"\[(?:/?(?:bold|dim|red|green|yellow|cyan|magenta|white|black|blue)(?: [^\]]+)?)\]")

try:
    from .config import VERSION
    from .gui import ChatSession
    from .ai import nekoAI
except ImportError:
    from modules.config import VERSION
    from modules.gui import ChatSession
    from modules.ai import nekoAI


class theme:
#color configs
    BG = "#0f0f0f"
    HDR = "#1a1a1a"
    PNL = "#1f1f2e"
    ACC = "#00d4ff"
    OK = "#00ff88"
    WARN = "#ffaa00"
    ERR = "#ff0088"
    TXT = "#a8a8a8"
    DIM = "#4a4a4a"
    FRAME = "#00ffff"
    BORDER = "#00ff88"


THEMES = {
    "ultrablack": {
        "name": "Ultra Black",
        "BG": "#000000", "HDR": "#000000", "PNL": "#0d0d0d",
        "ACC": "#00ffff", "OK": "#00ffff", "WARN": "#00dddd",
        "ERR": "#ff0000", "TXT": "#00ffff", "DIM": "#1a1a1a",
        "FRAME": "#00ffff", "BORDER": "#00ff88",
    },
    "atom-one-dark": {
        "name": "Atom One Dark",
        "BG": "#282c34", "HDR": "#21252b", "PNL": "#2c313a",
        "ACC": "#61afef", "OK": "#98c379", "WARN": "#e5c07b",
        "ERR": "#e06c75", "TXT": "#abb2bf", "DIM": "#5c6370",
        "FRAME": "#61afef", "BORDER": "#98c379",
    },
    "dracula": {
        "name": "Dracula",
        "BG": "#282a36", "HDR": "#21222c", "PNL": "#383a59",
        "ACC": "#8be9fd", "OK": "#50fa7b", "WARN": "#f1fa8c",
        "ERR": "#ff5555", "TXT": "#f8f8f2", "DIM": "#6272a4",
        "FRAME": "#8be9fd", "BORDER": "#50fa7b",
    },
    "nord": {
        "name": "Nord",
        "BG": "#2e3440", "HDR": "#252b37", "PNL": "#3b4252",
        "ACC": "#88c0d0", "OK": "#a3be8c", "WARN": "#ebcb8b",
        "ERR": "#bf616a", "TXT": "#e5e9f0", "DIM": "#4c566a",
        "FRAME": "#88c0d0", "BORDER": "#a3be8c",
    },
    "gruvbox": {
        "name": "Gruvbox",
        "BG": "#282828", "HDR": "#1d2021", "PNL": "#3c3836",
        "ACC": "#ebdbb2", "OK": "#b8bb26", "WARN": "#fabd2f",
        "ERR": "#fb4934", "TXT": "#ebdbb2", "DIM": "#665c54",
        "FRAME": "#fabd2f", "BORDER": "#b8bb26",
    },
    "solarized-dark": {
        "name": "Solarized Dark",
        "BG": "#002b36", "HDR": "#073642", "PNL": "#094352",
        "ACC": "#839496", "OK": "#859900", "WARN": "#b58900",
        "ERR": "#dc322f", "TXT": "#93a1a1", "DIM": "#586e75",
        "FRAME": "#268bd2", "BORDER": "#2aa198",
    },
    "solarized-light": {
        "name": "Solarized Light",
        "HDR": "#fdf6e3", "BG": "#fdf6e3", "PNL": "#eee8d5",
        "ACC": "#657b83", "OK": "#859900", "WARN": "#b58900",
        "ERR": "#dc322f", "TXT": "#657b83", "DIM": "#93a1a1",
        "FRAME": "#268bd2", "BORDER": "#2aa198",
    },
    "monokai": {
        "name": "Monokai",
        "BG": "#272822", "HDR": "#1e1f1c", "PNL": "#3e3d32",
        "ACC": "#f8f8f2", "OK": "#a6e22e", "WARN": "#e6db74",
        "ERR": "#f92672", "TXT": "#f8f8f2", "DIM": "#75715e",
        "FRAME": "#66d9ef", "BORDER": "#a6e22e",
    },
    "onedark": {
        "name": "One Dark",
        "BG": "#282c34", "HDR": "#21252b", "PNL": "#3a3f4b",
        "ACC": "#abb2bf", "OK": "#98c379", "WARN": "#e5c07b",
        "ERR": "#e06c75", "TXT": "#abb2bf", "DIM": "#5c6370",
        "FRAME": "#61afef", "BORDER": "#56b6c2",
    },
    "github": {
        "name": "GitHub",
        "BG": "#ffffff", "HDR": "#f6f8fa", "PNL": "#f0f0f0",
        "ACC": "#24292e", "OK": "#22863a", "WARN": "#b08800",
        "ERR": "#d73a49", "TXT": "#24292e", "DIM": "#6a737d",
        "FRAME": "#0366d6", "BORDER": "#28a745",
    },
    "tokyonight": {
        "name": "Tokyo Night",
        "BG": "#1a1b26", "HDR": "#16161e", "PNL": "#24283b",
        "ACC": "#a9b1d6", "OK": "#9ece6a", "WARN": "#e0af68",
        "ERR": "#f7768e", "TXT": "#a9b1d6", "DIM": "#565f89",
        "FRAME": "#7aa2f7", "BORDER": "#bb9af7",
    },
}


def apply_theme(theme_dict: dict):
    theme.BG = theme_dict.get("BG", "#282a36")
    theme.HDR = theme_dict.get("HDR", "#21222c")
    theme.PNL = theme_dict.get("PNL", "#383a59")
    theme.ACC = theme_dict.get("ACC", "#8be9fd")
    theme.OK = theme_dict.get("OK", "#50fa7b")
    theme.WARN = theme_dict.get("WARN", "#f1fa8c")
    theme.ERR = theme_dict.get("ERR", "#ff5555")
    theme.TXT = theme_dict.get("TXT", "#f8f8f2")
    theme.DIM = theme_dict.get("DIM", "#6272a4")
    theme.FRAME = theme_dict.get("FRAME", "#00ffff")
    theme.BORDER = theme_dict.get("BORDER", "#00ff88")
default_theme = 0
theme_list = list(THEMES.keys())
current_theme = default_theme
apply_theme(THEMES[theme_list[default_theme]])
def get_current_theme_name():
    return theme_list[current_theme]
def cycle_theme():
    global current_theme
    current_theme = (current_theme + 1) % len(theme_list)
    apply_theme(THEMES[theme_list[current_theme]])
    return theme_list[current_theme]
def get_system_info() -> str:
    """This only sends sysinfo at basic level, so it can suggest better approaches for compatible commands in your machine, 
    as good practices, i'll presume you're reading all this before running the script. 
    If you wish, feel free to remove all this to send empty string to API, to avoid sending any data
    --
    """
    import subprocess
    info = []
    
    # Net info, sends local tun0 IP in case you're in a CTF, so it can send proper commands already with your attacker IP and machine IP
    try:
        result = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and not line.strip().startswith('127'):
                info.append(f"IPv4: {line.strip().split()[1]}")
    except:
        pass
    
    try:
        result = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split('\n'):
            if 'tun0' in line:
                info.append(f"VPN (tun0): {line.strip()}")
    except:
        pass
    
    try:
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True, timeout=5)
        if result.stdout.strip():
            info.append(f"All IPs: {result.stdout.strip()}")
    except:
        pass

    try:
        result = subprocess.run(["uname", "-a"], capture_output=True, text=True, timeout=5)
        if result.stdout:
            info.append(f"Kernel: {result.stdout.strip()}")
    except:
        pass
    
    # OS info to trigger better compatible commands
    try:
        result = subprocess.run(["cat", "/etc/os-release"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split('\n'):
            if line.startswith('PRETTY_NAME='):
                info.append(f"Distro: {line.split('=')[1].strip('\"')}")
    except:
        pass
    try:
        result = subprocess.run(["nproc"], capture_output=True, text=True, timeout=5)
        if result.stdout:
            info.append(f"CPU Cores: {result.stdout.strip()}")
    except:
        pass
    try:
        result = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5)
        if result.stdout:
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                mem_line = lines[1].split()
                if len(mem_line) > 1:
                    info.append(f"RAM: {mem_line[1]} / {mem_line[2]}")
    except:
        pass
    try:
        result = subprocess.run(["whoami"], capture_output=True, text=True, timeout=5)
        if result.stdout:
            info.append(f"User: {result.stdout.strip()}")
    except:
        pass
    
    # checklist of what pentest tools are already installed, from common tools
    tools_check = {}
    for tool in ["nmap", "nikto", "sqlmap", "gobuster", "ffuf", "curl", "wget", "nc", "netcat", "socat", "john", "hashcat", "hydra", "msfconsole", "msfvenom", "searchsploit", "git", "python3", "pip", "docker", "podman", "mysql", "psql", "redis-cli", "ldapsearch", "smbclient", "rpcclient"]:
        try:
            result = subprocess.run(["which", tool], capture_output=True, text=True, timeout=2)
            tools_check[tool] = "✓" if result.stdout.strip() else "✗"
        except:
            tools_check[tool] = "✗"
    
    tools_str = ", ".join([f"{t}:{s}" for t, s in tools_check.items()])
    info.append(f"Tools: [{tools_str}]")
    
    # Common wordlist paths, so it can check or trigger route for custom paths
    wordlists = []
    for path in ["/usr/share/wordlists/", "/usr/share/john/", "/opt/wordlists/"]:
        try:
            result = subprocess.run(["ls", "-1"], input=path, capture_output=True, text=True, timeout=2)
            if result.stdout:
                wordlists.append(path)
        except:
            pass
    if wordlists:
        info.append(f"Wordlists: {', '.join(wordlists)}")
    
    return "\n".join(info) if info else "No system info available"


def checkStdout(cmd: str) -> tuple[str, str]:
    """Check if command has output flags and modify to also output to stdout.
    This way it can stream properly on the frame, since with output flas there is no stdout to catch from return
    """
    import re
    
    output_file = ""
    modified_cmd = cmd
    
    output_flags = [
        (r'-oN\s+(\S+)', '-oN'),   # nmap normal output
        (r'-oX\s+(\S+)', '-oX'),   # nmap XML output
        (r'-oG\s+(\S+)', '-oG'),   # nmap grepable output
        (r'-oA\s+(\S+)', '-oA'),   # nmap all output
        (r'-oS\s+(\S+)', '-oS'),   # nmap script kiddie output
        (r'--output=(\S+)', '--output'),  # general --output 
        (r'--output-format=(\S+)', '--output-format'),  # gobuster flags
        # add more
    ]
    
    for pattern, flag in output_flags:
        match = re.search(pattern, cmd)
        if match:
            output_file = match.group(1)
            
            if 'nmap' in cmd.lower():
                if flag == '-oN' and output_file:
                    modified_cmd = cmd + ' -oG -'
                elif flag == '-oX' and output_file:
                    modified_cmd = cmd + ' -oX -'
                elif flag == '-oG' and output_file:
                    modified_cmd = cmd + ' -oG -'
            elif 'gobuster' in cmd.lower():
                if flag == '--output':
                    modified_cmd = cmd + ' -of txt'
            break
    
    return modified_cmd, output_file


class QuitDialog(ModalScreen):
    BINDINGS = [
        Binding("left", "nav_left", "Left"),
        Binding("right", "nav_right", "Right"),
        Binding("enter", "press_selected", "Select"),
        Binding("escape", "cancel", "Cancel"),
    ]
    CSS = f"""
    QuitDialog {{
        align: center middle;
    }}
    
    #quit_container {{
        width: 50;
        height: auto;
        background: {theme.PNL};
        padding: 3 4;
        border: none;
    }}
    
    #quit_title {{
        text-align: center;
        color: {theme.ACC};
        margin-bottom: 2;
    }}
    
    #quit_buttons {{
        align: center middle;
        height: auto;
        margin-top: 2;
    }}
    """
    
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.selected_idx = 0
    def compose(self) -> ComposeResult:
        with Vertical(id="quit_container"):
            yield Static("[bold cyan]⚠ End NEKO Session?[/bold cyan]\n\nAre you sure you want to quit?", id="quit_title")
            yield Horizontal(
                Button("Cancel", variant="primary", id="btn_no"),
                Button("Exit", variant="error", id="btn_yes"),
                id="quit_buttons"
            )
    def on_mount(self) -> None:
        self._update_button_focus()
    def _update_button_focus(self):
        buttons = list(self.query(Button))
        for i, btn in enumerate(buttons):
            if i == self.selected_idx:
                btn.focus()
            else:
                btn.remove_class("-focus")
    def action_nav_left(self):
        self.selected_idx = max(0, self.selected_idx - 1)
        self._update_button_focus()
    def action_nav_right(self):
        self.selected_idx = min(1, self.selected_idx + 1)
        self._update_button_focus()
    def action_press_selected(self):
        buttons = list(self.query(Button))
        if 0 <= self.selected_idx < len(buttons):
            buttons[self.selected_idx].press()
    def action_cancel(self):
        self.app.pop_screen()
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_yes":
            try:
                self.app_ref.sess.save()
            except Exception:
                pass
            finally:
                self.app.exit()
        else:
            self.app.pop_screen()


class InteractiveQuitDialog(QuitDialog):
    CSS = f"""
    InteractiveQuitDialog {{
        align: center middle;
    }}

    #quit_container {{
        width: 50;
        height: auto;
        background: {theme.PNL};
        padding: 3 4;
        border: none;
    }}

    #quit_title {{
        text-align: center;
        color: {theme.ACC};
        margin-bottom: 2;
    }}

    #quit_buttons {{
        align: center middle;
        height: auto;
        margin-top: 2;
    }}
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="quit_container"):
            yield Static("[bold cyan]NEKO Interactive Mode[/bold cyan]\n\nAre you sure you wanna quit? Yes / No?", id="quit_title")
            yield Horizontal(
                Button("Cancel", variant="primary", id="btn_no"),
                Button("Quit", variant="error", id="btn_yes"),
                id="quit_buttons"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_yes":
            try:
                if hasattr(self.app_ref, "cancel_interactive_tasks"):
                    self.app_ref.cancel_interactive_tasks()
                self.app_ref.sess.save()
            except Exception:
                pass
            finally:
                self.app.exit()
        else:
            self.app.pop_screen()
class RenameDialog(ModalScreen):
    BINDINGS = [
        Binding("enter", "submit_rename", "Submit"),
        Binding("escape", "cancel", "Cancel"),
    ]
    CSS = """
    RenameDialog {
        align: center middle;
    }
    #rename_container {
        width: 50;
        height: auto;
        background: #1a1a2e;
        padding: 3 4;
        border: solid #00ffff;
        border-title-style: bold;
    }
    #rename_title {
        text-align: center;
        color: #00ffff;
        margin-bottom: 2;
    }
    
    #rename_input {
        margin-top: 2;
    }
    
    Input {
        margin: 1 0;
        background: #0d0d0d;
        color: #00ffff;
        border: solid #00ffff;
    }
    
    #rename_buttons {
        align: center middle;
        height: auto;
        margin-top: 2;
    }
    
    Button {
        min-width: 18;
        margin: 0 2;
    }
    
    Button#btn_save {
        background: #003333;
        color: #00ffff;
    }
    
    Button#btn_save:hover, Button#btn_save:focus {
        background: #004444;
    }
    
    Button#btn_cancel {
        background: #333333;
        color: #aaaaaa;
    }
    
    Button#btn_cancel:hover, Button#btn_cancel:focus {
        background: #444444;
    }
    """
    
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
    def compose(self) -> ComposeResult:
        with Vertical(id="rename_container"):
            yield Static("[bold cyan]📝 Rename Session[/bold cyan]\n\nEnter new session name (alphanumeric):", id="rename_title")
            yield Input(id="rename_input", placeholder="new_session_name")
            yield Horizontal(
                Button("Cancel", variant="default", id="btn_cancel"),
                Button("Save", variant="primary", id="btn_save"),
                id="rename_buttons"
            )
    def on_mount(self) -> None:
        self.query_one("#rename_input", Input).focus()
    def action_submit_rename(self):
        input_field = self.query_one("#rename_input", Input)
        self.rename_session(input_field.value)
    def action_cancel(self):
        self.app.pop_screen()
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.action_submit_rename()
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_save":
            input_field = self.query_one("#rename_input", Input)
            self.rename_session(input_field.value)
        else:
            self.app.pop_screen()
    def rename_session(self, new_name: str):
        if not new_name:
            self.app.pop_screen()
            return
        # Checks alphanumeric, since the name must be a valid .json file name, 
        import re
        new_name = re.sub(r'[^a-zA-Z0-9_-]', '', new_name)
        
        if not new_name:
            self.app.pop_screen()
            return
        
        try:
            old_file = self.app_ref.sess.chat_file
            old_id = self.app_ref.sess.session_id
            self.app_ref.sess.session_id = new_name
            import os
            dir_path = os.path.dirname(old_file)
            new_file = os.path.join(dir_path, f"{new_name}.json")
            self.app_ref.sess.chat_file = new_file
            self.app_ref.sess.save()
            self.app_ref.title = f"Neko - {new_name}"
            self.app_ref.sub_title = f"Session: {new_name}..."
            self.app_ref.displayInfo()
            self.app_ref.upd_resp(f"[green]Session renamed to: {new_name}[/green]")
        except Exception as e:
            self.app_ref.upd_resp(f"[red]Error renaming session: {str(e)}[/red]")
        
        self.app.pop_screen()


class SudoDialog(ModalScreen):
    """Some commands might be send or might require sudo, 
and since input is not possible, triggers automatic sudo dialog to prevent UI break """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    CSS = f"""
    SudoDialog {{
        align: center middle;
    }}
    
    #sudo_container {{
        width: 60;
        height: auto;
        background: #1a1a1a;
        padding: 3 4;
        border: tall {theme.ACC};
    }}
    
    #sudo_title {{
        text-align: center;
        color: {theme.WARN};
        margin-bottom: 2;
        text-style: bold;
    }}
    
    #sudo_command {{
        text-align: center;
        color: {theme.TXT};
        margin-bottom: 2;
        background: #0d0d0d;
        padding: 1 2;
    }}
    
    #sudo_input {{
        margin-top: 2;
    }}
    
    Input {{
        margin: 1 0;
        background: #0d0d0d;
        border: solid {theme.WARN};
    }}
    
    Button {{
        margin: 1 1;
    }}
    """
    
    def __init__(self, app_ref, command, callback, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.command = command
        self.callback = callback
        self._task = None
        self._attempts = 0
        self._max_attempts = 3
    def compose(self) -> ComposeResult:
        with Vertical(id="sudo_container"):
            yield Static(f"[bold yellow]⚠ SUDO PASSWORD REQUIRED[/bold yellow]", id="sudo_title")
            yield Static(f"[cyan]{self.command}[/cyan]", id="sudo_command")
            yield Static("Enter sudo password:", id="sudo_prompt")
            yield Input(id="sudo_input", placeholder="Password", password=True)
            with Horizontal():
                yield Button("Submit", id="btn_submit", variant="primary")
                yield Button("Cancel", id="btn_cancel", variant="error")
    def on_mount(self) -> None:
        self.query_one("#sudo_input", Input).focus()

    def _set_prompt(self, text: str) -> None:
        try:
            prompt = self.query_one("#sudo_prompt", Static)
            prompt.update(text)
            prompt.refresh()
            self.refresh()
        except Exception:
            pass

    def _set_busy(self, busy: bool) -> None:
        try:
            password_input = self.query_one("#sudo_input", Input)
            password_input.disabled = busy
            password_input.refresh()
        except Exception:
            password_input = None
        try:
            submit_btn = self.query_one("#btn_submit", Button)
            cancel_btn = self.query_one("#btn_cancel", Button)
            submit_btn.disabled = busy
            cancel_btn.disabled = busy
            submit_btn.refresh()
            cancel_btn.refresh()
            self.refresh()
        except Exception:
            pass
        if not busy and password_input is not None:
            try:
                password_input.focus()
            except Exception:
                pass

    def _is_incorrect_password(self, output: str) -> bool:
        lower = str(output or "").lower()
        return any(
            marker in lower
            for marker in (
                "incorrect password attempt",
                "sorry, try again",
                "try again.",
                "no password was provided",
            )
        )

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            event.stop()
            self.action_cancel()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_submit":
            self.action_submit_password()
        elif event.button.id == "btn_cancel":
            self.action_cancel()

    def action_submit_password(self):
        password_input = self.query_one("#sudo_input", Input)
        password_value = password_input.value
        if self._task:
            return
        if not password_value:
            self._set_prompt("[red]Password required.[/red]")
            try:
                password_input.focus()
            except Exception:
                pass
            return

        self._attempts += 1
        self._set_busy(True)
        self._set_prompt(f"Checking sudo password... attempt {self._attempts}/{self._max_attempts}")

        async def run_sudo_command():
            try:
                prepared_command = self.app_ref.prepare_sudo_command(self.command) if hasattr(self.app_ref, "prepare_sudo_command") else f"sudo -S -p '' {self.command}"
                process = await asyncio.create_subprocess_shell(
                    prepared_command,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    start_new_session=True,
                    executable="/bin/bash",
                )
                if process.stdin:
                    process.stdin.write(password_value.encode() + b"\n")
                    await process.stdin.drain()
                    process.stdin.close()
                    wait_closed = getattr(process.stdin, "wait_closed", None)
                    if callable(wait_closed):
                        try:
                            await wait_closed()
                        except Exception:
                            pass
                output_chunks = []
                if process.stdout:
                    while True:
                        try:
                            chunk = await process.stdout.read(256)
                            if not chunk:
                                break
                            chunk_str = chunk.decode("utf-8", errors="replace")
                            output_chunks.append(chunk_str)
                            if hasattr(self.app_ref, "upd_out"):
                                self.app_ref.upd_out(chunk_str, terminal_mode=True, raw_terminal_chunk=True)
                            await asyncio.sleep(0)
                        except Exception:
                            break
                returncode = await process.wait()
                output = "".join(output_chunks)
                if returncode != 0 and self._is_incorrect_password(output) and self._attempts < self._max_attempts:
                    password_input.value = ""
                    self._set_busy(False)
                    self._set_prompt(f"[red]Incorrect password.[/red] Try again ({self._attempts}/{self._max_attempts}).")
                    self._task = None
                    return
                self.callback(output)
                self.app.pop_screen()
            except Exception as e:
                self.callback(f"Error: {str(e)}")
                self.app.pop_screen()
            finally:
                self._task = None

        self.refresh()
        self._task = self.run_worker(run_sudo_command(), exclusive=True, thread=False)
    
    def action_cancel(self):
        if self._task:
            try:
                self._task.cancel()
            except Exception:
                pass
        self.callback("[sudo cancelled]")
        self.app.pop_screen()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.action_submit_password()


class CommandInputDialog(ModalScreen):
    BINDINGS = [
        Binding("enter", "submit_value", "Submit"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = f"""
    CommandInputDialog {{
        align: center middle;
    }}

    #cmd_input_container {{
        width: 80;
        height: auto;
        background: #1a1a1a;
        padding: 3 4;
        border: tall {theme.OK};
    }}

    #cmd_input_title {{
        text-align: center;
        color: {theme.OK};
        margin-bottom: 1;
        text-style: bold;
    }}

    #cmd_input_command {{
        color: {theme.TXT};
        background: #0d0d0d;
        padding: 1 2;
        margin-bottom: 1;
    }}

    #cmd_input_prompt {{
        color: {theme.WARN};
        margin-bottom: 1;
    }}
    """

    def __init__(self, app_ref, command: str, prompt: str, callback, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.command = command
        self.prompt = prompt
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Vertical(id="cmd_input_container"):
            yield Static("[bold green]INPUT REQUIRED[/bold green]", id="cmd_input_title")
            yield Static(self.command, id="cmd_input_command")
            yield Static(self.prompt, id="cmd_input_prompt")
            yield Input(id="cmd_input_value", placeholder="Type response and press Enter")
            with Horizontal():
                yield Button("Submit", id="btn_submit", variant="primary")
                yield Button("Cancel", id="btn_cancel", variant="error")

    def on_mount(self) -> None:
        self.query_one("#cmd_input_value", Input).focus()

    def action_submit_value(self):
        value = self.query_one("#cmd_input_value", Input).value
        self.callback(value)
        self.app.pop_screen()

    def action_cancel(self):
        self.callback("")
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_submit":
            self.action_submit_value()
        elif event.button.id == "btn_cancel":
            self.action_cancel()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.action_submit_value()


class MsgBubble(Static):
    DEFAULT_CSS = """
    MsgBubble {
        width: 100%;
        margin: 0 0 1 0;
        padding: 0;
        background: transparent;
    }
    """

    def __init__(self, role: str, msg: str, timestamp: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.msg = msg
        self.timestamp = timestamp

    def _fmt_timestamp(self) -> str:
        raw = str(self.timestamp or "").strip()
        if not raw:
            return ""
        try:
            normalized = raw.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized).strftime("%d/%m %H:%M")
        except Exception:
            return ""

    def render(self):
        timestamp = self._fmt_timestamp()
        if self.role == "user":
            pnl = Panel(
                self.msg,
                title=f"[bold cyan]You[/bold cyan]{f' [dim]{timestamp}[/dim]' if timestamp else ''}",
                border_style=theme.ACC,
                padding=(1, 2),
            )
            return Align.right(pnl)
        elif self.role == "sys":
            pnl = Panel(
                self.msg,
                title="[bold yellow]System[/bold yellow]",
                border_style=theme.WARN,
                padding=(1, 2),
            )
            return Align.center(pnl)
        else:
            pnl = Panel(
                self.msg,
                title=f"[bold cyan]Neko[/bold cyan]{f' [dim]{timestamp}[/dim]' if timestamp else ''}",
                border_style=theme.ACC,
                padding=(1, 2),
            )
            return Align.left(pnl)


class ChatBox(ScrollableContainer):
    DEFAULT_CSS = f"""
    ChatBox {{
        border: solid {theme.ACC};
        background: {theme.PNL};
        height: 1fr;
        width: 1fr;
        margin: 0;
        padding: 1 1;
    }}
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def scroll_latest(self) -> None:
        try:
            self.scroll_end(animate=False)
        except Exception:
            pass

    def scroll_latest_after_refresh(self) -> None:
        try:
            self.call_after_refresh(self.scroll_latest)
        except Exception:
            self.scroll_latest()

    def add_msg(self, role: str, msg: str, timestamp: Optional[str] = None):
        if not self.is_attached:
            return
        bub = MsgBubble(role, msg, timestamp=timestamp)
        self.mount(bub)
        self.scroll_latest_after_refresh()


class InfoBox(ScrollableContainer):
    DEFAULT_CSS = f"""
    InfoBox {{
        width: 35;
        height: 1fr;
        padding: 1 1;
        background: {theme.PNL};
        overflow-y: auto;
        scrollbar-gutter: stable;
    }}
    
    #info_content {{
        width: 100%;
    }}
    """

    def __init__(self, ttl: str = "Info", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ttl = ttl
        self.findings = []
        self.session_info = ""
        self.content_widget = None
        self.show_findings = True

    def compose(self) -> ComposeResult:
        yield Static(id="info_content")

    def on_mount(self):
        self.content_widget = self.query_one("#info_content", Static)
        self._update_content()

    def set_cnt(self, txt: str):
        self.session_info = txt
        self._update_content()

    def set_findings(self, findings: list):
        if findings:
            for finding in findings:
                if finding not in self.findings:
                    self.findings.append(finding)
        self._update_content()
    def set_show_findings(self, show: bool):
        self.show_findings = show
        self._update_content()
    def _update_content(self):
        if not hasattr(self, 'content_widget') or not self.content_widget:
            return
        content = f"[bold cyan]{self.ttl}[/bold cyan]\n{self.session_info}\n\n"
        if self.show_findings:
            if self.findings:
                content += "[bold yellow]FINDINGS[/bold yellow]\n\n"
                for i, finding in enumerate(self.findings, 1):
                    finding_str = finding[:70] + "..." if len(finding) > 70 else finding
                    content += f"[cyan]{i}. {finding_str}[/cyan]\n"
            else:
                content += "[dim]FINDINGS[/dim]\n[dim]No findings yet[/dim]"
        self.content_widget.update(content)


class Nekointerf(Screen):
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+r", "rename_session", "Rename"),
    ]

    CSS = f"""
    Screen {{
        background: {theme.BG};
    }}

    Header {{
        background: {theme.HDR};
        color: {theme.ACC};
        height: 3;
    }}

    Footer {{
        background: {theme.HDR};
        color: {theme.ACC};
    }}

    #chat {{
        border: solid {theme.ACC};
        background: {theme.PNL};
    }}

    #inp {{
        border: solid {theme.OK};
        background: {theme.PNL};
        height: auto;
    }}

    #info {{
        width: 35;
        border: solid {theme.ACC};
        background: {theme.PNL};
        overflow-y: auto;
    }}
    """

    def __init__(self, sess: ChatSession, init_msg: Optional[str] = None):
        super().__init__()
        self.sess = sess
        self.init_msg = init_msg
        self.chat: Optional[ChatBox] = None
        self.inp: Optional[InteractiveInput] = None
        self.info: Optional[InfoBox] = None
        self._loading_task: Optional[asyncio.Task] = None
        self._loading_bubble: Optional[MsgBubble] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical():
                self.chat = ChatBox(id="chat")
                yield self.chat
                
                self.inp = InteractiveInput(
                    placeholder="Type... (Enter send, Shift+Enter newline, Ctrl+C quit)",
                    id="inp"
                )
                yield self.inp

            self.info = InfoBox("Session", id="info")
            yield self.info

        yield Footer()

    def on_mount(self):
        self.title = ">>"
        self.sub_title = f"Session: {self.sess.session_id[:8]}..."
        for msg in self.sess.messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ["user", "assistant", "system"]:
                self.chat.add_msg(role, content, msg.get("timestamp"))
        self.info.set_show_findings(False)
        self.info.set_cnt(self.displayInfo())
        self.inp.focus()

        if self.init_msg and self.inp:
            self.inp.load_text(self.init_msg)

    def displayInfo(self) -> str:
        return f"""[bold cyan]N E K O | U I [/bold cyan]

[yellow]Status:[/yellow] [green]Ready[/green]

[bold cyan]Keys[/bold cyan]
[green]Enter[/green] - Send
[green]Ctrl+C[/green] - Quit

[bold cyan]Msgs[/bold cyan]
[yellow]Count:[/yellow] {len(self.sess.messages)}"""

    def upd_resp(self, txt: str):
        if self.chat:
            self.chat.add_msg("sys", txt)

    def on_interactive_input_submitted(self, event: InteractiveInput.Submitted) -> None:
        msg = event.value.strip()
        if not msg:
            return
        if self._loading_task:
            return

        try:
            msg_timestamp = datetime.now().isoformat(timespec="seconds")
            if self.chat:
                self.chat.add_msg("user", msg, msg_timestamp)
            self.sess.add_message("user", msg, metadata={"timestamp": msg_timestamp})
            if self.info:
                self.info.set_cnt(self.displayInfo())
            self.get_resp(msg)
        except BaseException as exc:
            self._handle_interactive_exception(exc)

    def _display_interactive_error(self, text: str) -> None:
        if not self.is_attached:
            return
        if self._loading_bubble:
            self._loading_bubble.msg = text
            self._loading_bubble.refresh()
            if self.chat and self.chat.is_attached:
                self.chat.refresh()
                self.chat.scroll_latest_after_refresh()
            self._loading_bubble = None
        elif self.chat and self.chat.is_attached:
            self.chat.add_msg("sys", text)
        if self.info and self.info.is_attached:
            self.info.set_cnt(self.displayInfo())
        if self.inp and self.inp.is_attached:
            self.inp.disabled = False
            try:
                self.inp.focus()
            except Exception:
                pass

    def _log_interactive_exception(self, exc: BaseException) -> None:
        try:
            with open("/tmp/neko_interactive_error.log", "a", encoding="utf-8") as fh:
                fh.write(f"{datetime.now().isoformat()} {type(exc).__name__}: {exc}\\n")
                traceback.print_exc(file=fh)
                fh.write("\\n")
        except Exception:
            pass

    def _handle_interactive_exception(self, exc: BaseException) -> None:
        self._log_interactive_exception(exc)
        self._display_interactive_error(f"[red]Error: {exc}[/red]")
        if self._loading_task:
            try:
                self._loading_task.cancel()
            except Exception:
                pass
            self._loading_task = None

    async def _replace_loading_bubble(self, role: str, text: str, timestamp: Optional[str] = None) -> None:
        if not self.is_attached:
            self._loading_bubble = None
            return
        bubble = self._loading_bubble
        self._loading_bubble = None
        if bubble:
            try:
                await bubble.remove()
            except Exception:
                pass
        if self.chat and self.chat.is_attached:
            self.chat.add_msg(role, text, timestamp)

    def startAnim(self):
        if not self.is_attached or not self.chat or not self.chat.is_attached:
            return
        if self._loading_task:
            self._loading_task.cancel()
        bubble = MsgBubble("assistant", "Loading .", timestamp=datetime.now().isoformat(timespec="seconds"))
        self.chat.mount(bubble)
        self.chat.scroll_latest_after_refresh()
        self._loading_bubble = bubble
        if self.inp:
            self.inp.disabled = True

        async def animate():
            states = ["Loading .", "Loading ..", "Loading ...", "Loading ."]
            idx = 0
            try:
                while True:
                    bubble.msg = states[idx % len(states)]
                    bubble.refresh()
                    if self.chat and self.chat.is_attached:
                        self.chat.refresh()
                    idx += 1
                    await asyncio.sleep(0.6)
            except asyncio.CancelledError:
                return

        self._loading_task = asyncio.create_task(animate())

    async def stopAnimat(self):
        task = self._loading_task
        if not task:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        self._loading_task = None
        if self.inp and self.inp.is_attached:
            self.inp.disabled = False

    @work(exclusive=True)
    async def get_resp(self, prompt: str):
        ### Get AI response
        self.startAnim()
        try:
            history = [
                {"role": m.get("role"), "content": m.get("content", "")}
                for m in self.sess.get_messages()
                if m.get("role") in {"user", "assistant", "system"}
            ]
            resp = await asyncio.to_thread(nekoAI, prompt, conversation=history)
            await self.stopAnimat()
            final_response = str(resp)
            resp_timestamp = datetime.now().isoformat(timespec="seconds")
            self.sess.add_message("assistant", final_response, metadata={"timestamp": resp_timestamp})
            if self._loading_bubble:
                await self._replace_loading_bubble("assistant", final_response, resp_timestamp)
            elif self.chat and self.chat.is_attached:
                self.chat.add_msg("assistant", final_response, resp_timestamp)
            if self.info and self.info.is_attached:
                self.info.set_cnt(self.displayInfo())
            if self.inp and self.inp.is_attached:
                self.inp.focus()
        except asyncio.CancelledError:
            await self.stopAnimat()
            return
        except SystemExit as ex:
            await self.stopAnimat()
            self._log_interactive_exception(ex)
            await self._replace_loading_bubble("sys", f"[red]AI unavailable: {ex}[/red]")
            if self.info and self.info.is_attached:
                self.info.set_cnt(self.displayInfo())
        except KeyboardInterrupt as ex:
            await self.stopAnimat()
            self._log_interactive_exception(ex)
            await self._replace_loading_bubble("sys", "[red]Operation interrupted.[/red]")
            if self.info and self.info.is_attached:
                self.info.set_cnt(self.displayInfo())
        except Exception as ex:
            await self.stopAnimat()
            self._log_interactive_exception(ex)
            await self._replace_loading_bubble("sys", f"[red]Error: {ex}[/red]")
            if self.info and self.info.is_attached:
                self.info.set_cnt(self.displayInfo())
        except BaseException as ex:
            await self.stopAnimat()
            self._log_interactive_exception(ex)
            await self._replace_loading_bubble("sys", f"[red]Unexpected error: {ex}[/red]")
            if self.info and self.info.is_attached:
                self.info.set_cnt(self.displayInfo())

    def action_rename_session(self):
        self.app.push_screen(RenameDialog(self))

    def cancel_interactive_tasks(self):
        if self._loading_task:
            try:
                self._loading_task.cancel()
            except Exception:
                pass
            self._loading_task = None
        self._loading_bubble = None
        if self.inp and self.inp.is_attached:
            self.inp.disabled = False

    def action_quit(self):
        self.app.push_screen(InteractiveQuitDialog(self))


class OptMenu(Static):
    ### options menu with nav  
    can_focus = True
    inherit_bindings = True
    DEFAULT_CSS = f"""
    OptMenu {{
        height: auto;
        border: solid {theme.ACC};
        padding: 1 1;
        background: {theme.PNL};
    }}
    """
    
    BINDINGS = [
        Binding("r", "press_r", "Run"),
        Binding("a", "press_a", "Ask"),
        Binding("s", "press_s", "Skip"),
        Binding("m", "press_m", "Report"),
        Binding("v", "press_v", "Map"),
        Binding("q", "press_q", "Quit"),
        Binding("c", "press_c", "Commands"),
    ]

    def __init__(self, opts: List[Dict[str, str]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opts = opts
        self.update(self.makePanel(self.opts))

    def makePanel(self, opts: List[Dict[str, str]]):
        txt = Text()
        for opt in opts:
            txt.append(f"{opt['key']}", style=f"bold {theme.ACC}")
            txt.append(f" {opt['label']}  ", style=theme.ACC)
        return Panel(txt, border_style=theme.OK)

    def render(self):
        if getattr(self, "_renderable", None) is not None:
            return self._renderable
        return self.makePanel(self.opts)

    def action_press_r(self):
        screen = self.screen
        if hasattr(screen, 'handle_menu_select'):
            screen.handle_menu_select({"key": "R", "label": "Run"})
    
    def action_press_a(self):
        screen = self.screen
        if hasattr(screen, 'handle_menu_select'):
            screen.handle_menu_select({"key": "A", "label": "Ask"})
    
    def action_press_s(self):
        screen = self.screen
        if hasattr(screen, 'handle_menu_select'):
            screen.handle_menu_select({"key": "S", "label": "Skip"})
    
    def action_press_m(self):
        screen = self.screen
        if hasattr(screen, 'handle_menu_select'):
            screen.handle_menu_select({"key": "M", "label": "Report"})
    
    def action_press_v(self):
        screen = self.screen
        if hasattr(screen, 'handle_menu_select'):
            screen.handle_menu_select({"key": "V", "label": "Map"})
    
    def action_press_q(self):
        screen = self.screen
        if hasattr(screen, 'handle_menu_select'):
            screen.handle_menu_select({"key": "Q", "label": "Quit"})

    def action_press_c(self):
        screen = self.screen
        if hasattr(screen, 'handle_menu_select'):
            screen.handle_menu_select({"key": "C", "label": "Commands"})
    
    def get_sel(self):
        # Return the first option since this is a static menu
        if self.opts:
            return self.opts[0]
        return None
    
    def nxt(self):
        pass

    def prv(self):
        pass
        self.refresh()


from textual.widgets import Input as TextualInput
from textual import events


class ChatInput(TextualInput):
    DEFAULT_CSS = f"""
    ChatInput {{
        background: {theme.BG};
        color: {theme.TXT};
        border: solid {theme.ACC};
    }}
    """

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter" and event.shift and not self.disabled:
            event.stop()
            event.prevent_default()
            self.value = f"{self.value}\\n"
            return
        await super()._on_key(event)


class InteractiveInput(TextArea):
    class Submitted(Message):
        def __init__(self, sender: "InteractiveInput", value: str) -> None:
            super().__init__()
            self.sender = sender
            self.value = value

    DEFAULT_CSS = f"""
    InteractiveInput {{
        background: {theme.BG};
        color: {theme.TXT};
        border: solid {theme.ACC};
    }}
    """

    async def _on_key(self, event: events.Key) -> None:
        if self.disabled:
            await super()._on_key(event)
            return
        keys = {event.key, *getattr(event, "aliases", [])}
        if (
            "shift+enter" in keys
            or "newline" in keys
            or "ctrl+j" in keys
            or event.character == "\n"
        ):
            event.stop()
            event.prevent_default()
            self.action_newline()
            return
        if "enter" in keys or "ctrl+m" in keys or event.character == "\r":
            event.stop()
            event.prevent_default()
            self.action_submit()
            return
        await super()._on_key(event)

    def action_submit(self) -> None:
        text = self.document.text
        if not text.strip():
            return
        self.post_message(InteractiveInput.Submitted(self, text))
        self.load_text("")

    def action_newline(self) -> None:
        self.insert("\n")


