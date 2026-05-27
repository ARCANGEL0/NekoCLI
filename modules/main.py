#!/usr/bin/env python3
# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import sys
import os
import subprocess
import tempfile
import urllib.request
import re
import shutil
import importlib
import getpass
import warnings
import locale
import platform
import psutil
import json

try:
    from .config import (
        VERSION, HISTORY_FILE, MEDIA_DIR,
        IS_WINDOWS
    )
except ImportError:
    from modules.config import (
        VERSION, HISTORY_FILE, MEDIA_DIR,
        IS_WINDOWS
    )
from utils import (
    spinner_start, spinner_stop, format_in_box_markdown, clean_shell_input, glow_print
)
try:
    from .ai import nekoAI, getReply
    from .media import open_file, genVideo, editImage, genImage
    from .chats import reset_all_sessions, list_sessions, load_session, session_exists, get_session_type
    from .chat import defUI
except ImportError:
    from modules.chat import defUI
    from modules.chats import reset_all_sessions, list_sessions, load_session, session_exists, get_session_type
from colorama import Fore, Style, init
warnings.filterwarnings("ignore", category=DeprecationWarning)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

init(autoreset=True)

def ensure_pip():
    if shutil.which("pip") is None:
        print("\n\nAyo, pip was not found in PATH. Please install python-pip and ensure pip is available, so I can install sum required packages to take off, bro 🥀\n\n.")
        sys.exit(1)

def ensure_package(import_name, pip_name=None):
    pip_name = pip_name or import_name
    try:
        importlib.import_module(import_name)
    except ImportError:
        print("[⮾] MISSING MODULE!")
        print(f"⬣ Installing missing dependency 🞛⮞ {pip_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name,"--break-system-packages"])

def ensure_glow():
    if shutil.which("glow"):
        return
    print(f"\n{Fore.YELLOW}glow not installed! glow is required for Neko's outputs.{Style.RESET_ALL}")
    try:
        with open("/dev/tty", "r") as tty:
            sys.stdout.write(f"{Fore.CYAN}Install it? (y/N){Style.RESET_ALL} ")
            sys.stdout.flush()
            answer = tty.readline().strip().lower()
    except Exception:
        answer = input(f"{Fore.CYAN}Install it? (y/N){Style.RESET_ALL} ").strip().lower()
    if answer != "y":
        return
    pkg_managers = [
        (["pacman", "-S", "--noconfirm", "glow"], "pacman"),
        (["apt-get", "install", "-y", "glow"],    "apt-get"),
        (["dnf",     "install", "-y", "glow"],    "dnf"),
        (["brew",    "install", "glow"],           "brew"),
    ]
    for cmd, mgr in pkg_managers:
        if shutil.which(mgr):
            try:
                subprocess.check_call(["sudo"] + cmd)
                if shutil.which("glow"):
                    print(f"\n{Fore.GREEN}✔ glow installed!{Style.RESET_ALL}\n")
                    return
            except Exception:
                pass
    print(f"{Fore.RED}[!] Could not auto-install glow. Install manually: https://github.com/charmbracelet/glow/releases{Style.RESET_ALL}")

def version_tuple(version):
    return tuple(int(part) for part in re.findall(r"\d+", version or "0"))

def fetch_latest_pypi_version():
    try:
        with urllib.request.urlopen("https://pypi.org/pypi/nekocli/json", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            latest = payload.get("info", {}).get("version", "").strip()
            return latest or None
    except Exception:
        return None

def isCheckout():
    repo_root = ROOT_DIR
    return os.path.isdir(os.path.join(repo_root, ".git"))

def update_git():
    repo_root = ROOT_DIR
    if shutil.which("git") is None:
        print(format_in_box_markdown(
            "🞫 git is not installed, cannot update checkout",
            color=Fore.RED
        ))
        return False

    result = subprocess.run(
        ["git", "-C", repo_root, "pull", "--ff-only"],
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        print(format_in_box_markdown(
            "🞫 Git update failed",
            color=Fore.RED
        ))
        error_output = (result.stderr or result.stdout or "").strip()
        if error_output:
            print(Fore.RED + error_output)
        return False

    output = (result.stdout or "").strip()
    if output:
        print(Fore.CYAN + output)
    print(format_in_box_markdown(
        "✔ Git checkout updated successfully!",
        color=Fore.GREEN
    ))
    return True

def update_pip():
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "nekocli", "--break-system-packages"]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        print(format_in_box_markdown(
            "🞫 Pip update failed",
            color=Fore.RED
        ))
        error_output = (result.stderr or result.stdout or "").strip()
        if error_output:
            print(Fore.RED + error_output)
        return False

    print(format_in_box_markdown(
        "✔ Pip package updated successfully!",
        color=Fore.GREEN
    ))
    return True

def checkupdts():
    try:
        import socket
        socket.create_connection(("pypi.org", 443), timeout=2)
    except OSError:
        return
    latest = fetch_latest_pypi_version()
    if not latest:
        return
    if version_tuple(latest) > version_tuple(VERSION):
        print("\n" + Fore.CYAN +  "="*40)
        print(Fore.CYAN + f"🐱 Update available: {VERSION} → {latest}")
        print(Fore.GREEN + "Run: neko -u to update to the latest version")
        print("="*40 + Fore.CYAN + "\n")

def neko_update():
    latest = fetch_latest_pypi_version()
    running_in_git_checkout = isCheckout()

    if latest:
        print(format_in_box_markdown(
            f"⚡ Latest release on PyPI: v{latest}",
            color=Fore.CYAN
        ))
    else:
        print(format_in_box_markdown(
            "⚠ Could not fetch latest release from PyPI",
            color=Fore.YELLOW
        ))

    if running_in_git_checkout:
        print(Fore.CYAN + "Detected git checkout install, running git pull...")
        success = update_git()
    else:
        if latest and version_tuple(latest) <= version_tuple(VERSION):
            print(format_in_box_markdown(
                "✔ neko is already up to date",
                color=Fore.GREEN
            ))
            return

        print(Fore.CYAN + "Detected pip install, running pip upgrade...")
        success = update_pip()

    if not success:
        return

    print(Fore.CYAN + f"Current local version: v{VERSION}")
    print(Fore.GREEN + "Restart your shell/session if your old command is still cached.")

def print_help_menu():
    help_text = """
              ▒                                         ▓
             ▒███                                     ████
              ████▓▓                               ██████▓
              ███  ▓▓▓                         ▓███   ██
               ██     ▓▓▓▓                    ▓▓▓▓    ▓█
               ██       ▓▓▓▓               ▓▓▓▓       ██
                █▓         ▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓          █▓
                ██                                   ██
                ▓█▓                                  ██
                 ██                                 ▓██
                 ██                                 ██
                  █▓   █▓                           ██
                  ██   ███▓            ▒▓▓  ▓▓▒    ▓█
                  ▓█   █████▓            █████     ██
                   █▓  ███████▓          ████     ▓█▓
                   ██       ▓█▓▓░      ░▓▓  ▓▓▒   ██
                   ▓█▓                            ██
                    ██                           ██
                     █           ▒▓██▓▒          ██
                     ███          ▓███          ██
                      █▓▓▓          ▓        ▓▓▓▓
                         ▓▓▓▓             ▓▓▓▓        @𝗔𝗥𝗖𝗫𝗟⎔
                            ▓▓▓▓       █▓█▓
░███    ░██            ░██     ▓▓▓▓ ▓▓▓█      ░██████  ░██         ░██████
░████   ░██            ░██        ▓▓▓        ░██   ░██ ░██           ░██
░██░██  ░██  ░███████  ░██    ░██ ░███████  ░██        ░██           ░██
░██ ░██ ░██ ░██    ░██ ░██   ░██ ░██    ░██ ░██        ░██           ░██
░██  ░██░██ ░█████████ ░███████  ░██    ░██ ░██        ░██           ░██
░██   ░████ ░██        ░██   ░██ ░██    ░██  ░██   ░██ ░██           ░██
░██    ░███  ░███████  ░██    ░██ ░███████    ░██████  ░██████████ ░██████
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
Usage: neko [options]

Options:
  -h, --help           Show this help menu and exit
  -v, --version        Display Neko current version
  -u, --update         Update Neko to the latest version
  -n, --neofetch       Show system information
  -r, --reset          Clear saved chat history
  -i, --interactive    Interactive chat mode (chat saved at ~/neko/chat.json)
  -l, --load           Load session and optionally send prompt (usage: neko -l <session_id> [prompt])
  -ls, --list-sessions List all available sessions

 Shell & Coding Modes:
  -w, --web            Use the web search module
  -c, --code           Code mode: get code with description + raw code output
  -s, --shell          Shell mode: get shell command with description + raw command
  -so, --shell-only    Only shell command: bare command without description

Media Modes:
  -f, --file           Provide an image file for Neko to analyze along with prompt
  -g, --generate       Image generation: ask Neko to create an image
  -gv, --generate-video Video generation: generate short 8s video from prompt
  -e, --edit           Image editing: edit an image with a custom prompt

If no flags are given, runs simple AI request.
Supports input via stdin for piped commands i.e:

$ cat logs.txt | neko analyze these logs.
$ neko -wsl "find a shell command for latest openssl CVE"

"""
    spinner_stop()
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + help_text)

def get_specs():
    def cmd(command):
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL).decode().strip()
        except:
            return ""
    sys_type = platform.system()
    distro_str = "Unknown"
    if sys_type == "Linux":
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    data = dict(re.findall(r'^([^=]+)=(.*)$', f.read(), re.M))
                    distro_name = data.get("PRETTY_NAME", "Linux").strip('"')
                    base = data.get("ID_LIKE", data.get("ID", "linux")).strip('"')
                    distro_str = f"{distro_name} (Base: {base})"
        except:
            distro_str = "Linux"
    elif sys_type == "Windows":
        distro_str = f"Windows {platform.release()} {platform.win32_edition()}"
    elif sys_type == "Darwin":
        distro_str = f"macOS {platform.mac_ver()[0]}"
    de = "CLI/Headless"
    for var in ["XDG_CURRENT_DESKTOP", "DESKTOP_SESSION"]:
        if os.environ.get(var):
            de = os.environ.get(var)
            break
    if de == "CLI/Headless" and sys_type == "Linux":
        for p, name in {"plasmashell": "KDE Plasma", "gnome-session": "GNOME", "xfce4-session": "XFCE"}.items():
            if shutil.which(p) or cmd(f"pgrep {p}"):
                de = name
                break
    elif sys_type == "Windows": de = "Windows Explorer"
    elif sys_type == "Darwin": de = "Aqua"
    try:
        lang, enc = locale.getlocale()
        locale_str = f"{lang}.{enc}" if lang else "Unknown"
    except:
        locale_str = "Unknown"
    managers = ["pacman", "yay", "paru", "apt", "brew", "dnf", "choco", "winget", "pip", "npm"]
    found_mgrs = ", ".join([m for m in managers if shutil.which(m)])
    cpu_name = ""
    if sys_type == "Linux":
        cpu_name = cmd("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2") or cmd("lscpu | grep 'Model name' | cut -d: -f2")
    elif sys_type == "Windows":
        cpu_name = cmd("wmic cpu get name").split('\n')[-1]
    elif sys_type == "Darwin":
        cpu_name = cmd("sysctl -n machdep.cpu.brand_string")
    cpu_name = (cpu_name or platform.processor()).strip()
    cores = psutil.cpu_count(logical=False)
    threads = psutil.cpu_count(logical=True)
    freq_info = psutil.cpu_freq()
    freq = f"{freq_info.max}MHz" if freq_info else "N/A"
    cpu_final = f"{cpu_name} | {cores} Cores / {threads} Threads @ {freq}"
    if sys_type == "Windows":
        gpu = cmd("wmic path win32_VideoController get name").split('\n')[-1].strip()
    elif sys_type == "Darwin":
        gpu = cmd("system_profiler SPDisplaysDataType | grep 'Chipset Model' | cut -d':' -f2").strip()
    else:
        gpu = cmd("lspci | grep -i vga | cut -d ':' -f3").strip()
    gpu = gpu if gpu else "Integrated Graphics/Unknown"
    mem = psutil.virtual_memory()
    ram_str = f"{round(mem.used / (1024**3), 2)}GB / {round(mem.total / (1024**3), 2)}GB"
    disk = psutil.disk_usage('/')
    storage_str = f"{round(disk.used / (1024**3), 2)}GB / {round(disk.total / (1024**3), 2)}GB"
    lines = [
        f"OS: {sys_type}",
        f"DISTRO: {distro_str}",
        f"DESKTOP ENVIRONMENT: {de}",
        f"LOCALE: {locale_str}",
        f"SHELL: {os.environ.get('SHELL') or os.environ.get('COMSPEC', 'unknown')}",
        f"PACKAGE MANAGERS: {found_mgrs}",
        "---",
        f"CPU: {cpu_final}",
        f"GPU: {gpu}",
        f"RAM: {ram_str} (used/total)",
        f"STORAGE: {storage_str} (used/total)"
    ]

    if hasattr(psutil, "sensors_battery"):
        bat = psutil.sensors_battery()
        if bat:
            lines.append(f"Battery: {bat.percent}% {'Charging' if bat.power_plugged else 'Discharging'}")

    return "\n".join(lines)

SYS_SPECS = get_specs()

def read_tty_line(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        return None

def clear_history():
    spinner_stop()
    if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
    reset_all_sessions()
    print("\n")
    print(format_in_box_markdown("[!] History cleared! ", color=Fore.CYAN))
    print("\n")

def prompt_user_choice(prompt_str, choices):
    valid_choices = {c.lower() for c in choices}
    print(f"{Fore.YELLOW}{prompt_str}{Style.RESET_ALL}", end=" ", flush=True)
    while True:
        try:
            choice = raw_input("")
            if choice is None:
                continue
            choice = choice.strip().lower()
            if not choice:
                continue
            if choice in valid_choices:
                return choice
            else:
                print(f"Please enter one of {valid_choices}: ", end="", flush=True)
        except Exception:
            while True:
                try:
                    choice = raw_input(f"Please enter one of {valid_choices}: ")
                    choice = choice.strip().lower()
                    if choice in valid_choices:
                        return choice
                except KeyboardInterrupt:
                    continue

def prompt_filename():
    while True:
        try:
            filename = raw_input("What will be the filename ? ").strip()
            if filename:
                return filename
            else:
                print(f"{Fore.RED}Filename cannot be empty. Please try again.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Save cancelled.{Style.RESET_ALL}")
            return None

def raw_input(prompt=""):
    print(prompt, end="", flush=True)
    try:
        with open('/dev/tty', 'r') as tty_fd:
            if IS_WINDOWS:
                import msvcrt
                buf = ""
                while True:
                    ch = msvcrt.getwch()
                    if ch in ("\r", "\n"):
                        print()
                        return buf
                    elif ch == "\x08":  # backspace
                        if buf:
                            buf = buf[:-1]
                            print("\b \b", end="", flush=True)
                    elif ch == "\x03":
                        raise KeyboardInterrupt
                    else:
                        buf += ch
                        print(ch, end="", flush=True)
            else:
                import termios
                import tty
                try:
                    import readline
                except ImportError:
                    pass
                fd = tty_fd.fileno()
                try:
                    old = termios.tcgetattr(fd)
                except Exception:
                    return input()
                buf = ""
                try:
                    tty.setcbreak(fd)
                    while True:
                        ch = tty_fd.read(1)
                        if ch in ("\n", "\r"):
                            print()
                            return buf
                        elif ch in ("\x7f", "\x08"):
                            if buf:
                                buf = buf[:-1]
                                print("\b \b", end="", flush=True)
                        elif ch == "\x03":
                            raise KeyboardInterrupt
                        else:
                            buf += ch
                            print(ch, end="", flush=True)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except KeyboardInterrupt:
        raise
    except Exception:
        try:
            return input()
        except EOFError:
            return ""

def extract_raw_code(full_response):
    lines = full_response.strip().splitlines()
    cleaned_lines = []
    in_code_block = False
    for line in lines:
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                continue
            else:
                in_code_block = False
                continue
        else:
            if in_code_block or not line.strip().startswith("```"):
                cleaned_lines.append(line)
    raw_code = "\n".join(cleaned_lines).strip()
    return raw_code

def extract_raw_commands(text: str) -> str:
    match = re.search(r"```(?:bash)?\s*(.*?)```", text, re.DOTALL)
    if not match:
        return ""

    command_block = match.group(1)
    lines = []
    for line in command_block.splitlines():
        cleaned = re.sub(r"^[\s│╭╰─]*", "", line)
        lines.append(cleaned.strip())
    command = " ".join(lines)
    command = command.replace("\\ ", "")
    command = re.sub(r"\s+", " ", command)

    return command.strip()

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return (result.returncode, result.stdout, result.stderr)
    except Exception as e:
        return (1, "", str(e))

def expand_combined_short_flags(args):
    non_combined_flags = {"-so", "-gv", "-ls"}
    expanded = []
    for arg in args:
        if (
            not arg.startswith("-")
            or arg == "-"
            or arg.startswith("--")
            or arg in non_combined_flags
        ):
            expanded.append(arg)
            continue
        if len(arg) > 2 and not arg[1].isdigit():
            expanded.extend(f"-{ch}" for ch in arg[1:])
            continue
        expanded.append(arg)
    return expanded

def main():
    # required pkgs for neko here 
    REQUIRED_PACKAGES = {
        "requests": "requests",
        "colorama": "colorama",
        "psutil": "psutil",
        "requests_toolbelt": "requests-toolbelt",
        "unicodeit": "unicodeit",
    }
    ensure_pip()
    for mod, pip_name in REQUIRED_PACKAGES.items():
        ensure_package(mod, pip_name)
    ensure_glow()

    args = expand_combined_short_flags(sys.argv[1:])
    shell_mode = False
    only_command = False
    code_mode = False
    web_mode = False
    image_gen = False
    image_edit = False
    video_gen = False
    interactive_mode = False
    load_history_flag = False
    load_session_id = None
    reset_history_flag = False
    upload_mode = False
    image_prompt = ""
    video_prompt = ""
    edit_prompt = ""
    image_dir = ""
    file_path = ""
    new_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-r", "--reset"):
            reset_history_flag = True
            clear_history()
            i += 1
        elif arg in ("-u", "--update"):
            neko_update()
            sys.exit(0)
        elif arg in ("-v", "--version"):
            print("\n" + Fore.GREEN + f"   [ ⚡] v{VERSION} 😼   \n")
            sys.exit(0)
        elif arg in ("-h", "--help"):
            print_help_menu()
            sys.exit(0)
        elif arg in ("-n", "--neofetch"):
            print("\n\n")
            username = getpass.getuser()
            print(format_in_box_markdown(
                f"N E K O - F E T C H      |        [ {username} ]\n..............................\n\n{SYS_SPECS}",
                color=Fore.CYAN
            ))
            print("\n")
            sys.exit(0)
        elif arg == "-ls" or arg == "--list-sessions":
            sessions = list_sessions()
            if not sessions:
                print(f"\n{Fore.YELLOW}[!] No sessions found.{Style.RESET_ALL}\n")
                sys.exit(0)
            
            print(f"\n{Fore.CYAN}[ NEKO SESSIONS ]{Style.RESET_ALL}\n")
            print("-" * 50)
            for s in sessions:
                created = s.get('created', 'Unknown')
                if 'T' in created:
                    created = created.replace('T', ' ').split('.')[0]
                print(f"{Fore.GREEN}{s['id']}{Style.RESET_ALL} - {s['type']} :: Created on {created}")
            print("-" * 50)
            print(f"\nTotal: {len(sessions)} session(s)\n")
            sys.exit(0)
        elif arg == "-l" or arg == "--load":
            if i + 1 >= len(args) or args[i + 1].startswith('-'):
                print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ -l flag requires a session ID.{Style.RESET_ALL}\n")
                print(f"{Fore.CYAN}Usage: neko -l <session_id> [prompt]{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Run 'neko -ls' to see available sessions.{Style.RESET_ALL}\n")
                sys.exit(1)
            session_id = args[i + 1]
            i += 2
            load_session_id = session_id
            if not session_exists(session_id):
                print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ Session not found!{Style.RESET_ALL}\n")
                print(f"{Fore.YELLOW}Run 'neko -ls' to see current sessions.{Style.RESET_ALL}\n")
                sys.exit(1)
        elif arg in ("-s", "--shell"):
            shell_mode = True
            i += 1
        elif arg in ("-so", "--shell-only"):
            shell_mode = True
            only_command = True
            i += 1
        elif arg in ("-c", "--code"):
            code_mode = True
            i += 1
        elif arg in ("-w", "--web"):
            web_mode = True
            i += 1
        elif arg in ("-gv", "--generate-video"):
            video_gen = True
            i += 1
            videoprompt_parts = []
            while i < len(args) and not args[i].startswith('-'):
                videoprompt_parts.append(args[i])
                i += 1
            if not videoprompt_parts:
                print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ -gv flag requires a prompt for video generation{Style.RESET_ALL}\n\n")
                sys.exit(1)
            video_prompt = " ".join(videoprompt_parts)
        elif arg in ("-g", "--generate"):
            image_gen = True
            i += 1
            prompt_parts = []
            while i < len(args) and not args[i].startswith('-'):
                prompt_parts.append(args[i])
                i += 1
            if not prompt_parts:
                print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ -g flag requires a prompt for image generation{Style.RESET_ALL}\n\n")
                sys.exit(1)
            image_prompt = " ".join(prompt_parts)
        elif arg in ("-e", "--edit", "--edit-image"):
            image_edit = True
            if i + 1 >= len(args):
                print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ -e flag requires an image path and a prompt for image edition{Style.RESET_ALL}\n\n")
                sys.exit(1)
            image_dir = args[i + 1]
            i += 2
            prompt_parts = []
            while i < len(args) and not args[i].startswith('-'):
                prompt_parts.append(args[i])
                i += 1
            if not prompt_parts:
                print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ -e flag requires a prompt after the image path{Style.RESET_ALL}\n\n")
                sys.exit(1)
            edit_prompt = " ".join(prompt_parts)
        elif arg in ("-f", "--file"):
            upload_mode = True
            if i + 1 >= len(args) or args[i + 1].startswith('-'):
                print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ -f flag requires a file path{Style.RESET_ALL}\n\n")
                sys.exit(1)
            file_path = args[i + 1]
            i += 2
        elif arg in ("-i", "--interactive"):
            interactive_mode = True
            i += 1
        else:
            new_args.append(arg)
            i += 1

    media_modes_enabled = int(image_gen) + int(video_gen) + int(image_edit)
    if media_modes_enabled > 1:
        print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ media flags are unique, use only one of: -g, -gv, -e{Style.RESET_ALL}\n\n")
        sys.exit(1)

    non_media_mode_enabled = any([
        shell_mode,
        only_command,
        code_mode,
        web_mode,
        interactive_mode,
        upload_mode,
        load_history_flag,
    ])
    if media_modes_enabled == 1 and non_media_mode_enabled:
        print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ media flags (-g, -gv, -e) cannot be combined with other modes{Style.RESET_ALL}\n\n")
        sys.exit(1)

    args = new_args
    user_input = " ".join(args).strip()

    if not sys.stdin.isatty():
        piped_data = sys.stdin.read().strip()
        if user_input:
            user_input += "\n\n" + piped_data
        else:
            user_input = piped_data

    if reset_history_flag:
        reset_all_sessions()
        sys.exit(0)
    if not user_input and not interactive_mode and not load_session_id and not any([upload_mode, video_gen, image_gen, image_edit]):
        spinner_stop()
        print_help_menu()
        sys.exit(0)

    if load_session_id:
        session_data = load_session(load_session_id)
        if not session_data:
            print(f"\n\n{Fore.RED}[!] Error:\n⯁➤ Session not found!{Style.RESET_ALL}\n")
            print(f"{Fore.YELLOW}Run 'neko -ls' to see current sessions.{Style.RESET_ALL}\n")
            sys.exit(1)
        
        if not user_input:
            interactive_app = defUI(initial_prompt="", loaded_session=session_data)
            interactive_app.run()
            sys.exit(0)

        interactive_app = defUI(initial_prompt=user_input, loaded_session=session_data)
        interactive_app.run()
        sys.exit(0)

    if interactive_mode:
        interactive_app = defUI(initial_prompt=user_input if user_input else None)
        interactive_app.run()
        sys.exit(0)
    if upload_mode:
        spinner_start()
        if not user_input:
            print(f"{Fore.RED}[!] Error:\n⯁➤ provide a prompt when using -f <file>{Style.RESET_ALL}")
            sys.exit(1)
        try:
            result = nekoAI(user_input, endpoint="vision", upload=True, filePath=file_path)
        except FileNotFoundError:
            spinner_stop()
            print(format_in_box_markdown(f"You sure u got this right? Didn't found any file here in {file_path}", color=Fore.YELLOW) + "\n")
            sys.exit(1)
        spinner_stop()
        glow_print(result)
        print("\n")
        sys.exit(0)
    if video_gen:
        print(format_in_box_markdown("Video will be sent in 5 minutes.\n" ,color=Fore.YELLOW))
        print(f"    Prompt for video gen:\n {Fore.CYAN}       {video_prompt} \n   ")
        vidresult = genVideo(video_prompt)
        if not vidresult:
            print(f"{Fore.RED}Video generation failed. Nothing to open.{Style.RESET_ALL}")
            sys.exit(1)
        print(f"\n{Fore.CYAN}DONE [!]\nF i l e  s a v e d  a t . . . . . {MEDIA_DIR}\n\n  ⬡ Opening video now . . .\n\n")
        open_file(vidresult)
        sys.exit(1)
    if image_gen:
        print(format_in_box_markdown("Image will be sent in 5 minutes.\n",color=Fore.YELLOW))
        print(f"     Prompt for image gen:\n {Fore.CYAN}       {image_prompt}\n\n")
        image = genImage(image_prompt)
        if not image:
            print(f"{Fore.RED}Image generation failed. Nothing to open.{Style.RESET_ALL}")
            sys.exit(1)
        print(f"\n{Fore.CYAN}DONE [!]\nF i l e  s a v e d  a t . . . . . {MEDIA_DIR}\n\n  ⬡ Opening image now . . .\n\n")
        open_file(image)
        sys.exit(1)
    if image_edit:
        print(format_in_box_markdown("Image will be sent in 5 minutes.\n",color=Fore.YELLOW))
        print(f"    Prompt for image edit:\n {Fore.CYAN}       {edit_prompt}\n")
        try:
            image = editImage(image_dir, edit_prompt)
        except FileNotFoundError:
            print(format_in_box_markdown(f"You sure u got this right? Didn't found any file here in {image_dir}", color=Fore.YELLOW) + "\n")
            sys.exit(1)
        if not image:
            print(f"{Fore.RED}Image edit failed. Nothing to open.{Style.RESET_ALL}")
            sys.exit(1)
        print(f"\n{Fore.CYAN}DONE [!]\nF i l e  s a v e d  a t . . . . . {MEDIA_DIR}\n\n  ⬡ Opening image now . . .\n\n")
        open_file(image)
        sys.exit(1)

    if shell_mode:
        spinner_start()
        while True:
            user_input_str = clean_shell_input(str(user_input))
            if not only_command:
                description = nekoAI(user_input_str, endpoint="shell-description", use_history=load_history_flag)
                spinner_stop()
                glow_print(description)
            spinner_start()
            command = nekoAI(user_input_str, specs=SYS_SPECS, endpoint="shell-command", use_history=load_history_flag)
            command = command.strip()
            spinner_stop()
            print(format_in_box_markdown(command, color=Fore.GREEN) + "\n")

            choice = prompt_user_choice(f"{Fore.YELLOW}--[ [E]xecute | [R]emake | [A]bort ]--\n\n{Fore.CYAN} ⯁➤ ", {'e', 'r', 'a'})
            if choice == 'e':
                print(f"{Fore.GREEN}Executing command...{Style.RESET_ALL}")
                try:
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"{Fore.RED}Command failed with exit code {e.returncode}{Style.RESET_ALL}")
                break
            elif choice == 'r':
                continue
            else:
                print(f"\n\n{Fore.YELLOW}ㅿ E x i t i n g . . . \n\n")
                break

    elif code_mode:
        spinner_start()
        while True:
            unformattedCode = nekoAI(user_input, endpoint="code", use_web=web_mode, use_history=load_history_flag)
            raw_code = extract_raw_code(unformattedCode)
            spinner_stop()
            print(format_in_box_markdown(raw_code, color=Fore.GREEN) + "\n")

            choice = prompt_user_choice(f"{Fore.YELLOW}--[ [S]ave | [N]ew | [Q]uit ]--\n\n{Fore.CYAN} ⯁➤ ", {'s', 'n', 'q'})

            if choice == 's':
                filename = prompt_filename()
                if filename:
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(raw_code)
                        print(f"{Fore.GREEN}Code saved to '{filename}'{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Failed to save file: {e}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Save operation cancelled.{Style.RESET_ALL}")
                break

            elif choice == 'n':
                continue
            else:
                print(f"\n\n{Fore.YELLOW}ㅿ 𝙴 𝚡 𝚒 𝚝 𝚒 𝚗 g... \n\n")
                break

    else:
        spinner_start()
        while True:
            response = nekoAI(user_input, use_web=web_mode, use_history=load_history_flag)
            spinner_stop()
            glow_print(response)
            print("\n\n")
            break


if __name__ == "__main__":
    checkupdts()
    main()
