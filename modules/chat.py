#!/usr/bin/env python3

import os
import subprocess
from typing import Optional
from colorama import init

try:
    from .gui import Colors, ChatSession
    from .interface import Nekointerf
except ImportError:
    from modules.gui import Colors, ChatSession
    from modules.interface import Nekointerf

init(autoreset=True)


NEKO_BANNER = f"""{Colors.NEON_MAGENTA}
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
                               ▓▓▓▓ ▓▓▓█
                                  ▓▓▓

{Colors.RESET}"""


def clear_screen():
    subprocess.run(["cls"] if os.name == "nt" else ["clear"], shell=False, check=False)


def print_banner():
    clear_screen()
    print(NEKO_BANNER)
    print(f"{Colors.NEON_CYAN}{Colors.BOLD}AI-Powered Command Line Assistant{Colors.RESET}")
    print(Colors.NEON_CYAN + "─" * 60 + Colors.RESET)


class defUI:
    # neko gui interaface ysing textual

    def __init__(self, initial_prompt: Optional[str] = None, loaded_session: Optional[dict] = None):
        if loaded_session:
            self.session = ChatSession(session_id=loaded_session.get('session_id'))
            self.session.session_type = loaded_session.get('session_type', 'CHAT')
            self.session.messages = loaded_session.get('messages', [])
            self.session.created = loaded_session.get('created')
        else:
            self.session = ChatSession()
            self.session.session_type = "CHAT"
        self.initial_prompt = initial_prompt
        self.sys_specs = ""

    def run(self):
        try:
            from textual.app import App
            from textual.binding import Binding

            session = self.session
            screen = Nekointerf(sess=session, init_msg=self.initial_prompt)

            class nekoTUI(App):
                COMMANDS = frozenset()
                BINDINGS = [Binding("ctrl+p", "command_palette", show=False)]

                def action_command_palette(self):
                    pass

                def on_mount(self):
                    self.push_screen(screen)

            app = nekoTUI()
            app.run()
            self.exitModal(session.session_id)
        except Exception as e:
            print(f" [!] Error launching interactive interface for n e k o: {e}")
            print("::: Falling back to simple interactive mode...")
            self.bkpTUI()

    def exitModal(self, sess_id: str):
        clear_screen()
        print(f"{Colors.NEON_MAGENTA}")
        print("               ▒                                         ▓")
        print("              ▒███                                     ████")
        print("               ████▓▓                               ██████▓")
        print("               ███  ▓▓▓                         ▓███   ██")
        print("                ██     ▓▓▓▓                    ▓▓▓▓    ▓█")
        print("                ██       ▓▓▓▓               ▓▓▓▓       ██")
        print("                 █▓         ▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓          █▓")
        print("                 ██                                   ██")
        print("                 ▓█▓                                  ██")
        print("                  ██                                 ▓██")
        print("                  ██                                 ██")
        print("                   █▓   █▓                           ██")
        print("                   ██   ███▓            ▒▓▓  ▓▓▒    ▓█")
        print("                   ▓█   █████▓            █████     ██")
        print("                    █▓  ███████▓          ████     ▓█▓")
        print("                    ██       ▓█▓▓░      ░▓▓  ▓▓▒   ██")
        print("                    ▓█▓                            ██")
        print("                     ██                           ██")
        print("                      █           ▒▓██▓▒          ██")
        print("                      ███          ▓███          ██")
        print("                       █▓▓▓          ▓        ▓▓▓▓")
        print("                          ▓▓▓▓             ▓▓▓▓        @ARCXLO")
        print("                             ▓▓▓▓       █▓█▓")
        print(f"{Colors.RESET}")
        print(f"{Colors.NEON_CYAN}" + "─" * 60 + f"{Colors.RESET}")
        print()
        print(f"💾 Session saved on: {self.session.chat_file}")
        print(f"💬 To resume chat, type:")
        print()
        print(f"neko -l {sess_id}")
        print()

    def bkpTUI(self):
        # fallback to simple interactive mode if TUI fails and runs in cli mode
        print_banner()
        print(f"\n{Colors.NEON_CYAN}Session ID: {self.session.session_id}{Colors.RESET}")
        print(f"{Colors.NEON_CYAN}Chat file: {self.session.chat_file}{Colors.RESET}\n")
        if self.session.messages:
            print(f"{Colors.NEON_CYAN}{'─' * 50}{Colors.RESET}")
            print(f"{Colors.NEON_CYAN}Chat History ({len(self.session.messages)} messages):{Colors.RESET}")
            print(f"{Colors.NEON_CYAN}{'─' * 50}{Colors.RESET}\n")
            for msg in self.session.messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    print(f"{Colors.NEON_GREEN}You:{Colors.RESET} {content}")
                elif role == "assistant":
                    print(f"{Colors.NEON_CYAN}Neko:{Colors.RESET} {content}")
                elif role == "system":
                    print(f"{Colors.NEON_MAGENTA}System:{Colors.RESET} {content}")
            print(f"\n{Colors.NEON_CYAN}{'─' * 50}{Colors.RESET}\n")

        print(f"{Colors.NEON_GREEN}Chat Mode{Colors.RESET}")
        print(f"{Colors.NEON_CYAN}Type your message or 'quit' to exit{Colors.RESET}\n")

        while True:
            try:
                print(f"{Colors.NEON_MAGENTA}You:{Colors.RESET} ", end="", flush=True)
                user_input = input().strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.exitneko()
                    break

                self.submitPrompt(user_input)

            except KeyboardInterrupt:
                self.exitneko()
                break
            except EOFError:
                break

    def exitneko(self):
        print(f"\n\n{Colors.NEON_CYAN}{Colors.BOLD}[+] N E K O Session terminated.{Colors.RESET}")
        print(f"{Colors.NEON_YELLOW}To resume this session, use:{Colors.RESET}")
        print(f"{Colors.NEON_CYAN}$ neko -l {self.session.session_id}{Colors.RESET}\n")
        self.session.save()


if __name__ == "__main__":
    mode = defUI("test")
    mode.run()
