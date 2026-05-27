#!/usr/bin/env python3
# GUI Framework module for Neko CLI
# Provides terminal UI utilities for interactive mode

import os
import sys
import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# ============================================================================
# ANSI Color & Styling Utilities Stuff
# ============================================================================

class Colors:
    """Theme --------
    ------  configs"""
    CYAN = '\033[36m'
    NEON_CYAN = '\033[96m'
    NEON_GREEN = '\033[92m'
    NEON_MAGENTA = '\033[95m'
    NEON_YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    TOP_LEFT = '┌'
    TOP_RIGHT = '┐'
    BOTTOM_LEFT = '└'
    BOTTOM_RIGHT = '┘'
    HORIZONTAL = '─'
    VERTICAL = '│'
    ARROW = '⮞'
    DIAMOND = '◆'
    CIRCLE = '●'
    CHECKBOX_UNCHECKED = '☐'
    CHECKBOX_CHECKED = '☑'

def draw_box(text: str, color: str = Colors.NEON_CYAN, width: Optional[int] = None) -> str:
    lines = text.split('\n')
    if width is None:
        width = max(len(line) for line in lines) if lines else 20
    
    top = color + Colors.TOP_LEFT + Colors.HORIZONTAL * (width + 2) + Colors.TOP_RIGHT + Colors.RESET
    bottom = color + Colors.BOTTOM_LEFT + Colors.HORIZONTAL * (width + 2) + Colors.BOTTOM_RIGHT + Colors.RESET
    
    box_lines = [top]
    for line in lines:
        padding = width - len(line)
        box_lines.append(f"{color}{Colors.VERTICAL} {line:<{width}} {Colors.VERTICAL}{Colors.RESET}")
    box_lines.append(bottom)
    
    return '\n'.join(box_lines)

def draw_frame(text: str, title: str = "", color: str = Colors.NEON_CYAN) -> str:
    lines = text.split('\n')
    width = max(len(line) for line in lines) if lines else 40
    if title:
        title_text = f" {title} "
        padding = (width - len(title_text)) // 2
        frame_top = color + Colors.TOP_LEFT + Colors.HORIZONTAL * (padding) + title_text + Colors.HORIZONTAL * (width - padding - len(title_text)) + Colors.TOP_RIGHT + Colors.RESET
    else:
        frame_top = color + Colors.TOP_LEFT + Colors.HORIZONTAL * (width + 2) + Colors.TOP_RIGHT + Colors.RESET
    
    frame_bottom = color + Colors.BOTTOM_LEFT + Colors.HORIZONTAL * (width + 2) + Colors.BOTTOM_RIGHT + Colors.RESET
    
    result = [frame_top]
    for line in lines:
        result.append(f"{color}{Colors.VERTICAL}{Colors.RESET} {line:<{width}} {color}{Colors.VERTICAL}{Colors.RESET}")
    result.append(frame_bottom)
    
    return '\n'.join(result)

# ============================================================================
# Chat Session Management
# ============================================================================

class ChatSession:
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.chat_dir = os.path.expanduser("~/NEKO/sessions")
        self.chat_file = os.path.join(self.chat_dir, f"{self.session_id}.json")
        self.messages: List[Dict[str, str]] = []
        self.session_type = "CHAT"
        self.created = datetime.now().isoformat()
        self._ensure_dir()
        self._load_session()
    
    def _ensure_dir(self):
        os.makedirs(self.chat_dir, exist_ok=True)
    
    def _load_session(self):
        if os.path.exists(self.chat_file):
            try:
                with open(self.chat_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.messages = data.get('messages', [])
                    self.created = data.get('created', datetime.now().isoformat())
                    self.session_type = data.get('session_type', 'CHAT')
                    # Load findings if available
                    if 'findings' in data:
                        self.findings = data.get('findings', [])
            except (json.JSONDecodeError, IOError):
                self.messages = []
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message.update(metadata)
        self.messages.append(message)
        self.save()
    
    def save(self):
        import os
        created = self.messages[0].get('timestamp') if self.messages else datetime.now().isoformat()
        
        if os.path.exists(self.chat_file):
            try:
                with open(self.chat_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    created = existing.get('created', created)
            except:
                pass
        
        try:
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                # Save findings if they exist
                findings = getattr(self, 'findings', [])
                json.dump({
                    "session_id": self.session_id,
                    "session_type": getattr(self, 'session_type', 'CHAT'),
                    "created": created,
                    "messages": self.messages,
                    "findings": findings
                }, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"{Colors.RED}Failed to save session: {e}{Colors.RESET}")
    
    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages
    
    def clear(self):
        self.messages = []
        self.save()


# ============================================================================
# GUI Components
# ============================================================================

class MenuOption:
    def __init__(self, key: str, label: str, description: str = ""):
        self.key = key.lower()
        self.label = label
        self.description = description
    
    def render(self, color: str = Colors.NEON_CYAN) -> str:
        if self.description:
            return f"{color}[{self.key.upper()}]{Colors.RESET} {self.label:20s} - {self.description}"
        else:
            return f"{color}[{self.key.upper()}]{Colors.RESET} {self.label}"


class Menu:
        #interactive menu
    
    def __init__(self, title: str = "", options: Optional[List[MenuOption]] = None):
        self.title = title
        self.options = options or []
    
    def add_option(self, key: str, label: str, description: str = ""):
        self.options.append(MenuOption(key, label, description))
    
    def render(self) -> str:
        lines = []
        
        if self.title:
            lines.append(f"\n{Colors.NEON_CYAN}{Colors.BOLD}{self.title}{Colors.RESET}")
            lines.append(Colors.NEON_CYAN + "─" * len(self.title) + Colors.RESET)
        
        for option in self.options:
            lines.append(option.render())
        
        return '\n'.join(lines)


# ============================================================================
# Chat
# ============================================================================

class ChatDisplay:
    
    @staticmethod
    def render_message(role: str, content: str, color: Optional[str] = None) -> str:
        if role == "user":
            color = color or Colors.NEON_GREEN
            prefix = f"{Colors.NEON_GREEN}You{Colors.RESET}"
        elif role == "assistant":
            color = color or Colors.NEON_CYAN
            prefix = f"{Colors.NEON_CYAN}Assistant{Colors.RESET}"
        else:
            prefix = f"{Colors.WHITE}{role}{Colors.RESET}"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"{prefix} {Colors.DIM}[{timestamp}]{Colors.RESET}"
        
        return f"\n{header}\n{color}{content}{Colors.RESET}\n"
    
    @staticmethod
    def render_commands(commands: List[str]) -> str:
        """Render commands list from array in a single frame"""
        if not commands:
            return ""
        
        lines = []
        lines.append(f"{Colors.NEON_CYAN}{Colors.BOLD}COMMANDS TO EXECUTE{Colors.RESET}")
        lines.append(Colors.NEON_CYAN + "─" * 30 + Colors.RESET)
        
        for i, cmd in enumerate(commands, 1):
            arrow = Colors.NEON_MAGENTA + "⮞ " + Colors.RESET if i == 1 else "  "
            lines.append(f"{arrow}{Colors.NEON_YELLOW}{i}. {cmd}{Colors.RESET}")
        
        return draw_frame('\n'.join(lines[1:]), "COMMANDS", Colors.NEON_MAGENTA)


# ============================================================================
# Progress and status components for tui
# ============================================================================

class StatusBar:
    
    @staticmethod
    def render(message: str, status: str = "info") -> str:
        if status == "success":
            color = Colors.NEON_GREEN
            symbol = "✓"
        elif status == "error":
            color = Colors.RED
            symbol = "✗"
        elif status == "warning":
            color = Colors.NEON_YELLOW
            symbol = "⚠"
        else:
            color = Colors.NEON_CYAN
            symbol = "ℹ"
        
        return f"{color}{symbol} {message}{Colors.RESET}"


if __name__ == "__main__":
    print(f"\n{Colors.NEON_CYAN}{Colors.BOLD}Neko CLI - GUI Framework Test{Colors.RESET}\n")
    print(draw_box("Hello World", Colors.NEON_CYAN))
    print(draw_frame("Command 1\nCommand 2\nCommand 3", "COMMANDS", Colors.NEON_MAGENTA))
    menu = Menu("Main Menu")
    menu.add_option("r", "Run", "Execute commands")
    menu.add_option("a", "Ask", "Send follow-up question")
    menu.add_option("s", "Skip", "Skip to next command")
    menu.add_option("q", "Quit", "Exit the program")
    print(menu.render())
    print(ChatDisplay.render_message("user", "What can you do?"))
    print(ChatDisplay.render_message("assistant", "I can help u test this code by debugging like now"))
    print(StatusBar.render("Operation completed", "success"))
    print(StatusBar.render("Something went wrong", "error"))
