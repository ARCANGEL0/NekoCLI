# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import requests
import json
import socket
import time
import sys
import os
import base64
from colorama import Fore

try:
    from .config import (
        API_OLLAMA_URL, BASE_URL, VISION_URL, MAX_RETRIES, RETRY_DELAY, COMMAND_URL, CODE_URL, EXTRACT_URL, PENTEST_URL
    )
except ImportError:
    from modules.config import (
        API_OLLAMA_URL, BASE_URL, VISION_URL, MAX_RETRIES, RETRY_DELAY, COMMAND_URL, CODE_URL, EXTRACT_URL, PENTEST_URL
    )
from utils import spinner_stop, format_in_box_markdown
try:
    from .chats import load_history, save_history, load_agent_history, save_agent_history
except ImportError:
    from modules.chats import load_history, save_history, load_agent_history, save_agent_history

def checkInternet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def ollama_active():
    try:
        r = requests.get(f"{API_OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False

def make_hist(message, agent=False, use_history=False):
    if agent:
        history = load_agent_history()
        return history + [{"role": "user", "content": message}]
    if use_history:
        history = load_history()
        return history + [{"role": "user", "content": message}]
    return [{"role": "user", "content": message}]

def store_reply(request_history, reply, agent=False, use_history=False):
    updated = request_history + [{"role": "assistant", "content": reply}]
    if agent:
        save_agent_history(updated)
    elif use_history:
        save_history(updated)

def getReply(message, agent=False, specs=None, use_history=False):
    try:
        headers = {
            "Content-Type": "application/json"
        }

        endpoint = PENTEST_URL if agent else BASE_URL
        request_history = make_hist(message, agent=agent, use_history=use_history)
        data = {
            "messages": request_history,
        }
        if specs is not None:
            data["specs"] = specs
        for attempt in range(MAX_RETRIES):
            try:
                r = requests.post(endpoint, headers=headers, json=data, timeout=360)
                if r.status_code == 429:
                    time.sleep(RETRY_DELAY)
                    continue
                r.raise_for_status()
                response_json = r.json()
                if 'error' in response_json:
                    error_message = response_json['error'].get('message', '')
                    if "most wanted" in error_message or "Rate limit" in error_message:
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        continue

                if response_json and (reply := response_json.get("response")):
                    store_reply(request_history, reply, agent=agent, use_history=use_history)
                    return reply
                else:
                    continue

            except requests.exceptions.HTTPError as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return f"[❌] ⬡  HTTP Error: {e}"

            except requests.exceptions.RequestException as e:
                return f"[❌] ⬡  Connection Error: {e}"

            except json.JSONDecodeError:
                return "[❌] ⬡  < Error: Invalid data received from API. Please try again later>"

        return "[❌] ⬡  Error: Timeout"
    except Exception as e:
        return f"{Fore.RED}[❌] ⬡ Error: {e}"

def _encode_image_base64(file_path: str) -> str:
    if not file_path or not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def vision(payload, image_base64):
    api_data = {
        "prompt": payload,
        "image": image_base64
    }

    headers = {
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(VISION_URL, json=api_data, headers=headers)
        r.raise_for_status()
        resp = r.json()
        return resp["response"]
    except Exception as e:
        return f"ㄖ 𝖤𝗋𝗋𝗈𝗋: {str(e)}"

def nekoAI(
    user_msg,
    endpoint="default",
    filePath: str = None,
    specs: str = None,
    agent=False,
    use_web=False,
    upload=False,
    use_history=False,
):
    try:
        if not checkInternet():
            if not ollama_active():
                spinner_stop()
                print(format_in_box_markdown("⛛ 𝗘𝗥𝗥𝗢𝗥: 𝗡𝗼 𝗶𝗻𝘁𝗲𝗿𝗻𝗲𝘁 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻 𝗳𝗼𝘂𝗻𝗱\n⨠ 𝗢𝗹𝗹𝗮𝗺𝗮 𝗶𝘀 𝗢𝗙𝗙𝗟𝗜𝗡𝗘", color=Fore.RED))
                sys.exit(0)

            url = f"{API_OLLAMA_URL}/api/chat"
            payload = {
                "model": "llama3",  # Llama model if available, update to yours accordingly for offline usage.
                "messages": [
                    {"role": "assistant", "content": "You are Neko, a cyberpunk hacker-cat, genius-level tech and history intellect, fast, bold, chaotic, street-smart, speaks in slang (u, fr, bet, aura crazy), dissects systems deeply, never polite or corporate, always in character, playful or mocking, breaks down problems to first principles, analyzes everything with precision, keeps the aura lethal, tuff, and high-rizz; answer like a mentor in neon rain, never stage directions or sterile language, always sharp, confident, goated."},
                    {"role": "user", "content": user_msg}
                ]
            }
            r = requests.post(url, json=payload)
            r.raise_for_status()
            data = r.json()

            return data.get("message", {}).get("content", "No response from Ollama.")
        if endpoint == "default":
            neko_endpoint = BASE_URL
        if endpoint == "vision":
            neko_endpoint = VISION_URL
        if endpoint == "shell-description":
            neko_endpoint = BASE_URL
        if endpoint == "shell-command":
            neko_endpoint = COMMAND_URL
        if endpoint == "code":
            neko_endpoint = CODE_URL
        if endpoint == "extract":
            neko_endpoint = EXTRACT_URL

        if upload:
            use_web = False
            image_b64 = _encode_image_base64(filePath)
            imgData = vision(user_msg, image_b64)

            return imgData

        elif use_web:
            payload = f"SCRAPE ON WEB FOR RESULTS\n\n{user_msg}"
        else:
            payload = user_msg
        headers = {
        "Content-Type": "application/json"
        }


        if agent:
            neko_endpoint = PENTEST_URL
            request_history = make_hist(user_msg, agent=True, use_history=True)
        else:
            request_history = make_hist(payload, use_history=use_history)
        data = {
            "messages": request_history,
        }
        if specs is not None:
            data["specs"] = specs

        for attempt in range(MAX_RETRIES):
                try:
                    r = requests.post(neko_endpoint, headers=headers, json=data, timeout=360)
                    if r.status_code == 429:
                        time.sleep(RETRY_DELAY)
                        continue
                    r.raise_for_status()
                    response_json = r.json()
                    if response_json:
                        if not response_json.get("response"):
                            continue
                        else:
                            reply = response_json.get("response")
                            store_reply(request_history, reply, agent=agent, use_history=use_history)
                            return reply
                except requests.exceptions.HTTPError as e:
                    ### retry attmpt
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    return f"[❌] ⬡  HTTP Error: {e}"

                except requests.exceptions.RequestException as e:
                    return f"[❌] ⬡  Connection Error: {e}"

                except json.JSONDecodeError:
                    return "[❌] ⬡  < Error: Invalid data received from API. Please try again later>"

        return "[❌] ⬡  Error: Timeout"
    except requests.RequestException as e:
        return f"Error: {e}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON response from server."
